from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from app.auth import verify_jwt_token

router = APIRouter(
    prefix="/api/user", tags=["User"], dependencies=[Depends(verify_jwt_token)]
)


@router.get("/get_user_info")
def get_user_info():
    # We can return a JSONResponse with headers
    response = JSONResponse({"message": "Send Client Hints"})
    response.headers["Accept-CH"] = (
        "Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version, Sec-CH-UA-Model, Sec-CH-UA, Sec-CH-UA-Mobile"
    )
    return response


@router.get("/user_info")
def user_info(request: Request):
    brand = request.headers.get("Sec-CH-UA", "Unknown")
    mobile = request.headers.get("Sec-CH-UA-Mobile", "Unknown")
    platform = request.headers.get("Sec-CH-UA-Platform", "Unknown Platform")
    platform_version = request.headers.get(
        "Sec-CH-UA-Platform-Version", "Unknown Version"
    )
    model = request.headers.get("Sec-CH-UA-Model", "Unknown Model")

    return {
        "brand": brand,
        "mobile": mobile,
        "platform": platform,
        "platform_version": platform_version,
        "model": model,
    }
