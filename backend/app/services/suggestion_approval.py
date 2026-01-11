"""
Shared functions for case analyzer approval workflow.
Used by both routes/moderation.py and any API-based approval endpoints.
"""

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


def norm_key_map(d: dict[str, Any]) -> dict[str, Any]:
    """Return a case- and punctuation-insensitive key map for convenient lookup."""

    def norm(s: str) -> str:
        return "".join(ch.lower() for ch in s if ch.isalnum())

    return {norm(k): v for k, v in d.items()}


def first_match(d: dict[str, Any], *keys: str) -> Any:
    """Get first matching value from dict using normalized key lookup."""
    if not d:
        return None
    km = norm_key_map(d)
    for k in keys:
        nk = "".join(ch.lower() for ch in k if ch.isalnum())
        if nk in km:
            return km[nk]
    return None


def is_new_submitted_data_format(payload: dict[str, Any]) -> bool:
    """Check if payload is in new submitted_data format (flat keys, no nested 'data')."""
    if not isinstance(payload, dict):
        return False
    return ("abstract" in payload or "courts_position" in payload or "legal_provisions" in payload) and "data" not in payload


def normalize_submitted_data(submitted_data: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Normalize the new submitted_data format for display and NocoDB submission.

    The new format has flat keys like 'jurisdiction', 'abstract', 'legal_provisions'
    directly at the top level, with a 'raw_data' JSON string containing original
    analysis results and jurisdiction info.

    Args:
        submitted_data: The submitted_data from the case_analyzer record
        item: The full database row with metadata (username, user_email, data, etc.)

    Returns:
        Normalized dict with standardized field names for display/submission
    """
    result: dict[str, Any] = {}

    # Top-level meta from item
    result["username"] = item.get("username") or submitted_data.get("username")
    result["user_email"] = item.get("user_email") or submitted_data.get("user_email")
    result["model"] = item.get("model") or submitted_data.get("model")
    result["case_citation"] = item.get("case_citation") or submitted_data.get("case_citation")

    # Parse raw_data if available for additional context
    raw_data_parsed: dict[str, Any] = {}
    if submitted_data.get("raw_data"):
        try:
            raw_str = submitted_data["raw_data"]
            raw_data_parsed = json.loads(raw_str) if isinstance(raw_str, str) else raw_str
        except Exception:
            pass

    # Get jurisdiction info from raw_data.jurisdiction if available
    jurisdiction_info = raw_data_parsed.get("jurisdiction", {}) or {}

    # Date: from created_at
    created_at = item.get("created_at")
    if created_at and hasattr(created_at, "isoformat"):
        created_at = created_at.isoformat()
    result["date"] = created_at

    # Jurisdiction (precise) - in new format, 'jurisdiction' field IS the precise jurisdiction
    # Fall back to raw_data.jurisdiction or item's analyzer.jurisdiction.result data
    result["jurisdiction"] = submitted_data.get("jurisdiction") or jurisdiction_info.get("precise_jurisdiction")

    # Additional fallback: get from analyzer column if available
    if not result["jurisdiction"]:
        analyzer_data = item.get("analyzer", {})
        if isinstance(analyzer_data, str):
            try:
                analyzer_data = json.loads(analyzer_data)
            except Exception:
                analyzer_data = {}
        if isinstance(analyzer_data, dict):
            jur_step = analyzer_data.get("jurisdiction", {})
            if isinstance(jur_step, dict):
                jur_result = jur_step.get("result", {})
                if isinstance(jur_result, dict):
                    result["jurisdiction"] = jur_result.get("precise_jurisdiction")

    # Jurisdiction Type (law family) - from raw_data.jurisdiction
    jurisdiction_type = jurisdiction_info.get("legal_system_type")
    result["jurisdiction_type"] = jurisdiction_type

    # Sections - prefer direct field, fall back to raw_data.analysisResults
    col_sections = submitted_data.get("choice_of_law_sections")
    if not col_sections:
        analysis_results = raw_data_parsed.get("analysisResults", {}) or {}
        col_extraction = analysis_results.get("col_extraction", {}) or {}
        col_sections = col_extraction.get("col_section") or col_extraction.get("col_sections")
        if isinstance(col_sections, list) and col_sections:
            col_sections = col_sections[-1] if col_sections else None
    result["choice_of_law_sections"] = col_sections

    # Theme - prefer direct field, fall back to raw_data.analysisResults
    theme_val = submitted_data.get("themes")
    if not theme_val:
        analysis_results = raw_data_parsed.get("analysisResults", {}) or {}
        theme_classification = analysis_results.get("theme_classification", {}) or {}
        theme_val = (
            theme_classification.get("classification")
            or theme_classification.get("theme")
            or theme_classification.get("themes")
        )
        if isinstance(theme_val, list) and theme_val:
            theme_val = theme_val[-1]
    if isinstance(theme_val, list | dict):
        try:
            theme_val = json.dumps(theme_val, ensure_ascii=False)
        except Exception:
            theme_val = str(theme_val)
    result["theme"] = theme_val

    # Direct fields from new format
    result["abstract"] = submitted_data.get("abstract")
    result["relevant_facts"] = submitted_data.get("relevant_facts")
    result["pil_provisions"] = submitted_data.get("legal_provisions")  # New format uses 'legal_provisions'
    result["choice_of_law_issue"] = submitted_data.get("choice_of_law_issue")

    # Court's Position - check if common law for assembly
    is_common_law = jurisdiction_type and "common" in jurisdiction_type.lower() if jurisdiction_type else False

    if is_common_law:
        parts: list[str] = []
        cp = submitted_data.get("courts_position")
        if cp:
            parts.append(str(cp).strip())
        ob = submitted_data.get("obiter_dicta")
        if ob:
            parts.append(f"Obiter Dicta: {str(ob).strip()}")
        ds = submitted_data.get("dissenting_opinions")
        if ds:
            parts.append(f"Dissenting Opinions: {str(ds).strip()}")
        result["courts_position"] = "\n\n".join([p for p in parts if p]) or None
    else:
        result["courts_position"] = submitted_data.get("courts_position")

    # Preserve raw data
    result["raw_data"] = submitted_data.get("raw_data")

    # pdf_url and file_name from the data column (not submitted_data)
    # These are stored in the original data column during upload
    legacy_data: dict[str, Any] = {}
    item_data = item.get("data")
    if isinstance(item_data, dict):
        legacy_data = item_data
    elif isinstance(item_data, str):
        try:
            parsed = json.loads(item_data)
            if isinstance(parsed, dict):
                legacy_data = parsed
        except Exception:
            pass
    result["pdf_url"] = legacy_data.get("pdf_url") or submitted_data.get("pdf_url")
    result["file_name"] = legacy_data.get("file_name") or submitted_data.get("file_name")

    return result


def normalize_case_analyzer_payload(raw: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    """Flatten and normalize the analyzer payload for read-only display.

    Supports two formats:
    1. NEW format (submitted_data): flat keys - delegates to normalize_submitted_data
    2. OLD format (legacy data): nested 'data' object with '_edited' suffix fields

    Rules for old format:
    - Prefer *_edited fields.
    - Jurisdiction -> precise_jurisdiction(_edited)
    - Jurisdiction Type -> jurisdiction(_edited)
    - Choice of Law Section(s) -> last item of col_section(_edited)
    - Theme -> last item of classification(_edited)
    - Court's Position ->
        * Civil law: courts_position_edited
        * Common law: concat of courts_position_edited, obiter_dicta_edited, dissenting_opinions_edited
    """
    if not isinstance(raw, dict):
        raw = {}

    # Detect and delegate to new format handler
    if is_new_submitted_data_format(raw):
        return normalize_submitted_data(raw, item)

    # OLD FORMAT: nested 'data' object with '_edited' suffix fields
    result: dict[str, Any] = {}

    # Top-level meta from item (always available)
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
        return first_match(data_obj, *keys)

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
    if isinstance(theme_val, list | dict):
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

    # Preserve pdf_url and file_name for approval workflow
    result["pdf_url"] = data_obj.get("pdf_url") or raw.get("pdf_url")
    result["file_name"] = data_obj.get("file_name") or raw.get("file_name")

    return result


def resolve_jurisdiction_ids(
    nocodb_service: NocoDBService,
    court_decision_data: dict[str, Any],
) -> list[int]:
    """Resolve jurisdiction string to NocoDB jurisdiction IDs."""
    jurisdiction_ids: list[int] = []
    if court_decision_data.get("jurisdiction"):
        try:
            jurisdiction_value = court_decision_data.get("jurisdiction")
            if jurisdiction_value is not None:
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


def prepare_nocodb_data(
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


def link_jurisdictions(
    nocodb_service: NocoDBService,
    jurisdiction_ids: list[int],
    merged_id: int | str,
) -> None:
    """Link jurisdiction IDs to the court decision record."""
    if jurisdiction_ids:
        try:
            nocodb_service.link_records(
                table="mdmls7kc3a3w1vu",
                record_id=int(merged_id),
                field_id="c2rumo81p8xw0pg",
                linked_record_ids=jurisdiction_ids,
            )
        except Exception as e:
            logger.error("Failed to link jurisdictions: %s", str(e))
            # Continue - record is already created


def handle_pdf_upload(
    nocodb_service: NocoDBService,
    pdf_url: str | None,
    file_name: str | None,
    merged_id: int | str,
) -> None:
    """Download PDF from Azure and upload to NocoDB if pdf_url is present."""
    if not pdf_url or not isinstance(pdf_url, str) or not pdf_url.strip():
        logger.warning("No pdf_url found for record %s - skipping PDF upload", merged_id)
        return

    try:
        pdf_data = download_blob_with_managed_identity(pdf_url)

        parsed_url = urlparse(pdf_url)
        filename = file_name or os.path.basename(parsed_url.path)
        if not filename:
            filename = "document.pdf"
        elif not filename.endswith(".pdf"):
            filename = f"{filename}.pdf"

        nocodb_service.upload_file(
            table="mdmls7kc3a3w1vu",
            record_id=int(merged_id),
            field_id="ciw1ko4kixrlep0",
            file_data=pdf_data,
            filename=filename,
            mime_type="application/pdf",
            field_name="Official Source (PDF)",
        )
    except Exception as e:
        logger.error("Failed to download/upload PDF from %s: %s", pdf_url, str(e))
        # Continue - record is already created


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


async def approve_case_analyzer(
    suggestion_service: SuggestionService,
    writer: MainDBWriter,
    table: str,
    suggestion_id: int,
    original_payload: dict[str, Any],
    item: dict[str, Any],
    moderator_email: str,
) -> None:
    """Handle approval of case analyzer submissions via NocoDB API.

    Uses submitted_data column if available (new records), otherwise falls back
    to normalizing from the legacy data column (backwards compatibility).
    """
    submitted_data = item.get("submitted_data")
    if submitted_data and is_new_submitted_data_format(submitted_data):
        normalized = normalize_submitted_data(submitted_data, item)
    else:
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

    jurisdiction_ids = resolve_jurisdiction_ids(nocodb_service, court_decision_data)
    nocodb_data = prepare_nocodb_data(writer, court_decision_data)
    created_record = nocodb_service.create_row("mdmls7kc3a3w1vu", nocodb_data)
    merged_id = created_record.get("id") or created_record.get("Id")

    if not merged_id:
        logger.error("Failed to get record ID from NocoDB response: %s", created_record)
        raise HTTPException(
            status_code=500,
            detail="Failed to create record in NocoDB",
        )

    link_jurisdictions(nocodb_service, jurisdiction_ids, merged_id)

    # Get pdf_url from the data column (legacy data), not submitted_data
    legacy_data = item.get("data", {})
    if isinstance(legacy_data, str):
        try:
            legacy_data = json.loads(legacy_data)
        except Exception:
            legacy_data = {}
    if not isinstance(legacy_data, dict):
        legacy_data = {}

    pdf_url = legacy_data.get("pdf_url") or original_payload.get("pdf_url")
    file_name = legacy_data.get("file_name") or original_payload.get("file_name")

    handle_pdf_upload(nocodb_service, pdf_url, file_name, merged_id)

    suggestion_service.mark_status(
        table,
        suggestion_id,
        "approved",
        moderator_email,
        note="Automatically inserted into Court_Decisions table via NocoDB API",
        merged_id=int(merged_id),
    )
