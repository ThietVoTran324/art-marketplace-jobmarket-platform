import uuid
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy import insert, select

from app.api.rest.dependencies import db
from app.api.rest.roles import ensure_default_roles
from app.api.rest.security import set_auth_cookie, set_csrf_cookie
from app.api.rest.utils import create_access_token, create_refresh_token, save_file_bytes
from app.config import settings
from app.httpx.app import get_httpx_client
from app.postgresql.models import UsersOrm

router = APIRouter(prefix="/users/google/auth", tags=["users-google-auth"])


@router.get("/login/")
async def login_google():
    return {
        "url": (
            "https://accounts.google.com/o/oauth2/auth"
            f"?response_type=code"
            f"&client_id={settings.GOOGLE_OAUTH2_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_OAUTH2_REDIRECT_URI}"
            f"&scope=openid%20profile%20email"
            f"&access_type=offline"
            f"&prompt=select_account"
        )
    }


@router.get("/")
async def auth_google(code: str, db: db):
    client = get_httpx_client()

    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_OAUTH2_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = await client.post(token_url, data=data)
    access_token = response.json().get("access_token")

    user_info = await client.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    user_data = user_info.json()

    user_by_google_id = await db.scalar(
        select(UsersOrm).where(UsersOrm.google_id == user_data["id"])
    )

    register = False
    if not user_by_google_id:
        username = user_data["email"].split("@")[0]
        user_by_username = await db.scalar(select(UsersOrm).where(UsersOrm.username == username))
        if user_by_username:
            username = f"{username}_{uuid.uuid4().hex[:6]}"

        picture = await client.get(user_data["picture"])

        unique_filename = f"{uuid.uuid4()}.jpg"
        media_root = Path(settings.MEDIA_PATH)
        users_dir = media_root / "users"
        users_dir.mkdir(parents=True, exist_ok=True)
        full_path = users_dir / unique_filename
        await save_file_bytes(picture.content, str(full_path))
        db_image_path = f"users/{unique_filename}"

        user_by_google_id = await db.scalar(
            insert(UsersOrm)
            .values(
                google_id=user_data["id"],
                username=username,
                email=user_data["email"],
                verified=True,
                image=db_image_path,
            )
            .returning(UsersOrm)
        )
        register = True
        await ensure_default_roles(db, user_by_google_id.id)
        await db.commit()

    access_token = create_access_token({"user_id": user_by_google_id.id})
    refresh_token = create_refresh_token({"user_id": user_by_google_id.id})

    if not register:
        response_frontend = RedirectResponse(url=settings.FRONTEND_DOMAIN, status_code=302)
    else:
        response_frontend = RedirectResponse(
            url=f"{settings.FRONTEND_DOMAIN}?register=true", status_code=302
        )

    set_auth_cookie(response_frontend, "access_token", access_token)
    set_auth_cookie(response_frontend, "refresh_token", refresh_token)
    set_csrf_cookie(response_frontend)

    return response_frontend
