"""Pin original signed URL helpers (HMAC)."""
from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import urlencode

from fastapi import HTTPException, status

from app.config import settings


def _signing_secret() -> str:
    return getattr(settings, "PIN_MEDIA_SIGNING_SECRET", None) or settings.JWT_SECRET_KEY


def sign_original_params(pin_id: int, user_id: int, ttl_seconds: int | None = None) -> dict[str, str]:
    ttl = ttl_seconds if ttl_seconds is not None else settings.PIN_ORIGINAL_URL_TTL_SECONDS
    exp = int(time.time()) + int(ttl)
    payload = f"{pin_id}:{user_id}:{exp}"
    sig = hmac.new(
        _signing_secret().encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {"exp": str(exp), "uid": str(user_id), "sig": sig}


def build_original_file_path(pin_id: int, user_id: int, ttl_seconds: int | None = None) -> str:
    params = sign_original_params(pin_id, user_id, ttl_seconds)
    return f"/pins/original/{pin_id}/file?{urlencode(params)}"


def verify_original_signature(pin_id: int, uid: int, exp: int, sig: str) -> None:
    now = int(time.time())
    if exp < now:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="signed_url_expired")
    payload = f"{pin_id}:{uid}:{exp}"
    expected = hmac.new(
        _signing_secret().encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="signed_url_invalid")
