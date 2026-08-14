import secrets

from fastapi import Response

from app.config import settings

CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"


def cookie_secure() -> bool:
    return not settings.DEV_MODE


def set_auth_cookie(response: Response, key: str, value: str) -> None:
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=cookie_secure(),
        samesite="lax",
        path="/",
    )


def set_csrf_cookie(response: Response) -> str:
    token = secrets.token_urlsafe(32)
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,
        secure=cookie_secure(),
        samesite="lax",
        path="/",
    )
    return token
