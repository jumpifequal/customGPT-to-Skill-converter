#!/usr/bin/env python3
"""
Purpose: Normalize a user-supplied icon into Skill-safe icon.png and self-contained icon.svg assets.
When used: Run during GPT-to-Skill conversion whenever an icon is supplied or an existing icon needs normalization.
Why it exists: Skill UI metadata requires stable local icon paths, and raster inputs need a self-contained SVG form.
Inputs/parameters: Source PNG/JPEG/WEBP/SVG path and output directory.
Outputs: icon.png (64x64) and icon.svg (64x64 square; raster sources embedded as base64 PNG).
High-level behaviour: Validate the source, preserve aspect ratio with cover-style square reframing and centered crop,
reject unsafe SVG constructs/references, render square assets without letterbox/pillarbox bands, and write outputs atomically.
Failure semantics: Unsupported formats, unsafe SVG, unavailable raster dependencies, corrupt images, or write failures
produce a clear error and non-zero exit; partial success is removed.
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

UNSAFE_TAGS = {"script", "foreignObject"}
UNSAFE_ATTR_PREFIXES = ("on",)
REMOTE_SCHEMES = ("http://", "https://", "javascript:", "data:text/html")
XLINK = "{http://www.w3.org/1999/xlink}href"


def fail(message: str) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def validate_svg(text: str) -> ET.Element:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        fail(f"invalid SVG XML: {exc}")
    if local_name(root.tag) != "svg":
        fail("root element is not svg")
    for elem in root.iter():
        if local_name(elem.tag) in UNSAFE_TAGS:
            fail(f"unsafe SVG element: {local_name(elem.tag)}")
        for key, value in elem.attrib.items():
            name = local_name(key).lower()
            value_l = str(value).strip().lower()
            if name.startswith(UNSAFE_ATTR_PREFIXES):
                fail(f"unsafe SVG event attribute: {name}")
            if name in {"href"} or key == XLINK:
                if value_l.startswith(REMOTE_SCHEMES):
                    fail("external or executable SVG reference is not allowed")
            if "url(" in value_l and ("http://" in value_l or "https://" in value_l):
                fail("remote SVG resource is not allowed")
    return root


def render_svg_to_png(svg_path: Path, out_png: Path) -> None:
    try:
        import cairosvg  # type: ignore
    except Exception:
        fail("SVG to PNG conversion requires cairosvg in this runtime")
    try:
        # Render at the SVG's intrinsic aspect ratio first. Square reframing happens
        # afterwards in fit_raster so non-square SVGs are not stretched or letterboxed.
        cairosvg.svg2png(url=str(svg_path), write_to=str(out_png))
    except Exception as exc:
        fail(f"cannot render SVG to PNG: {exc}")


def fit_raster(source: Path, out_png: Path, icon_size: int = 64) -> bytes:
    try:
        from PIL import Image, ImageOps  # type: ignore
    except Exception:
        fail("raster icon conversion requires Pillow in this runtime")
    try:
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image).convert("RGBA")
            if image.width < 1 or image.height < 1:
                fail("source icon has invalid dimensions")

            # Reframe with a CSS-cover equivalent: scale until both square dimensions
            # are filled, then crop the overflow. This avoids top/bottom or side bands.
            scale = max(icon_size / image.width, icon_size / image.height)
            resized_width = max(icon_size, round(image.width * scale))
            resized_height = max(icon_size, round(image.height * scale))
            image = image.resize((resized_width, resized_height), Image.Resampling.LANCZOS)

            # Prefer the visible foreground center when alpha is informative; otherwise
            # use the geometric center. Clamp the crop so it always remains in-bounds.
            alpha = image.getchannel("A")
            bbox = alpha.getbbox()
            if bbox and bbox != (0, 0, resized_width, resized_height):
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
            else:
                center_x = resized_width / 2
                center_y = resized_height / 2

            left = round(center_x - icon_size / 2)
            top = round(center_y - icon_size / 2)
            left = max(0, min(left, resized_width - icon_size))
            top = max(0, min(top, resized_height - icon_size))
            framed = image.crop((left, top, left + icon_size, top + icon_size))

            framed.save(out_png, format="PNG")
            buf = io.BytesIO()
            framed.save(buf, format="PNG")
            return buf.getvalue()
    except SystemExit:
        raise
    except Exception as exc:
        fail(f"cannot decode raster icon: {exc}")


def png_to_embedded_svg(preview_png: bytes) -> str:
    payload = base64.b64encode(preview_png).decode("ascii")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" '
        'viewBox="0 0 64 64" preserveAspectRatio="xMidYMid meet">'
        f'<image width="64" height="64" href="data:image/png;base64,{payload}"/>'
        "</svg>"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize a Skill icon.")
    parser.add_argument("source", help="PNG, JPEG, WEBP, or SVG source icon.")
    parser.add_argument("output_dir", help="Directory that will receive icon.png and icon.svg.")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output_dir = Path(args.output_dir).resolve()
    if not source.is_file():
        fail(f"source icon not found: {source}")
    if source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
        fail("supported icon formats are PNG, JPEG, WEBP, and SVG")

    output_dir.mkdir(parents=True, exist_ok=True)
    final_png = output_dir / "icon.png"
    final_svg = output_dir / "icon.svg"

    with tempfile.TemporaryDirectory(dir=output_dir) as temp_dir:
        temp = Path(temp_dir)
        tmp_png = temp / "icon.png"
        tmp_svg = temp / "icon.svg"

        if source.suffix.lower() == ".svg":
            text = source.read_text(encoding="utf-8")
            validate_svg(text)
            tmp_svg.write_text(text, encoding="utf-8")
            render_svg_to_png(tmp_svg, tmp_png)
            # Normalize raster dimensions and create a safe embedded SVG for deterministic small-size rendering.
            preview = fit_raster(tmp_png, tmp_png)
            tmp_svg.write_text(png_to_embedded_svg(preview), encoding="utf-8")
        else:
            preview = fit_raster(source, tmp_png)
            tmp_svg.write_text(png_to_embedded_svg(preview), encoding="utf-8")

        validate_svg(tmp_svg.read_text(encoding="utf-8"))
        os.replace(tmp_png, final_png)
        os.replace(tmp_svg, final_svg)

    print(f"WROTE: {final_png}")
    print(f"WROTE: {final_svg}")


if __name__ == "__main__":
    main()
