#!/usr/bin/env python3
"""Convert pixel-art PNG to pixel-grid SVG via target-size downsampling.

Resamples the source PNG to an N x N grid using nearest-neighbor (preserves
pixel-art look), then emits one <rect> per non-background cell. Output SVG
uses `shape-rendering="crispEdges"` and groups same-color rects for compactness.

Usage:
    python3 scripts/png_to_svg_pixels.py SRC.png \\
        --output OUT.svg \\
        --target-size N \\
        [--silhouette-color #000000] \\
        [--background-threshold 240]

Consumers control rendered size via SVG width/height attributes; viewBox is
the native cell grid (0 0 N N).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

from PIL import Image


RGBA = tuple[int, int, int, int]


def _to_rgba(px: object) -> RGBA:
    """Coerce a Pillow getpixel result to a 4-tuple RGBA."""
    if isinstance(px, tuple):
        if len(px) == 4:
            return cast(RGBA, px)
        if len(px) == 3:
            r, g, b = cast(tuple[int, int, int], px)
            return (r, g, b, 255)
        if len(px) == 2:
            l, a = cast(tuple[int, int], px)
            return (l, l, l, a)
    if isinstance(px, int):
        return (px, px, px, 255)
    raise ValueError(f"unsupported pixel value: {px!r}")


def _is_background(color: RGBA, threshold: int) -> bool:
    """White / near-white = background. Average RGB >= threshold."""
    r, g, b, a = color
    if a == 0:
        return True
    return (r + g + b) >= 3 * threshold


def png_to_svg(
    src_path: Path,
    out_path: Path,
    target_size: int,
    silhouette_color: str | None,
    background_threshold: int,
) -> dict:
    im = Image.open(src_path).convert("RGBA")
    width, height = im.size

    long_edge = max(width, height)
    scale = target_size / long_edge
    new_w = max(1, round(width * scale))
    new_h = max(1, round(height * scale))
    im = im.resize((new_w, new_h), Image.Resampling.NEAREST)

    rects: list[tuple[int, int, str]] = []
    for y in range(new_h):
        for x in range(new_w):
            color = _to_rgba(im.getpixel((x, y)))
            if _is_background(color, background_threshold):
                continue
            r, g, b, _ = color
            fill = silhouette_color if silhouette_color else f"#{r:02x}{g:02x}{b:02x}"
            rects.append((x, y, fill))

    by_color: dict[str, list[tuple[int, int]]] = {}
    for x, y, fill in rects:
        by_color.setdefault(fill, []).append((x, y))

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {new_w} {new_h}" '
        f'shape-rendering="crispEdges">'
    ]
    for fill, cells in by_color.items():
        lines.append(f'  <g fill="{fill}">')
        for x, y in cells:
            lines.append(f'    <rect x="{x}" y="{y}" width="1" height="1"/>')
        lines.append("  </g>")
    lines.append("</svg>")

    out_path.write_text("\n".join(lines) + "\n")

    return {
        "grid_w": new_w,
        "grid_h": new_h,
        "rects": len(rects),
        "colors": len(by_color),
        "output_size_bytes": out_path.stat().st_size,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Convert pixel-art PNG to pixel-grid SVG via target-size downsampling.",
    )
    ap.add_argument("src", type=Path, help="source PNG path")
    ap.add_argument("--output", "-o", type=Path, required=True, help="output SVG path")
    ap.add_argument(
        "--target-size",
        type=int,
        required=True,
        help="downsample longer edge to this many cells (e.g. 64, 128)",
    )
    ap.add_argument(
        "--silhouette-color",
        type=str,
        default=None,
        help="force foreground pixels to this color (e.g. '#000000')",
    )
    ap.add_argument(
        "--background-threshold",
        type=int,
        default=240,
        help="RGB threshold for background detection (avg(R,G,B) >= threshold)",
    )
    args = ap.parse_args()

    if not args.src.exists():
        print(f"error: source not found: {args.src}", file=sys.stderr)
        return 2
    if args.target_size < 4:
        print("error: --target-size must be >= 4", file=sys.stderr)
        return 2

    stats = png_to_svg(
        args.src,
        args.output,
        args.target_size,
        args.silhouette_color,
        args.background_threshold,
    )
    print(
        f"wrote {args.output}: "
        f"grid {stats['grid_w']}x{stats['grid_h']}, "
        f"{stats['rects']} rects across {stats['colors']} colors, "
        f"{stats['output_size_bytes']:,} bytes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
