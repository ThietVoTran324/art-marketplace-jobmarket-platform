import json
import mimetypes
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import delete, desc, func, insert, or_, select, update

from app.api.rest.dependencies import db, filter, filter_with_value, optional_user_id, user_id
from app.api.rest.ownership import assert_can_access_pin_original, assert_pin_owner
from app.api.rest.pins.media_signing import (
    build_original_file_path,
    verify_original_signature,
)
from app.api.rest.pins.watermark import original_dir
from app.api.rest.tags.routes import get_all_tags
from app.api.rest.utils import save_file
from app.config import settings
from app.postgresql.models import (
    CommentsOrm,
    LikesOrm,
    PinStatsOrm,
    PinsOrm,
    TagsOrm,
    UsersOrm,
    pins_tags,
    users_pins,
)

from .schemas import FeedMetaIn, FeedMetaOut, OriginalUrlOut, PinIn, PinOut

mimetypes.add_type("image/webp", ".webp")

from app.celery.tasks import (
    generate_pin_preview,
    make_update_pin_created_for_followers,
    make_update_save_pin,
    user_view_pin,
)

router = APIRouter(prefix="/pins", tags=["pins"])

ALLOWED_FILE_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
    "image/png",
    "image/bmp",
    "video/mp4",
    "video/webm",
]


def _default_preview_file() -> Path:
    return Path(settings.MEDIA_PATH) / "notauth" / "1.jpg"


@router.get("/", response_model=list[PinOut])
async def get_pins(db: db, filter: filter, user_id: optional_user_id):
    _ = user_id  # optional; anonymous may browse the home feed
    pins = await db.scalars(
        select(PinsOrm).offset(filter.offset).limit(filter.limit).order_by(desc(PinsOrm.id))
    )

    return pins


@router.post("/feed-meta", response_model=list[FeedMetaOut])
async def get_feed_meta(body: FeedMetaIn, db: db, user_id: optional_user_id):
    """Batch username + like/comment counts for feed cards (cuts N+1)."""
    raw_ids = body.pin_ids or []
    # Preserve order, de-dupe, hard cap
    seen: set[int] = set()
    pin_ids: list[int] = []
    for pid in raw_ids:
        if not isinstance(pid, int) or pid <= 0 or pid in seen:
            continue
        seen.add(pid)
        pin_ids.append(pid)
        if len(pin_ids) >= 50:
            break
    if not pin_ids:
        return []

    pins = (
        await db.scalars(select(PinsOrm).where(PinsOrm.id.in_(pin_ids)))
    ).all()
    pin_by_id = {p.id: p for p in pins}
    owner_ids = {p.user_id for p in pins}
    users = (
        await db.scalars(select(UsersOrm).where(UsersOrm.id.in_(owner_ids)))
    ).all() if owner_ids else []
    username_by_uid = {u.id: u.username for u in users}

    likes_rows = (
        await db.execute(
            select(LikesOrm.pin_id, func.count())
            .where(LikesOrm.pin_id.in_(pin_ids))
            .group_by(LikesOrm.pin_id)
        )
    ).all()
    likes_by_pin = {row[0]: int(row[1]) for row in likes_rows}

    liked_ids: set[int] = set()
    if user_id is not None:
        liked_ids = set(
            (
                await db.scalars(
                    select(LikesOrm.pin_id).where(
                        LikesOrm.user_id == user_id,
                        LikesOrm.pin_id.in_(pin_ids),
                    )
                )
            ).all()
        )

    comments_rows = (
        await db.execute(
            select(CommentsOrm.pin_id, func.count())
            .where(CommentsOrm.pin_id.in_(pin_ids))
            .group_by(CommentsOrm.pin_id)
        )
    ).all()
    comments_by_pin = {row[0]: int(row[1]) for row in comments_rows}

    out: list[FeedMetaOut] = []
    for pid in pin_ids:
        pin = pin_by_id.get(pid)
        if pin is None:
            continue
        out.append(
            FeedMetaOut(
                pin_id=pid,
                username=username_by_uid.get(pin.user_id),
                likes_count=likes_by_pin.get(pid, 0),
                liked=pid in liked_ids,
                comments_count=comments_by_pin.get(pid, 0),
            )
        )
    return out


@router.get("/tag/{tag_name}", response_model=list[PinOut])
async def get_pins_by_tag(tag_name: str, user_id: user_id, db: db, filter: filter):
    tag = await db.scalar(select(TagsOrm).where(TagsOrm.name == tag_name))
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tag not found")

    result = await db.execute(select(pins_tags).where(pins_tags.c.tag_id == tag.id))
    rows = result.all()
    pins = []
    for row in rows:
        pin_id = row[0]
        pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
        pins.append(pin)
    return pins[filter.offset : filter.offset + filter.limit]


