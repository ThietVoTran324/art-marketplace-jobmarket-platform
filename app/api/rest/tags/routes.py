import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import desc, func, insert, select

from app.api.rest.dependencies import db, filter, user_id
from app.api.rest.pins.schemas import PinOut
from app.config import settings
from app.postgresql.models import LikesOrm, PinsOrm, TagsOrm, pins_tags

from .schemas import TagOut, TagsIn

mimetypes.add_type("image/webp", ".webp")

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tags_on_pin(db: db, user_id: user_id, tags_model: TagsIn):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == tags_model.pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    for tag_name in tags_model.tags:
        tag = await db.scalar(select(TagsOrm).where(TagsOrm.name == tag_name))
        if not tag:
            new_tag = await db.scalar(insert(TagsOrm).values(name=tag_name).returning(TagsOrm))
            await db.execute(insert(pins_tags).values(pin_id=pin.id, tag_id=new_tag.id))
            await db.commit()
        else:
            await db.execute(insert(pins_tags).values(pin_id=pin.id, tag_id=tag.id))
            await db.commit()


@router.get("/", response_model=list[TagOut])
async def get_all_tags(db: db, user_id: user_id):
    tags = await db.scalars(select(TagsOrm))
    return tags


@router.get("/tags-with-first-pin", response_model=list[dict])
async def get_tags_with_first_pin(user_id: user_id, db: db):
    result = []

    last_pin_stmt = select(PinsOrm).order_by(desc(PinsOrm.id)).limit(1)
    last_pin_result = await db.execute(last_pin_stmt)
    last_pin = last_pin_result.scalar_one_or_none()

    result.append({"id": 0, "name": "Everything", "pinId": last_pin.id if last_pin else None})

    tags_stmt = select(TagsOrm)
    tags_result = await db.execute(tags_stmt)
    tags = tags_result.scalars().all()

    for tag in tags:
        stmt = (
            select(PinsOrm)
            .join(pins_tags, PinsOrm.id == pins_tags.c.pin_id)
            .where(pins_tags.c.tag_id == tag.id)
            .limit(1)
        )
        pin_result = await db.execute(stmt)
        pin = pin_result.scalar_one_or_none()

        if pin:
            result.append({"id": tag.id, "name": tag.name, "pinId": pin.id})

    return result




@router.get("/tags-with-first-pin/upload/{id}")
async def get_image(user_id: user_id, id: int, db: db):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    media_root = Path(settings.MEDIA_PATH)

    # fallback
    default_image = media_root / "notauth" / "1.jpg"

    # 👉 VIDEO
    if pin.videoPreview:
        video_path = media_root / pin.videoPreview
        if video_path.exists():
            return FileResponse(video_path, media_type="video/mp4")

        return FileResponse(default_image, media_type="image/jpeg")

    # 👉 IMAGE
    if not pin.image:
        return FileResponse(default_image, media_type="image/jpeg")

    image_path = media_root / pin.image
    if not image_path.exists():
        return FileResponse(default_image, media_type="image/jpeg")

    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    return FileResponse(image_path, media_type=mime_type)



@router.get("/search/tags-with-first-pin", response_model=list[dict])
async def get_tags_with_first_pin(user_id: user_id, db: db):
    result = []

    tags_stmt = select(TagsOrm).limit(8)
    tags_result = await db.execute(tags_stmt)
    tags = tags_result.scalars().all()

    for tag in tags:
        stmt = (
            select(PinsOrm)
            .join(pins_tags, PinsOrm.id == pins_tags.c.pin_id)
            .where(pins_tags.c.tag_id == tag.id)
            .limit(1)
        )
        pin_result = await db.execute(stmt)
        pin = pin_result.scalar_one_or_none()

        if pin:
            result.append({"id": tag.id, "name": tag.name, "pinId": pin.id})

    return result


@router.get("/{pin_id}", response_model=list[PinOut])
async def get_related_pins(db: db, user_id: user_id, pin_id: int, filter: filter):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    tag_rows = await db.execute(select(pins_tags.c.tag_id).where(pins_tags.c.pin_id == pin_id))
    tag_ids = [row[0] for row in tag_rows.all()]
    if not tag_ids:
        return []

    likes_subq = (
        select(LikesOrm.pin_id.label("pin_id"), func.count(LikesOrm.id).label("likes_cnt"))
        .where(LikesOrm.pin_id.isnot(None))
        .group_by(LikesOrm.pin_id)
        .subquery()
    )

    overlap_subq = (
        select(
            pins_tags.c.pin_id.label("pin_id"),
            func.count(pins_tags.c.tag_id).label("overlap"),
        )
        .where(pins_tags.c.tag_id.in_(tag_ids))
        .where(pins_tags.c.pin_id != pin_id)
        .group_by(pins_tags.c.pin_id)
        .subquery()
    )

    stmt = (
        select(PinsOrm)
        .join(overlap_subq, PinsOrm.id == overlap_subq.c.pin_id)
        .outerjoin(likes_subq, PinsOrm.id == likes_subq.c.pin_id)
        .order_by(
            desc(overlap_subq.c.overlap),
            desc(func.coalesce(likes_subq.c.likes_cnt, 0)),
            desc(PinsOrm.id),
        )
        .offset(filter.offset)
        .limit(filter.limit)
    )
    related = await db.scalars(stmt)
    return related.all()


@router.get("/pin/tags/{pin_id}", response_model=list[TagOut])
async def get_tags_on_pin(db: db, user_id: user_id, pin_id: int):
    pin = await db.scalar(select(PinsOrm).where(PinsOrm.id == pin_id))
    if pin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pin not found")

    result = await db.execute(select(pins_tags).where(pins_tags.c.pin_id == pin_id))
    rows = result.all()

    tags = []

    for row in rows:
        tag_id = row[1]
        tag = await db.scalar(select(TagsOrm).where(TagsOrm.id == tag_id))
        tags.append(tag)
    return tags
