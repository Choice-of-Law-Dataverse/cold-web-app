from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, Any, Dict, List, Tuple, Type
import html
from datetime import date
import json

from app.config import config
from app.services.suggestions import SuggestionService
from app.services.moderation_writer import MainDBWriter
from app.schemas.suggestions import (
    CourtDecisionSuggestion,
    DomesticInstrumentSuggestion,
    RegionalInstrumentSuggestion,
    InternationalInstrumentSuggestion,
    LiteratureSuggestion,
    CaseAnalyzerSuggestion,
)

router = APIRouter(prefix="/moderation", tags=["Moderation"], include_in_schema=False)

service: SuggestionService | None = None
writer: MainDBWriter | None = None


def _is_logged_in(request: Request) -> bool:
    return bool(request.session.get("moderator"))


def _category_schema(category: str):
    mapping: Dict[str, Any] = {
        "court-decisions": CourtDecisionSuggestion,
        "domestic-instruments": DomesticInstrumentSuggestion,
        "regional-instruments": RegionalInstrumentSuggestion,
        "international-instruments": InternationalInstrumentSuggestion,
        "literature": LiteratureSuggestion,
        # New: Case Analyzer
        "case-analyzer": CaseAnalyzerSuggestion,
    }
    return mapping.get(category)


def _python_type(t: Any) -> Any:
    """Resolve Optional/Union and containers to their base python types for widget selection."""
    try:
        from typing import get_origin, get_args, Union

        origin = get_origin(t)
        if origin is None:
            return t
        if origin in (list, tuple, dict):
            return origin
        if origin is Union:
            args = [a for a in get_args(t) if a is not type(None)]  # noqa: E721
            return args[0] if args else Any
        return t
    except Exception:
        return t


def _render_input(name: str, value: Any, field_info) -> str:
    """Return HTML input element for a schema field."""
    annotation = getattr(field_info, "annotation", str)
    base_t = _python_type(annotation)
    label = field_info.description or name.replace("_", " ").title()
    safe_val = "" if value is None else str(value)
    if isinstance(value, list):
        safe_val = ", ".join(str(v) for v in value)
    safe_val = html.escape(safe_val)

    # Choose widget by type
    if base_t is bool:
        checked = " checked" if (value is True or (isinstance(value, str) and value.lower() in {"true", "1", "yes"})) else ""
        return f"<label style='display:block;margin:6px 0'><input type='checkbox' name='{html.escape(name)}' value='true'{checked}/> {html.escape(label)}</label>"
    if base_t in (date,):
        return (
            f"<label style='display:block;margin:6px 0'>{html.escape(label)} "
            f"<input type='date' name='{html.escape(name)}' value='{safe_val}'/></label>"
        )
    if base_t in (int, float):
        return (
            f"<label style='display:block;margin:6px 0'>{html.escape(label)} "
            f"<input type='number' step='any' name='{html.escape(name)}' value='{safe_val}'/></label>"
        )
    # For lists, accept comma-separated text
    if base_t in (list, tuple):
        return (
            f"<label style='display:block;margin:6px 0'>{html.escape(label)} "
            f"<input type='text' name='{html.escape(name)}' value='{safe_val}' placeholder='Comma-separated values'/></label>"
        )
    # Default to text input; use textarea for likely long text fields
    longish = any(k in name for k in ["abstract", "quote", "excerpt", "notes", "relevant", "original_text", "english_translation", "raw_data", "legal_provisions"]) \
        or (isinstance(value, str) and len(value) > 180)
    if longish:
        return (
            f"<label style='display:block;margin:6px 0'>{html.escape(label)}<br/>"
            f"<textarea name='{html.escape(name)}' rows='4' style='width:100%'>{safe_val}</textarea></label>"
        )
    return (
        f"<label style='display:block;margin:6px 0'>{html.escape(label)} "
        f"<input type='text' name='{html.escape(name)}' value='{safe_val}'/></label>"
    )


def _norm_key_map(d: Dict[str, Any]) -> Dict[str, Any]:
    """Return a case- and punctuation-insensitive key map for convenient lookup."""
    def norm(s: str) -> str:
        return "".join(ch.lower() for ch in s if ch.isalnum())
    return {norm(k): v for k, v in d.items()}


