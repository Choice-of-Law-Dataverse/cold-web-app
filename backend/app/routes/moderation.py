from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, Any, Dict, List, Tuple, Type
import html
from datetime import date

from app.config import config
from app.services.suggestions import SuggestionService
from app.services.moderation_writer import MainDBWriter
from app.schemas.suggestions import (
    CourtDecisionSuggestion,
    DomesticInstrumentSuggestion,
    RegionalInstrumentSuggestion,
    InternationalInstrumentSuggestion,
    LiteratureSuggestion,
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
    longish = any(k in name for k in ["abstract", "quote", "excerpt", "notes", "relevant", "original_text", "english_translation"])
    if longish:
        return (
            f"<label style='display:block;margin:6px 0'>{html.escape(label)}<br/>"
            f"<textarea name='{html.escape(name)}' rows='4' style='width:100%'>{safe_val}</textarea></label>"
        )
    return (
        f"<label style='display:block;margin:6px 0'>{html.escape(label)} "
        f"<input type='text' name='{html.escape(name)}' value='{safe_val}'/></label>"
    )


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
        # Build inputs for every field in the schema, always included
        inputs: List[str] = []
        for fname, finfo in getattr(model, "model_fields").items():  # type: ignore[attr-defined]
            val = payload.get(fname)
            # dates in payload may be iso strings; fine
            # lists -> show as comma-separated string
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            inputs.append(_render_input(fname, val, finfo))
        # moderation note
        inputs.append(
            "<label style='display:block;margin:8px 0'>Moderation Note (optional)<br/>"
            "<textarea name='moderation_note' rows='2' style='width:100%'></textarea></label>"
        )
        # Buttons using HTML5 formaction so we don't duplicate inputs
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

    entries = "".join(render_form(i) for i in items)
    return HTMLResponse(
        f"""
        <html><head><title>Pending - {category}</title></head>
        <body>
          <h3>Pending suggestions: {category}</h3>
          <ul>{entries}</ul>
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
            # Checkbox only present when checked; set '' when unchecked to allow DB boolean coercion to None
            updated_fields[fname] = "true" if raw in ("true", "on", "1", "yes") else ""
        elif base_t in (list, tuple):
            # Store as comma-separated string (DB usually expects text)
            updated_fields[fname] = (raw or "").strip()
        else:
            updated_fields[fname] = raw if raw is not None else ""

    # Merge edited fields into original payload to preserve any extra keys
    payload: Dict[str, Any] = {**original_payload, **updated_fields}
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
    moderation_note = str(form.get("moderation_note") or "")
    merged_id = writer.insert_record(target_table, payload)
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
