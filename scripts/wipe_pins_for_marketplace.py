"""Wipe all pins (and best-effort media files) for Marketplace clean slate (D10).

Usage (inside fastapi container):
    CONFIRM_WIPE_PINS=YES python scripts/wipe_pins_for_marketplace.py

Does NOT run from Alembic. Use before Sprint1 if old pins conflict with new media pipeline.
"""
from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path

from sqlalchemy import text

from app.config import settings
from app.postgresql.database import async_session_maker


async def wipe() -> None:
    if os.environ.get("CONFIRM_WIPE_PINS") != "YES":
        raise SystemExit(
            "Refusing wipe. Set CONFIRM_WIPE_PINS=YES to delete all pins (+ cascades)."
        )

    media_root = Path(settings.MEDIA_PATH)
    paths: list[str] = []

    async with async_session_maker() as session:
        rows = (
            await session.execute(
                text(
                    'SELECT image, "videoPreview", original_image FROM pins'
                )
            )
        ).all()
        for image, video_preview, original_image in rows:
            for rel in (image, video_preview, original_image):
                if rel:
                    paths.append(rel)

        before = await session.scalar(text("SELECT COUNT(*) FROM pins"))
        await session.execute(text("DELETE FROM pins"))
        await session.commit()
        after = await session.scalar(text("SELECT COUNT(*) FROM pins"))

    removed_files = 0
    for rel in paths:
        full = media_root / rel
        try:
            if full.is_file():
                full.unlink()
                removed_files += 1
        except OSError as exc:
            print(f"warn: could not delete {full}: {exc}")

    # Best-effort clear Sprint1 layout dirs
    for sub in ("pins/original", "pins/preview", "pins"):
        folder = media_root / sub
        if folder.is_dir():
            for child in folder.iterdir():
                try:
                    if child.is_file():
                        child.unlink()
                        removed_files += 1
                    elif child.is_dir() and child.name in {"original", "preview"}:
                        shutil.rmtree(child, ignore_errors=True)
                except OSError as exc:
                    print(f"warn: could not clean {child}: {exc}")

    print(f"pins_before={before} pins_after={after} media_files_removed={removed_files}")


if __name__ == "__main__":
    asyncio.run(wipe())