@router.get("/search", response_model=list[PinOut])
async def search_pins(filter_with_value: filter_with_value, user_id: user_id, db: db):
    result = {}

    split_and_clean = [part for part in filter_with_value.value.split(" ") if part.strip()]
    tags = await get_all_tags(db, user_id)
    tag_list = tags.all()
    for value in split_and_clean:
        pins = await db.scalars(
            select(PinsOrm).where(
                or_(PinsOrm.title.ilike(f"%{value}%"), PinsOrm.description.ilike(f"%{value}%"))
            )
        )
        pin_list = pins.all()
        for pin in pin_list:
            if pin.id not in result:
                result[pin.id] = pin

        for tag in tag_list:
            if value in tag.name:
                tag = await db.scalar(select(TagsOrm).where(TagsOrm.name == tag.name))
                result_table = await db.execute(
                    select(pins_tags).where(pins_tags.c.tag_id == tag.id)
                )
                rows = result_table.all()
                for row in rows:
                    pin_by_tag_id = row[0]
                    if pin_by_tag_id not in result:
                        pin_by_tag = await db.scalar(
                            select(PinsOrm).where(PinsOrm.id == pin_by_tag_id)
                        )
                        result[pin_by_tag.id] = pin_by_tag

    return [pin for pin in result.values()][
        filter_with_value.offset : filter_with_value.offset + filter_with_value.limit
    ]


@router.post("/", response_model=PinOut, status_code=status.HTTP_201_CREATED)
async def create_pin(user_id: user_id, db: db, pin_model: PinIn):
    pin = await db.scalar(
        insert(PinsOrm).values(**pin_model.model_dump(), user_id=user_id).returning(PinsOrm)
    )
    await db.execute(insert(PinStatsOrm).values(pin_id=pin.id, view_count=0))
    await db.commit()
    return pin


@router.post("/create-pin-entity", response_model=PinOut, status_code=status.HTTP_201_CREATED)
async def create_pin_entity(
    user_id: user_id,
    db: db,
    pin_model: str = Form(...),
    file: UploadFile = File(...),
):
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=415, detail="Invalid file type")

    pin_data = json.loads(pin_model)
    pin = await db.scalar(
        insert(PinsOrm).values(**pin_data, user_id=user_id).returning(PinsOrm)
    )
    await db.execute(insert(PinStatsOrm).values(pin_id=pin.id, view_count=0))

    filename = f"{uuid.uuid4()}{Path(file.filename).suffix}"
    full_path = original_dir() / filename
    await save_file(file, str(full_path))
    original_rel = f"pins/original/{filename}"

    pin = await db.scalar(
        update(PinsOrm)
        .where(PinsOrm.id == pin.id)
        .values(original_image=original_rel)
        .returning(PinsOrm)
    )
    await db.commit()

    pin_id = pin.id
    # Sync preview so response has image path (Celery task also usable via .delay)
    generate_pin_preview.run(pin_id)
    db.expire_all()
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    make_update_pin_created_for_followers.delay(user_id, pin.id)
    return pin


@router.delete("/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete_created_pin(pin_id: int, user_id: user_id, db: db):
    await assert_pin_owner(db, pin_id, user_id)
    await db.execute(delete(PinsOrm).where(PinsOrm.id == pin_id))
    await db.commit()
    return {"status", "ok"}


@router.post("/upload/{id}", response_model=PinOut)
async def upload_image(user_id: user_id, id: int, db: db, file: UploadFile):
    await assert_pin_owner(db, id, user_id)

    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=415, detail="Invalid file type")

    filename = f"{uuid.uuid4()}{Path(file.filename).suffix}"
    full_path = original_dir() / filename
    await save_file(file, str(full_path))
    original_rel = f"pins/original/{filename}"

    pin = await db.scalar(
        update(PinsOrm)
        .where(PinsOrm.id == id)
        .values(original_image=original_rel, image=None, videoPreview=None)
        .returning(PinsOrm)
    )
    await db.commit()

    pin_id = pin.id
    generate_pin_preview.run(pin_id)
    db.expire_all()
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    return pin


