"""Static watermark helpers for Marketplace Sprint1 preview generation."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.config import settings


VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".mkv"}


def media_root() -> Path:
    return Path(settings.MEDIA_PATH)


def original_dir() -> Path:
    path = media_root() / "pins" / "original"
    path.mkdir(parents=True, exist_ok=True)
    return path


def preview_dir() -> Path:
    path = media_root() / "pins" / "preview"
    path.mkdir(parents=True, exist_ok=True)
    return path


def watermark_asset_path() -> Path:
    # Prefer repo assets; fall back under MEDIA_PATH
    candidates = [
        Path("/fastapi/assets/watermark.png"),
        Path(__file__).resolve().parents[4] / "assets" / "watermark.png",
        media_root() / "assets" / "watermark.png",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    # Generate placeholder
    out = Path("/fastapi/assets/watermark.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (320, 80), (0, 0, 0, 0))
    # Simple translucent bar as watermark mark
    bar = Image.new("RGBA", (320, 80), (255, 255, 255, 110))
    img.paste(bar, (0, 0), bar)
    img.save(out, format="PNG")
    return out


def is_video_path(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def apply_watermark(src: Path, dest: Path) -> None:
    base = Image.open(src).convert("RGBA")
    mark = Image.open(watermark_asset_path()).convert("RGBA")

    # Scale watermark to ~35% of base width
    target_w = max(64, int(base.width * 0.35))
    ratio = target_w / mark.width
    target_h = max(24, int(mark.height * ratio))
    mark = mark.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Bottom-right with margin
    margin = max(8, int(base.width * 0.03))
    x = base.width - mark.width - margin
    y = base.height - mark.height - margin

    layered = base.copy()
    layered.alpha_composite(mark, (x, y))
    rgb = layered.convert("RGB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(dest, format="JPEG", quality=88)
