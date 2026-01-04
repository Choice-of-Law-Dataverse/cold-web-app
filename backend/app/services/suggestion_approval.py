import json
import logging
import os
from typing import Any
from urllib.parse import urlparse

from fastapi import HTTPException

from app.config import config
from app.services.azure_storage import download_blob_with_managed_identity
from app.services.moderation_writer import MainDBWriter
from app.services.nocodb import NocoDBService
from app.services.suggestions import SuggestionService

logger = logging.getLogger(__name__)


def _norm_key_map(d: dict[str, Any]) -> dict[str, Any]:
    """Return a case- and punctuation-insensitive key map for convenient lookup."""

    def norm(s: str) -> str:
        return "".join(ch.lower() for ch in s if ch.isalnum())

    return {norm(k): v for k, v in d.items()}


def _first(d: dict[str, Any], *keys: str) -> Any:
    if not d:
        return None
    km = _norm_key_map(d)
    for k in keys:
        nk = "".join(ch.lower() for ch in k if ch.isalnum())
        if nk in km:
            return km[nk]
    return None


def normalize_case_analyzer_payload(raw: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Flatten and normalize the analyzer payload for read-only display.
    Rules:
    - Prefer *_edited fields.
    - Jurisdiction -> precise_jurisdiction(_edited)
    - Jurisdiction Type -> jurisdiction(_edited)
    - Choice of Law Section(s) -> last item of col_section(_edited)
    - Theme -> last item of classification(_edited)
    - Court's Position ->
        * Civil law: courts_position_edited
        * Common law: concat of courts_position_edited, obiter_dicta_edited, dissenting_opinions_edited
    """
    result: dict[str, Any] = {}
    if not isinstance(raw, dict):
        raw = {}

    # Top-level meta
    result["username"] = item.get("username") or raw.get("username")
    result["user_email"] = item.get("user_email") or raw.get("user_email")
    result["model"] = item.get("model") or raw.get("model")
    result["case_citation"] = item.get("case_citation") or raw.get("case_citation")

    # Load inner data
    data_obj: Any = raw.get("data") if "data" in raw else raw
    if isinstance(data_obj, str):
        try:
            data_obj = json.loads(data_obj)
        except Exception:
            pass
    if not isinstance(data_obj, dict):
        data_obj = {}

    # Helpers
    def pref(*names: str) -> Any:
        edited_first: list[str] = []
        plain: list[str] = []
        for n in names:
            (edited_first if n.endswith("_edited") else plain).append(n)
        keys: list[str] = []
        keys.extend(edited_first)
        keys.extend(plain)
        return _first(data_obj, *keys)

    def last_item(val: Any) -> Any:
        if isinstance(val, list):
            # choose last non-empty item
            for x in reversed(val):
                if x is None:
                    continue
                s = str(x).strip()
                if s:
                    return x
            return None
        return val

    # Date: prefer decision date; fallback to row created_at
    decision_date = pref(
        "decision_date_edited",
        "decision_date",
        "date_of_judgment_edited",
        "date_of_judgment",
        "date_edited",
        "date",
    )
    created_at = item.get("created_at")
    if created_at and hasattr(created_at, "isoformat"):
        created_at = created_at.isoformat()
    result["date"] = decision_date or created_at

    # Jurisdiction (precise)
    result["jurisdiction"] = pref("precise_jurisdiction_edited", "precise_jurisdiction")

    # Jurisdiction Type (law family)
    jurisdiction_type = pref("jurisdiction_edited", "jurisdiction")
    result["jurisdiction_type"] = jurisdiction_type

    # Sections and themes
    result["choice_of_law_sections"] = last_item(pref("col_section_edited", "col_section"))
    theme_val = last_item(pref("classification_edited", "classification"))
    # If list item is dict or list, stringify
    if isinstance(theme_val, (list, dict)):
        try:
            theme_val = json.dumps(theme_val, ensure_ascii=False)
        except Exception:
            theme_val = str(theme_val)
    result["theme"] = theme_val

    # Abstract and facts
    result["abstract"] = pref("abstract_edited", "abstract", "summary_edited", "summary")
    result["relevant_facts"] = pref("relevant_facts_edited", "relevant_facts", "facts_edited", "facts")

    # PIL/CoL
    result["pil_provisions"] = pref("pil_provisions_edited", "pil_provisions")
    result["choice_of_law_issue"] = pref(
        "choice_of_law_issue_edited",
        "choice_of_law_issue",
        "col_issue_edited",
        "col_issue",
    )

    # Determine common vs civil law for Court's Position assembly
    is_common_law_raw = pref("is_common_law_edited", "is_common_law", "common_law_edited", "common_law")
    is_common_law: bool | None = None
    if isinstance(is_common_law_raw, bool):
        is_common_law = is_common_law_raw
    elif isinstance(is_common_law_raw, str):
        is_common_law = is_common_law_raw.strip().lower() in {
            "true",
            "1",
            "yes",
            "y",
            "common",
            "common law",
        }
    # If still unknown, infer from jurisdiction_type string
    if is_common_law is None and isinstance(jurisdiction_type, str):
        jt = jurisdiction_type.strip().lower()
        if "common" in jt:
            is_common_law = True
        elif "civil" in jt:
            is_common_law = False

    # Court's Position assembly per rules
    if is_common_law is True:
        parts: list[str] = []
        cp = pref("courts_position_edited", "courts_position")
        if cp:
            parts.append(str(cp).strip())
        ob = pref("obiter_dicta_edited", "obiter_dicta")
        if ob:
            parts.append(f"Obiter Dicta: {str(ob).strip()}")
        ds = pref("dissenting_opinions_edited", "dissenting_opinions")
        if ds:
            parts.append(f"Dissenting Opinions: {str(ds).strip()}")
        result["courts_position"] = "\n\n".join([p for p in parts if p]) or None
    else:
        # Civil law (or unknown treated as civil per instruction): prefer courts_position_edited
        result["courts_position"] = pref("courts_position_edited", "courts_position")

    # Preserve raw analyzer output for copy/paste
    try:
        result["raw_data"] = json.dumps(data_obj, ensure_ascii=False, indent=2)
    except Exception:
        result["raw_data"] = str(data_obj)

    return result


def _resolve_jurisdiction_ids(
    nocodb_service: NocoDBService,
    court_decision_data: dict[str, Any],
) -> list[int]:
    """Resolve jurisdiction string to NocoDB jurisdiction IDs."""
    jurisdiction_ids: list[int] = []
    if court_decision_data.get("jurisdiction"):
        try:
            jurisdiction_value = court_decision_data.get("jurisdiction")
            if jurisdiction_value is not None:
                logger.info("Resolving jurisdiction '%s' before creating record", jurisdiction_value)
                jurisdiction_ids = nocodb_service.list_jurisdictions(str(jurisdiction_value))

            if not jurisdiction_ids:
                logger.warning(
                    "Could not resolve jurisdiction '%s' - record will be created without jurisdiction link",
                    jurisdiction_value,
                )
        except Exception as e:
            logger.warning(
                "Failed to resolve jurisdiction '%s': %s - record will be created without jurisdiction link",
                court_decision_data.get("jurisdiction"),
                str(e),
            )
    return jurisdiction_ids


def _prepare_nocodb_data(
    writer: MainDBWriter,
    court_decision_data: dict[str, Any],
) -> dict[str, Any]:
    """Map snake_case keys to NocoDB column names (PascalCase)."""
    column_mapping = writer.COLUMN_MAPPINGS.get("Court_Decisions", {})
    nocodb_data: dict[str, Any] = {}

    for key, value in court_decision_data.items():
        if key == "jurisdiction":
            # Skip jurisdiction - handled separately via link_records
            continue
        nocodb_column = column_mapping.get(key, key)
        if value is not None and value != "":
            nocodb_data[nocodb_column] = value

    return nocodb_data


def _link_jurisdictions(
    nocodb_service: NocoDBService,
    jurisdiction_ids: list[int],
    merged_id: int | str,
) -> None:
    """Link jurisdiction IDs to the court decision record."""
    if jurisdiction_ids:
        try:
            logger.info("Linking jurisdiction IDs %s to record %s", jurisdiction_ids, merged_id)
            nocodb_service.link_records(
                table="mdmls7kc3a3w1vu",
                record_id=int(merged_id),
                field_id="c2rumo81p8xw0pg",
                linked_record_ids=jurisdiction_ids,
            )
            logger.info("Successfully linked jurisdictions to record")
        except Exception as e:
            logger.error("Failed to link jurisdictions: %s", str(e))
            # Continue - record is already created


def _handle_pdf_upload(
    nocodb_service: NocoDBService,
    original_payload: dict[str, Any],
    merged_id: int | str,
) -> None:
    """Download PDF from Azure and upload to NocoDB if pdf_url is present."""
    pdf_url = original_payload.get("pdf_url")
    if not pdf_url or not isinstance(pdf_url, str) or not pdf_url.strip():
        return

    try:
        logger.info("Downloading PDF from Azure: %s", pdf_url)
        pdf_data = download_blob_with_managed_identity(pdf_url)

        parsed_url = urlparse(pdf_url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = "document.pdf"
        elif not filename.endswith(".pdf"):
            filename = f"{filename}.pdf"

        logger.info("Uploading PDF to NocoDB for record %s", merged_id)
        nocodb_service.upload_file(
            table="mdmls7kc3a3w1vu",
            record_id=int(merged_id),
            field_id="ciw1ko4kixrlep0",
            file_data=pdf_data,
            filename=filename,
            mime_type="application/pdf",
            field_name="Official Source (PDF)",
        )
        logger.info("Successfully uploaded PDF to NocoDB")
    except Exception as e:
        logger.error("Failed to download/upload PDF from %s: %s", pdf_url, str(e))
        # Continue - record is already created


async def approve_case_analyzer(
    suggestion_service: SuggestionService,
    writer: MainDBWriter,
    table: str,
    suggestion_id: int,
    original_payload: dict[str, Any],
    item: dict[str, Any],
    moderator_email: str,
) -> None:
    """Handle approval of case analyzer submissions via NocoDB API."""
    normalized = normalize_case_analyzer_payload(original_payload, item)
    suggestion_service.update_payload(table, suggestion_id, {"normalized": normalized})

    court_decision_data = writer.prepare_case_analyzer_for_court_decisions(normalized)

    if not config.NOCODB_BASE_URL or not config.NOCODB_API_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="NocoDB API credentials not configured",
        )
    nocodb_service = NocoDBService(
        base_url=config.NOCODB_BASE_URL,
        api_token=config.NOCODB_API_TOKEN,
    )

    jurisdiction_ids = _resolve_jurisdiction_ids(nocodb_service, court_decision_data)
    nocodb_data = _prepare_nocodb_data(writer, court_decision_data)
    created_record = nocodb_service.create_row("mdmls7kc3a3w1vu", nocodb_data)
    merged_id = created_record.get("id") or created_record.get("Id")

    if not merged_id:
        logger.error("Failed to get record ID from NocoDB response: %s", created_record)
        raise HTTPException(
            status_code=500,
            detail="Failed to create record in NocoDB",
        )

    _link_jurisdictions(nocodb_service, jurisdiction_ids, merged_id)
    _handle_pdf_upload(nocodb_service, original_payload, merged_id)

    suggestion_service.mark_status(
        table,
        suggestion_id,
        "approved",
        moderator_email,
        note="Automatically inserted into Court_Decisions table via NocoDB API",
        merged_id=int(merged_id),
    )


def get_target_table(category: str) -> str | None:
    """Map category to target database table name."""
    table_map = {
        "court-decisions": "Court_Decisions",
        "domestic-instruments": "Domestic_Instruments",
        "regional-instruments": "Regional_Instruments",
        "international-instruments": "International_Instruments",
        "literature": "Literature",
    }
    return table_map.get(category)


def normalize_domestic_instruments(updated_fields: dict[str, Any]) -> None:
    """Auto-derive year text for Domestic Instruments if missing."""
    if (not updated_fields.get("date_year_of_entry_into_force")) and updated_fields.get("entry_into_force"):
        try:
            year = str(updated_fields["entry_into_force"])[:4]
            updated_fields["date_year_of_entry_into_force"] = year
        except Exception:
            pass


def link_jurisdictions_for_default_categories(
    writer: MainDBWriter,
    target_table: str,
    merged_id: int,
    payload_for_writer: dict[str, Any],
) -> None:
    """Link jurisdictions for default categories."""
    for key in ("jurisdiction", "jurisdiction_link"):
        if key in payload_for_writer and payload_for_writer.get(key):
            try:
                writer.link_jurisdictions(target_table, merged_id, payload_for_writer.get(key))
            except Exception as e:
                logger.warning(
                    "Failed to link jurisdiction '%s' for %s record %s: %s",
                    payload_for_writer.get(key),
                    target_table,
                    merged_id,
                    str(e),
                )