def _first(d: Dict[str, Any], *keys: str) -> Any:
    if not d:
        return None
    km = _norm_key_map(d)
    for k in keys:
        nk = "".join(ch.lower() for ch in k if ch.isalnum())
        if nk in km:
            return km[nk]
    return None


def _normalize_case_analyzer_payload(raw: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
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
    result: Dict[str, Any] = {}
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
        edited_first: List[str] = []
        plain: List[str] = []
        for n in names:
            (edited_first if n.endswith("_edited") else plain).append(n)
        keys: List[str] = []
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
    decision_date = pref("decision_date_edited", "decision_date", "date_of_judgment_edited", "date_of_judgment", "date_edited", "date")
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
    result["choice_of_law_issue"] = pref("choice_of_law_issue_edited", "choice_of_law_issue", "col_issue_edited", "col_issue")

    # Determine common vs civil law for Court's Position assembly
    is_common_law_raw = pref("is_common_law_edited", "is_common_law", "common_law_edited", "common_law")
    is_common_law: Optional[bool] = None
    if isinstance(is_common_law_raw, bool):
        is_common_law = is_common_law_raw
    elif isinstance(is_common_law_raw, str):
        is_common_law = is_common_law_raw.strip().lower() in {"true", "1", "yes", "y", "common", "common law"}
    # If still unknown, infer from jurisdiction_type string
    if is_common_law is None and isinstance(jurisdiction_type, str):
        jt = jurisdiction_type.strip().lower()
        if "common" in jt:
            is_common_law = True
        elif "civil" in jt:
            is_common_law = False

    # Court's Position assembly per rules
    if is_common_law is True:
        parts: List[str] = []
        cp = pref("courts_position_edited")  # exact key as requested
        if cp:
            parts.append(str(cp).strip())
        ob = pref("obiter_dicta_edited")
        if ob:
            parts.append(f"Obiter Dicta: {str(ob).strip()}")
        ds = pref("dissenting_opinions_edited")
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


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if _is_logged_in(request):
        return RedirectResponse(url="/moderation", status_code=302)
    return HTMLResponse(
        """
        <html><head><title>Moderation Login</title></head>
        <body>
          <h2>Moderation Login</h2>
          <form method="post" action="/moderation/login">
            <label>Username <input name="username"/></label><br/>
            <label>Password <input name="password" type="password"/></label><br/>
            <button type="submit">Login</button>
          </form>
        </body></html>
        """
    )


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not config.MODERATION_USERNAME or not config.MODERATION_PASSWORD:
        raise HTTPException(status_code=500, detail="Moderation credentials not configured")
    if username == config.MODERATION_USERNAME and password == config.MODERATION_PASSWORD:
        request.session["moderator"] = username
        return RedirectResponse(url="/moderation", status_code=302)
    return HTMLResponse("Invalid credentials", status_code=401)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/moderation/login", status_code=302)


@router.get("/")
def index(request: Request):
    if not _is_logged_in(request):
        return RedirectResponse(url="/moderation/login", status_code=302)
    # simple landing listing links per table
    return HTMLResponse(
        """
        <html><head><title>Moderation</title></head>
        <body>
          <h2>Suggestions Moderation</h2>
          <ul>
            <li><a href="/moderation/court-decisions">Court Decisions</a></li>
            <li><a href="/moderation/domestic-instruments">Domestic Instruments</a></li>
            <li><a href="/moderation/regional-instruments">Regional Instruments</a></li>
            <li><a href="/moderation/international-instruments">International Instruments</a></li>
            <li><a href="/moderation/literature">Literature</a></li>
            <li><a href="/moderation/case-analyzer">Case Analyzer</a></li>
          </ul>
          <p><a href="/moderation/logout">Logout</a></p>
        </body></html>
        """
    )


def _table_key(path_segment: str) -> Optional[str]:
    mapping = {
        "court-decisions": "court_decisions",
        "domestic-instruments": "domestic_instruments",
        "regional-instruments": "regional_instruments",
        "international-instruments": "international_instruments",
        "literature": "literature",
        # New: Case Analyzer
        "case-analyzer": "case_analyzer",
    }
    return mapping.get(path_segment)


@router.get("/{category}")
def list_pending(request: Request, category: str):
    if not _is_logged_in(request):
        return RedirectResponse(url="/moderation/login", status_code=302)
    table = _table_key(category)
    if not table:
        raise HTTPException(status_code=404)
    global service
    if service is None:
        service = SuggestionService()
    items = service.list_pending(table)
    model = _category_schema(category)
    if model is None:
        raise HTTPException(status_code=404)

    def render_form(item: Dict[str, Any]) -> str:
        payload: Dict[str, Any] = item.get("payload", {}) or {}
        if category == "case-analyzer":
            normalized = _normalize_case_analyzer_payload(payload, item)
            def show(key: str) -> str:
                val = normalized.get(key)
                text = "NA" if val is None or (isinstance(val, str) and val.strip() == "") else str(val)
                return html.escape(text)
            ordered_rows = [
                ("Username", show("username")),
                ("E-Mail", show("user_email")),
                ("Model", show("model")),
                ("Date", show("date")),
                ("Case Citation", show("case_citation")),
                ("Jurisdiction", show("jurisdiction")),
                ("Jurisdiction Type", show("jurisdiction_type")),
                ("Choice of Law Section(s)", show("choice_of_law_sections")),
                ("Theme", show("theme")),
                ("Abstract", show("abstract")),
                ("Relevant Facts", show("relevant_facts")),
                ("PIL Provisions", show("pil_provisions")),
                ("Choice of Law Issue", show("choice_of_law_issue")),
                ("Court's Position", show("courts_position")),
            ]
            rows_html = [f"<div style='margin:4px 0'><strong>{html.escape(label)}:</strong> {value}</div>" for label, value in ordered_rows]
            meta = (
                f"<div style='color:#555;font-size:12px;margin-bottom:6px'>"
                f"ID #{item['id']} — Source: {html.escape(str(item.get('source') or ''))}</div>"
            )
            buttons = (
                f"<form method='post' action='/moderation/{category}/{item['id']}/approve'>"
                f"<div style='margin-top:8px'>"
                f"<button type='submit' style='padding:6px 12px'>Mark as finished</button>"
                f"<button type='submit' formaction='/moderation/{category}/{item['id']}/reject' style='padding:6px 12px;margin-left:8px'>Reject</button>"
                f"</div></form>"
            )
            return (
                f"<li style='border:1px solid #ddd;padding:10px;border-radius:6px;margin-bottom:12px'>"
                f"{meta}"
                + "".join(rows_html)
                + buttons
                + "</li>"
            )

        # Default: form-based editing for other categories
        if category != "case-analyzer":
            inputs: List[str] = []
            for fname, finfo in getattr(model, "model_fields").items():  # type: ignore[attr-defined]
                val = payload.get(fname)
                if isinstance(val, list):
                    val = ", ".join(str(v) for v in val)
                inputs.append(_render_input(fname, val, finfo))
            # moderation note (not for case analyzer)
            inputs.append(
                "<label style='display:block;margin:8px 0'>Moderation Note (optional)<br/>"
                "<textarea name='moderation_note' rows='2' style='width:100%'></textarea></label>"
            )
            buttons = (
                f"<div style='margin-top:8px'>"
                f"<button type='submit' style='padding:6px 12px'>Approve</button>"
                f"<button type='submit' formaction='/moderation/{category}/{item['id']}/reject' style='padding:6px 12px;margin-left:8px'>Reject</button>"
                f"</div>"
            )
            meta = (
                f"<div style='color:#555;font-size:12px;margin-bottom:6px'>"
                f"ID #{item['id']} — Source: {html.escape(str(item.get('source') or ''))}</div>"
            )
            return (
                f"<li style='border:1px solid #ddd;padding:10px;border-radius:6px;margin-bottom:12px'>"
                f"{meta}"
                f"<form method='post' action='/moderation/{category}/{item['id']}/approve'>"
                + "".join(inputs)
                + buttons
                + "</form></li>"
            )

        return ""  # fallback, shouldn't hit

    entries = "".join(render_form(i) for i in items)
    empty_state = "<p>No pending suggestions.</p>" if not entries else ""
    return HTMLResponse(
        f"""
        <html><head><title>Pending - {category}</title></head>
        <body>
          <h3>Pending suggestions: {category}</h3>
          <ul>{entries}</ul>
          {empty_state}
          <p><a href="/moderation">Back</a></p>
        </body></html>
        """
    )


@router.post("/{category}/{suggestion_id}/approve")
async def approve(request: Request, category: str, suggestion_id: int):
    if not _is_logged_in(request):
        return RedirectResponse(url="/moderation/login", status_code=302)
    table = _table_key(category)
    if not table:
        raise HTTPException(status_code=404)
    global service
    if service is None:
        service = SuggestionService()
    items = service.list_pending(table)
    item = next((i for i in items if i["id"] == suggestion_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Suggestion not found or not pending")
    original_payload: Dict[str, Any] = item["payload"] or {}

    # Case Analyzer: recompute normalized snapshot and mark finished; no editable inputs expected
    if category == "case-analyzer":
        normalized = _normalize_case_analyzer_payload(original_payload, item)
        service.update_payload(table, suggestion_id, {"normalized": normalized})
        service.mark_status(
            table,
            suggestion_id,
            "approved",
            request.session.get("moderator", "moderator"),
            note="",
        )
        return RedirectResponse(url=f"/moderation/{category}", status_code=302)

    # Default flow for other categories: write into main DB and mark approved
    form = await request.form()
    model = _category_schema(category)
    if model is None:
        raise HTTPException(status_code=400, detail="Unsupported category")
    updated_fields: Dict[str, Any] = {}
    for fname, finfo in getattr(model, "model_fields").items():  # type: ignore[attr-defined]
        raw = form.get(fname)
        ann = getattr(finfo, "annotation", str)
        base_t = _python_type(ann)
        if base_t is bool:
            updated_fields[fname] = "true" if raw in ("true", "on", "1", "yes") else ""
        elif base_t in (list, tuple):
            updated_fields[fname] = (raw or "").strip()
        else:
            updated_fields[fname] = raw if raw is not None else ""

    moderation_note = str(form.get("moderation_note") or "")

    global writer
    if writer is None:
        writer = MainDBWriter()
    table_map = {
        "court-decisions": "Court_Decisions",
        "domestic-instruments": "Domestic_Instruments",
        "regional-instruments": "Regional_Instruments",
        "international-instruments": "International_Instruments",
        "literature": "Literature",
    }
    target_table = table_map.get(category)
    if not target_table:
        raise HTTPException(status_code=400, detail="Unsupported category")
    payload: Dict[str, Any] = {**original_payload, **updated_fields}
    merged_id = writer.insert_record(target_table, payload)
    for key in ("jurisdiction", "jurisdiction_link"):
        if key in payload and payload.get(key):
            try:
                writer.link_jurisdictions(target_table, merged_id, payload.get(key))
            except Exception:
                pass
    service.mark_status(
        table,
        suggestion_id,
        "approved",
        request.session.get("moderator", "moderator"),
        note=moderation_note,
        merged_id=merged_id,
    )
    return RedirectResponse(url=f"/moderation/{category}", status_code=302)


@router.post("/{category}/{suggestion_id}/reject")
async def reject(request: Request, category: str, suggestion_id: int):
    if not _is_logged_in(request):
        return RedirectResponse(url="/moderation/login", status_code=302)
    table = _table_key(category)
    if not table:
        raise HTTPException(status_code=404)
    global service
    if service is None:
        service = SuggestionService()
    form = await request.form()
    moderation_note = str(form.get("moderation_note") or "")
    service.mark_status(
        table,
        suggestion_id,
        "rejected",
        request.session.get("moderator", "moderator"),
        note=moderation_note,
    )
    return RedirectResponse(url=f"/moderation/{category}", status_code=302)
