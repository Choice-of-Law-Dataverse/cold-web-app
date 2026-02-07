# ruff: noqa: E501
import html
import logging
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.datastructures import FormData

from app.config import config
from app.schemas.suggestions import (
    CaseAnalyzerSuggestion,
    CourtDecisionSuggestion,
    DomesticInstrumentSuggestion,
    InternationalInstrumentSuggestion,
    LiteratureSuggestion,
    RegionalInstrumentSuggestion,
)
from app.services.moderation_writer import MainDBWriter
from app.services.suggestion_approval import (
    approve_case_analyzer,
    first_match,
    get_target_table,
    link_jurisdictions_for_default_categories,
    normalize_case_analyzer_payload,
    normalize_domestic_instruments,
)
from app.services.suggestions import SuggestionService

logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/moderation", tags=["Moderation"], include_in_schema=False)
router = APIRouter(prefix="", tags=["Moderation"], include_in_schema=False)

service: SuggestionService | None = None
writer: MainDBWriter | None = None


def _is_logged_in(request: Request) -> bool:
    return bool(request.session.get("moderator"))


def _category_schema(category: str):
    mapping: dict[str, Any] = {
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
        from typing import Union, get_args, get_origin

        origin = get_origin(t)
        if origin is None:
            return t
        if origin in (list, tuple, dict):
            return origin
        if origin is Union:
            args = [a for a in get_args(t) if a is not type(None)]  # noqa: E721
            # Recurse to resolve nested typing like Optional[List[str]] -> list
            return _python_type(args[0]) if args else Any
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
        return f"<label><input type='checkbox' name='{html.escape(name)}' value='true'{checked}/> {html.escape(label)}</label>"
    if base_t in (date,):
        return f"<label>{html.escape(label)} <input type='date' name='{html.escape(name)}' value='{safe_val}'/></label>"
    if base_t in (int, float):
        return f"<label>{html.escape(label)} <input type='number' step='any' name='{html.escape(name)}' value='{safe_val}'/></label>"
    # For lists, accept comma-separated text
    if base_t in (list, tuple):
        return f"<label>{html.escape(label)} <input type='text' name='{html.escape(name)}' value='{safe_val}' placeholder='Comma-separated values'/></label>"
    # Default to text input; use textarea for likely long text fields
    longish = any(
        k in name
        for k in [
            "abstract",
            "quote",
            "excerpt",
            "notes",
            "relevant",
            "original_text",
            "english_translation",
            "raw_data",
            "legal_provisions",
        ]
    ) or (isinstance(value, str) and len(value) > 180)
    if longish:
        return f"<label>{html.escape(label)}<br/><textarea name='{html.escape(name)}' rows='4'>{safe_val}</textarea></label>"
    # Fallback: standard text input
    return f"<label>{html.escape(label)} <input type='text' name='{html.escape(name)}' value='{safe_val}'/></label>"


def _page(title: str, inner_html: str, show_logout: bool = True) -> HTMLResponse:
    style = """
        <style>
            :root { --bg:#FAFAFA; --text:#0F0035; --accent:#6F4DFA; --card:#FFFFFF; }
            *{ box-sizing: border-box; }
            body{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:var(--bg); color:var(--text); }
            a{ color:var(--accent); text-decoration:none; }
            a:hover{ text-decoration:underline; }
            .container{ max-width:960px; margin:0 auto; padding:24px; }
            .header{ display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }
            h1,h2,h3{ margin:0 0 12px; }
            .card{ background:var(--card); border:1px solid #EAE7FF; border-radius:10px; padding:16px; box-shadow:0 1px 2px rgba(15,0,53,0.05); }
            ul.plain{ list-style:none; padding:0; margin:0; }
            .meta{ color:#463E78; font-size:12px; }
            .byline{ color:#5B528F; font-size:12px; }
            button{ background:var(--accent); color:var(--bg); border:0; border-radius:8px; padding:8px 14px; cursor:pointer; }
            button:hover{ filter:brightness(0.95); }
            input, textarea{ width:100%; padding:8px 10px; border:1px solid #E0D9FF; border-radius:8px; background:var(--card); color:var(--text); }
            label{ display:block; margin:8px 0; }
            .space-x > * + * { margin-left: 8px; }
        </style>
        """
    logout_html = "" if not show_logout else "<a href='/moderation/logout'>Logout</a>"
    html_doc = f"""
        <html>
            <head>
                <title>{html.escape(title)}</title>
                {style}
            </head>
            <body>
                <div class='container'>
                    <div class='header'>
                        <h2>{html.escape(title)}</h2>
                        <div>{logout_html}</div>
                    </div>
                    {inner_html}
                </div>
            </body>
        </html>
        """
    return HTMLResponse(html_doc)


# New helpers: overview and detail rendering


def _render_overview_item(category: str, item: dict[str, Any]) -> str:
    payload: dict[str, Any] = item.get("payload", {}) or {}

    def format_created(value: Any) -> str:
        if isinstance(value, datetime | date):
            return value.isoformat()
        if value is None:
            return ""
        return str(value)

    def val_to_str(v: Any) -> str:
        if v is None:
            return "NA"
        if isinstance(v, list | tuple):
            return ", ".join(str(x) for x in v if x is not None)
        return str(v)

    # Case Analyzer summary
    if category == "case-analyzer":
        normalized = normalize_case_analyzer_payload(payload, item)
        title = normalized.get("case_citation") or f"Case #{item['id']}"
        parts = [
            ("Jurisdiction", normalized.get("jurisdiction")),
            ("Theme", normalized.get("theme")),
            ("Date", normalized.get("date")),
        ]
        meta = " | ".join(f"{html.escape(k)}: {html.escape(val_to_str(v))}" for k, v in parts)
        src = html.escape(str(item.get("source") or ""))
        created = item.get("created_at")
        created_s = format_created(created)
        submit_name = normalized.get("username") or item.get("username") or payload.get("username")
        submit_email = normalized.get("user_email") or item.get("user_email") or payload.get("user_email")
        byline = (
            f"<div style='color:#555;font-size:12px;margin-top:2px'>By: {html.escape(str(submit_name or ''))} — E-Mail: {html.escape(str(submit_email or ''))}</div>"
            if (submit_name or submit_email)
            else ""
        )
        return (
            f"<li style='border:1px solid #eee;padding:8px;border-radius:6px;margin-bottom:8px'>"
            f"<a href='/moderation/{category}/{item['id']}' style='font-weight:600;text-decoration:none'>{html.escape(str(title))}</a>"
            f"<div style='color:#555;font-size:12px;margin-top:4px'>{meta}</div>"
            f"{byline}"
            f"<div style='color:#777;font-size:11px;margin-top:2px'>ID #{item['id']} — Source: {src} — Created: {html.escape(created_s)}</div>"
            f"</li>"
        )

    # Default: other categories
    summary_specs: dict[str, dict[str, Any]] = {
        "court-decisions": {
            "title_keys": ["case_citation", "case_name", "title", "name"],
            "info": [
                ("Jurisdiction", ["jurisdiction", "country"]),
                ("Date", ["date_of_judgment", "decision_date", "date", "year"]),
            ],
        },
        "domestic-instruments": {
            "title_keys": ["title", "name"],
            "info": [
                ("Jurisdiction", ["jurisdiction", "country"]),
                ("Date", ["date", "year"]),
            ],
        },
        "regional-instruments": {
            "title_keys": ["title", "name"],
            "info": [
                ("Jurisdiction", ["jurisdiction", "region"]),
                ("Date", ["date", "year"]),
            ],
        },
        "international-instruments": {
            "title_keys": ["title", "name"],
            "info": [("Date", ["date", "year"])],
        },
        "literature": {
            "title_keys": ["title", "name"],
            "info": [
                ("Authors", ["authors", "author"]),
                ("Year", ["year", "publication_year"]),
            ],
        },
    }

    spec = summary_specs.get(category, {"title_keys": ["title", "name"], "info": []})

    def first_key(*keys: str) -> Any:
        return first_match(payload, *keys)

    title = first_key(*spec["title_keys"]) or f"Entry #{item['id']}"
    info_parts: list[tuple[str, Any]] = []
    for label, keys in spec.get("info", []):
        info_parts.append((label, first_key(*keys)))
    meta = " | ".join(f"{html.escape(label)}: {html.escape(val_to_str(val))}" for label, val in info_parts)
    src = html.escape(str(item.get("source") or ""))
    created = item.get("created_at")
    created_s = format_created(created)
    submit_name = item.get("username") or first_key("username", "submitter_name", "name")
    submit_email = item.get("token_sub") or item.get("user_email") or first_key("user_email", "email", "submitter_email")
    submit_comments = first_key("submitter_comments", "comments", "note")
    comments_snippet = ""
    if isinstance(submit_comments, str) and submit_comments.strip():
        txt = submit_comments.strip()
        if len(txt) > 120:
            txt = txt[:117] + "..."
        comments_snippet = f" — Comments: {html.escape(txt)}"
    byline = (
        f"<div style='color:#555;font-size:12px;margin-top:2px'>By: {html.escape(str(submit_name or ''))} — E-Mail: {html.escape(str(submit_email or ''))}{comments_snippet}</div>"
        if (submit_name or submit_email or submit_comments)
        else ""
    )
    return (
        f"<li style='border:1px solid #eee;padding:8px;border-radius:6px;margin-bottom:8px'>"
        f"<a href='/moderation/{category}/{item['id']}' style='font-weight:600;text-decoration:none'>{html.escape(str(title))}</a>"
        f"<div style='color:#555;font-size:12px;margin-top:4px'>{meta}</div>"
        f"{byline}"
        f"<div style='color:#777;font-size:11px;margin-top:2px'>ID #{item['id']} — Source: {src} — Created: {html.escape(created_s)}</div>"
        f"</li>"
    )


def _render_detail_entry(category: str, model, item: dict[str, Any]) -> str:
    payload: dict[str, Any] = item.get("payload", {}) or {}
    if category == "case-analyzer":
        normalized = normalize_case_analyzer_payload(payload, item)

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
        rows_html = [
            f"<div style='margin:4px 0'><strong>{html.escape(label)}:</strong> {value}</div>" for label, value in ordered_rows
        ]
        submit_name = normalized.get("username") or item.get("username") or payload.get("username")
        submit_email = normalized.get("user_email") or item.get("user_email") or payload.get("user_email")
        by_meta = (
            f" — By: {html.escape(str(submit_name or ''))} — E-Mail: {html.escape(str(submit_email or ''))}"
            if (submit_name or submit_email)
            else ""
        )
        meta = f"<div style='color:#555;font-size:12px;margin-bottom:6px'>ID #{item['id']} — Source: {html.escape(str(item.get('source') or ''))}{by_meta}</div>"
        buttons = (
            f"<form method='post' action='/moderation/{category}/{item['id']}/approve' onsubmit='this.querySelectorAll(\"button\").forEach(b=>b.disabled=true)'>"
            f"<div style='margin-top:8px'>"
            f"<button type='submit' style='padding:6px 12px'>Mark as finished</button>"
            f"<button type='submit' formaction='/moderation/{category}/{item['id']}/reject' style='padding:6px 12px;margin-left:8px'>Reject</button>"
            f"</div></form>"
        )
        return (
            f"<div style='border:1px solid #ddd;padding:10px;border-radius:6px;margin-bottom:12px'>{meta}"
            + "".join(rows_html)
            + buttons
            + "</div>"
        )

    # Default: form-based editing for other categories
    inputs: list[str] = []
    # Do not render submitter meta as editable inputs; show read-only in header instead
    _meta_fields = {
        "submitter_email",
        "submitter_comments",
        "official_source_pdf",
        "source_pdf",
        "attachment",
    }
    for fname, finfo in model.model_fields.items():  # type: ignore[attr-defined]
        if fname in _meta_fields:
            continue
        val = payload.get(fname)
        if isinstance(val, list):
            val = ", ".join(str(v) for v in val)
        try:
            rendered = _render_input(fname, val, finfo)
        except Exception:
            # Fallback to a simple text input if rendering fails
            safe_label = html.escape(finfo.description or fname.replace("_", " ").title())
            safe_name = html.escape(fname)
            safe_val = html.escape("" if val is None else str(val))
            rendered = f"<label>{safe_label} <input type='text' name='{safe_name}' value='{safe_val}'/></label>"
        inputs.append(rendered)
    # Moderation note field removed per request
    buttons = f"<div style='margin-top:8px'><button type='submit' style='padding:6px 12px'>Approve</button><button type='submit' formaction='/moderation/{category}/{item['id']}/reject' style='padding:6px 12px;margin-left:8px'>Reject</button></div>"
    submit_name = item.get("username") or first_match(payload, "username", "submitter_name", "name")
    submit_email = item.get("user_email") or first_match(payload, "user_email", "email", "submitter_email")
    submit_comments = first_match(payload, "submitter_comments", "comments", "note")
    comments_snippet = ""
    if isinstance(submit_comments, str) and submit_comments.strip():
        comments_snippet = f" — Comments: {html.escape(submit_comments.strip())}"
    by_meta = (
        f" — Submitted by: {html.escape(str(submit_name or ''))} — E-Mail: {html.escape(str(submit_email or ''))}{comments_snippet}"  # noqa: E501
        if (submit_name or submit_email or submit_comments)
        else ""
    )
    # Explicit read-only block for submitter info (clear visibility)
    submit_block = ""
    if submit_name or submit_email or submit_comments:
        comments_block = ""
        if isinstance(submit_comments, str) and submit_comments.strip():
            # Preserve line breaks in comments
            c = html.escape(submit_comments.strip()).replace("\n", "<br/>")
            comments_block = f"<div><strong>Comments:</strong> {c}</div>"
        submit_block = (
            "<div style='background:#F8F7FF;border:1px solid #EAE7FF;padding:8px;border-radius:6px;margin:8px 0'>"
            + (f"<div><strong>Submitted by:</strong> {html.escape(str(submit_name or ''))}</div>" if submit_name else "")
            + (f"<div><strong>E-Mail:</strong> {html.escape(str(submit_email or ''))}</div>" if submit_email else "")
            + comments_block
            + "</div>"
        )
    meta = f"<div style='color:#555;font-size:12px;margin-bottom:6px'>ID #{item['id']} — Source: {html.escape(str(item.get('source') or ''))}{by_meta}</div>"  # noqa: E501
    # Safeguard join if any element is None
    inputs_html = "".join(i for i in inputs if isinstance(i, str))
    return (
        f"<div style='border:1px solid #ddd;padding:10px;border-radius:6px;margin-bottom:12px'>{meta}{submit_block}<form method='post' action='/moderation/{category}/{item['id']}/approve' onsubmit='this.querySelectorAll(\"button\").forEach(b=>b.disabled=true)'>"  # noqa: E501
        + inputs_html
        + buttons
        + "</form></div>"
    )


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if _is_logged_in(request):
        return RedirectResponse(url="/moderation", status_code=302)
    content = (
        "<div class='card' style='max-width:520px'>"
        "<form method='post' action='/moderation/login'>"
        "<label>Username<input name='username'/></label>"
        "<label>Password<input name='password' type='password'/></label>"
        "<div class='space-x'><button type='submit'>Login</button></div>"
        "</form>"
        "</div>"
    )
    return _page("Moderation Login", content, show_logout=False)


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
    content = (
        "<div class='card'>"
        "<ul class='plain'>"
        "<li><a href='/moderation/court-decisions'>Court Decisions</a></li>"
        "<li><a href='/moderation/domestic-instruments'>Domestic Instruments</a></li>"
        "<li><a href='/moderation/regional-instruments'>Regional Instruments</a></li>"
        "<li><a href='/moderation/international-instruments'>International Instruments</a></li>"
        "<li><a href='/moderation/literature'>Literature</a></li>"
        "<li><a href='/moderation/case-analyzer'>Case Analyzer</a></li>"
        "</ul>"
        "</div>"
    )
    return _page("Suggestions Moderation", content)


def _table_key(path_segment: str) -> str | None:
    mapping = {
        "court-decisions": "court_decisions",
        "domestic-instruments": "domestic_instruments",
        "regional-instruments": "regional_instruments",
        "international-instruments": "international_instruments",
        "literature": "literature",
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

    # Use specialized method for case-analyzer that checks moderation_status='pending'
    if category == "case-analyzer":
        items = service.list_pending_case_analyzer()
    else:
        items = service.list_pending(table)

    entries = "".join(_render_overview_item(category, i) for i in items)
    empty_state = "<p>No pending suggestions.</p>" if not entries else ""
    content = f"<h3>Pending suggestions: {html.escape(category)}</h3><ul class='plain'>{entries}</ul>{empty_state}<p><a href='/moderation'>Back</a></p>"  # noqa: E501
    return _page(f"Pending - {category}", content)


@router.get("/{category}/{suggestion_id}")
def view_entry(request: Request, category: str, suggestion_id: int):
    if not _is_logged_in(request):
        return RedirectResponse(url="/moderation/login", status_code=302)
    table = _table_key(category)
    if not table:
        raise HTTPException(status_code=404)
    global service
    if service is None:
        service = SuggestionService()

    # Use specialized method for case-analyzer
    if category == "case-analyzer":
        items = service.list_pending_case_analyzer()
    else:
        items = service.list_pending(table)

    item = next((i for i in items if i["id"] == suggestion_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Suggestion not found or not pending")
    model = _category_schema(category)
    if model is None:
        raise HTTPException(status_code=404)

    detail_html = _render_detail_entry(category, model, item)
    content = f"<h3>{html.escape(category.title())} — Entry #{suggestion_id}</h3>{detail_html}<p><a href='/moderation/{html.escape(category)}'>Back to list</a></p>"  # noqa: E501
    return _page(f"Detail - {category} #{suggestion_id}", content)


@router.post("/{category}/{suggestion_id}/approve")
async def approve(request: Request, category: str, suggestion_id: int):
    if not _is_logged_in(request):
        return RedirectResponse(url="/moderation/login", status_code=302)
    table = _table_key(category)
    if not table:
        raise HTTPException(status_code=404)
    global service, writer, nocodb_service
    if service is None:
        service = SuggestionService()
    if writer is None:
        writer = MainDBWriter()
    assert service is not None
    assert writer is not None

    # Use specialized method for case-analyzer
    if category == "case-analyzer":
        items = service.list_pending_case_analyzer()
    else:
        items = service.list_pending(table)

    item = next((i for i in items if i["id"] == suggestion_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Suggestion not found or not pending")
    original_payload: dict[str, Any] = item["payload"] or {}

    if category == "case-analyzer":
        assert service is not None
        assert writer is not None
        await approve_case_analyzer(
            service,
            writer,
            table,
            suggestion_id,
            original_payload,
            item,
            request.session.get("moderator", "moderator"),
        )
        return RedirectResponse(url=f"/moderation/{category}", status_code=302)

    await _approve_default_category(request, category, table, suggestion_id, original_payload)
    return RedirectResponse(url=f"/moderation/{category}", status_code=302)


async def _approve_default_category(
    request: Request,
    category: str,
    table: str,
    suggestion_id: int,
    original_payload: dict[str, Any],
) -> None:
    """Handle approval for default categories (non-case-analyzer)."""
    global service, writer
    assert service is not None
    assert writer is not None

    form = await request.form()
    model = _category_schema(category)
    if model is None:
        raise HTTPException(status_code=400, detail="Unsupported category")

    updated_fields = _extract_form_fields(form, model)
    moderation_note = ""

    target_table = get_target_table(category)
    if not target_table:
        raise HTTPException(status_code=400, detail="Unsupported category")

    if target_table == "Domestic_Instruments":
        normalize_domestic_instruments(updated_fields)

    payload_merged: dict[str, Any] = {**original_payload, **updated_fields}
    _reserved = {
        "submitter_email",
        "submitter_comments",
        "official_source_pdf",
        "source_pdf",
        "attachment",
    }
    payload_for_writer = {k: v for k, v in payload_merged.items() if k not in _reserved}

    merged_id = writer.insert_record(target_table, payload_for_writer)
    link_jurisdictions_for_default_categories(writer, target_table, merged_id, payload_for_writer)

    service.mark_status(
        table,
        suggestion_id,
        "approved",
        request.session.get("moderator", "moderator"),
        note=moderation_note,
        merged_id=merged_id,
    )


def _extract_form_fields(form: FormData, model: type) -> dict[str, Any]:
    """Extract and type-convert form fields based on model schema."""
    updated_fields: dict[str, Any] = {}
    _reserved = {
        "submitter_email",
        "submitter_comments",
        "official_source_pdf",
        "source_pdf",
        "attachment",
    }

    for fname, finfo in model.model_fields.items():  # type: ignore[attr-defined]
        if fname in _reserved:
            continue
        raw = form.get(fname)
        ann = getattr(finfo, "annotation", str)
        base_t = _python_type(ann)

        if base_t is bool:
            updated_fields[fname] = "true" if raw in ("true", "on", "1", "yes") else ""
        elif base_t in (list, tuple):
            list_value = raw if isinstance(raw, str) else ""
            updated_fields[fname] = list_value.strip()
        else:
            if isinstance(raw, UploadFile):
                updated_fields[fname] = raw.filename or ""
            elif isinstance(raw, str):
                updated_fields[fname] = raw
            else:
                updated_fields[fname] = "" if raw is None else str(raw)

    return updated_fields


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
    moderation_note = ""
    service.mark_status(
        table,
        suggestion_id,
        "rejected",
        request.session.get("moderator", "moderator"),
        note=moderation_note,
    )
    return RedirectResponse(url=f"/moderation/{category}", status_code=302)