@router.get("/upload/{id}")
async def get_image(id: int, db: db, user_id: optional_user_id):
    """Serve watermarked preview only — never the original. Anonymous OK for feed."""
    _ = user_id
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == id))
    if pin is None:
        raise HTTPException(status_code=404, detail="pin not found")

    media_root = Path(settings.MEDIA_PATH)
    default_image = _default_preview_file()

    preview_rel = pin.image or pin.videoPreview
    if not preview_rel:
        return FileResponse(default_image, media_type="image/jpeg")

    full_path = media_root / preview_rel
    if not full_path.exists():
        return FileResponse(default_image, media_type="image/jpeg")

    mime_type, _ = mimetypes.guess_type(str(full_path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    return FileResponse(full_path, media_type=mime_type)


@router.get("/original/{id}", response_model=OriginalUrlOut)
async def get_original_signed_url(user_id: user_id, id: int, db: db):
    pin = await assert_can_access_pin_original(db, id, user_id)
    if not pin.original_image:
        raise HTTPException(status_code=404, detail="original_not_found")

    url = build_original_file_path(id, user_id)
    return OriginalUrlOut(url=url, expires_in=settings.PIN_ORIGINAL_URL_TTL_SECONDS)


@router.get("/original/{id}/file")
async def get_original_file(
    id: int,
    exp: int = Query(...),
    uid: int = Query(...),
    sig: str = Query(...),
):
    verify_original_signature(id, uid, exp, sig)

    from app.api.rest.ownership import assert_can_access_pin_original
    from app.postgresql.database import async_session_maker

    async with async_session_maker() as session:
        # Re-check ACL even if signed URL was leaked within TTL.
        pin = await assert_can_access_pin_original(session, id, uid)
        if not pin.original_image:
            raise HTTPException(status_code=404, detail="original_not_found")
        full_path = Path(settings.MEDIA_PATH) / pin.original_image
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="original_file_missing")

        mime_type, _ = mimetypes.guess_type(str(full_path))
        if mime_type is None:
            mime_type = "application/octet-stream"
        return FileResponse(full_path, media_type=mime_type)


@router.get("/{id}", response_model=PinOut)
async def get_pin_by_id(user_id: user_id, id: int, db: db):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    user_view_pin.delay(user_id, id)

    return pin


@router.get("/user_created_pins/{id}", response_model=list[PinOut])
async def get_user_created_pins(id: int, user_id: user_id, db: db, filter: filter):
    user = await db.scalar(select(UsersOrm).where(UsersOrm.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    pins = await db.scalars(
        select(PinsOrm)
        .where(PinsOrm.user_id == id)
        .offset(filter.offset)
        .limit(filter.limit)
        .order_by(desc(PinsOrm.id))
    )
    return pins


@router.post("/user_saved_pins/{pin_id}", status_code=status.HTTP_201_CREATED)
async def user_save_pin(pin_id: int, user_id: user_id, db: db):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    query = select(users_pins).where(users_pins.c.user_id == user_id, users_pins.c.pin_id == pin_id)
    result = await db.execute(query)
    user_pin = result.fetchone()

    if user_pin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already saved this pin"
        )

    await db.execute(insert(users_pins).values(user_id=user_id, pin_id=pin_id))
    await db.commit()

    if pin.user_id != user_id:
        make_update_save_pin.delay(pin.user_id, user_id, pin_id, "Profile")

    return {"status", "ok"}


@router.delete("/user_saved_pins/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete_saved_pin(pin_id: int, user_id: user_id, db: db):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    await db.execute(
        delete(users_pins).where(users_pins.c.user_id == user_id, users_pins.c.pin_id == pin_id)
    )
    await db.commit()
    return {"status", "ok"}


@router.get("/user_saved_pins/{id}", response_model=list[PinOut])
async def get_user_saved_pins(id: int, user_id: user_id, db: db, filter: filter):
    user = await db.scalar(select(UsersOrm).where(UsersOrm.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    result = await db.execute(
        select(users_pins)
        .where(users_pins.c.user_id == id)
        .offset(filter.offset)
        .limit(filter.limit)
    )
    rows = result.all()
    pins = []
    for row in rows:
        pin_id = row[1]
        pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
        pins.append(pin)
    return pins


@router.get("/user_liked_pins/{id}", response_model=list[PinOut])
async def get_user_liked_pins(id: int, user_id: user_id, db: db, filter: filter):
    user = await db.scalar(select(UsersOrm).where(UsersOrm.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    result = await db.execute(
        select(PinsOrm)
        .join(LikesOrm, PinsOrm.id == LikesOrm.pin_id)
        .where(LikesOrm.user_id == id)
        .offset(filter.offset)
        .limit(filter.limit)
    )
    pins = result.scalars().all()

    return pins
