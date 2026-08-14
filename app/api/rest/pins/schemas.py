from datetime import datetime

from pydantic import BaseModel


class PinOut(BaseModel):
    id: int
    user_id: int
    title: str | None = None
    description: str | None = None
    href: str | None = None
    image: str | None = None
    rgb: str | None = None
    height: str | None = None
    created_at: datetime | None = None
    original_image: str | None = None
    videoPreview: str | None = None

    class Config:
        from_attributes = True


class PinIn(BaseModel):
    title: str | None = None
    description: str | None = None
    href: str | None = None
    height: str | None = None


class OriginalUrlOut(BaseModel):
    url: str
    expires_in: int


class FilterParams(BaseModel):
    offset: int = 0
    limit: int = 10


class FilterWithValue(FilterParams):
    value: str


class FeedMetaIn(BaseModel):
    pin_ids: list[int]


class FeedMetaOut(BaseModel):
    pin_id: int
    username: str | None = None
    likes_count: int = 0
    liked: bool = False
    comments_count: int = 0
