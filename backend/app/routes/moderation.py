from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

from app.config import config
from app.services.suggestions import SuggestionService
from app.services.moderation_writer import MainDBWriter

router = APIRouter(prefix="/moderation", tags=["Moderation"], include_in_schema=False)

service: SuggestionService | None = None
writer: MainDBWriter | None = None


def _is_logged_in(request: Request) -> bool:
    return bool(request.session.get("moderator"))


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
    entries = "".join(
        f"<li>#{i['id']} <pre style='white-space:pre-wrap'>{i['payload']}</pre>"
        f"<form method='post' action='/moderation/{category}/{i['id']}/approve' style='display:inline'><button>Approve</button></form>"
        f"<form method='post' action='/moderation/{category}/{i['id']}/reject' style='display:inline;margin-left:10px'><button>Reject</button></form>"
        f"</li>" for i in items
    )
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
def approve(request: Request, category: str, suggestion_id: int):
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
    payload = item["payload"]
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
    merged_id = writer.insert_record(target_table, payload)
    service.mark_status(table, suggestion_id, "approved", request.session.get("moderator", "moderator"), merged_id=merged_id)
    return RedirectResponse(url=f"/moderation/{category}", status_code=302)


@router.post("/{category}/{suggestion_id}/reject")
def reject(request: Request, category: str, suggestion_id: int):
    if not _is_logged_in(request):
        return RedirectResponse(url="/moderation/login", status_code=302)
    table = _table_key(category)
    if not table:
        raise HTTPException(status_code=404)
    global service
    if service is None:
        service = SuggestionService()
    service.mark_status(table, suggestion_id, "rejected", request.session.get("moderator", "moderator"))
    return RedirectResponse(url=f"/moderation/{category}", status_code=302)
