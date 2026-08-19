#!/usr/bin/env python3
"""Prepare the curated 3dweather icons for the Widgy weather widget.

Only 12 of the 45 pack icons are genuinely transparent; the rest have a
baked-in near-opaque white card (see icons/README.md). Picks below use
clean sources wherever possible. Three derivations handle the gaps:

- cloudy:  frosted 1069 with the sun erased (no bare-cloud icon in pack)
- rain:    1096 with the sun erased (no neutral day/night rain in pack)
- fog/wind: 1085/1094 de-hazed — the white card is removed by keying
  alpha off saturation/whiteness, safe because their content is beige
  with grey shadows and contains no white elements.

Run from anywhere: paths are resolved relative to this file.
"""
from pathlib import Path
from PIL import Image
import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "icons" / "src"
OUT = HERE.parent / "icons" / "prepped"
HERO = HERE.parent / "icons" / "hero"
OUT_SIZE = 400
MARGIN = 0.06  # fraction of the square edge
# Hero variants fill the widget's 1400-unit custom-image box like the
# original orb did: content-tight, no optical normalization.
HERO_SIZE = 480
HERO_MARGIN = 0.02

# condition -> (source id, treatment), per icons/README.md curation
# (frosted-first, transparency-clean sources only).
PICKS = {
    "clear-day": ("1000031068", None),
    "clear-night": ("1000031075", None),
    "rain": ("1000031096", "erase_sun"),
    "snow": ("1000031097", None),
    "sleet": ("1000031087", None),               # frosted
    "wind": ("1000031094", "dehaze"),
    "fog": ("1000031085", "dehaze"),
    "cloudy": ("1000031096", "bare_cloud"),      # solid cloud, derived
    "partly-cloudy-day": ("1000031069", None),   # frosted
    "partly-cloudy-night": ("1000031112", None),
    "hail": ("1000031092", None),
    "thunderstorm": ("1000031080", None),        # frosted
    "tornado": ("1000031088", None),
}


def trim_pad_resize(im: Image.Image, margin: float = MARGIN,
                    size: int = OUT_SIZE) -> Image.Image:
    im = im.convert("RGBA")
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.where(a > 8)
    if len(xs):
        im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    edge = int(max(im.size) * (1 + 2 * margin))
    sq = Image.new("RGBA", (edge, edge), (0, 0, 0, 0))
    sq.paste(im, ((edge - im.width) // 2, (edge - im.height) // 2), im)
    return sq.resize((size, size), Image.LANCZOS)


def erase_sun(im: Image.Image) -> Image.Image:
    """Remove warm-hue (sun) pixels; neutralise warm tint bleeding
    through translucent cloud areas."""
    px = np.asarray(im.convert("RGBA")).astype(int)
    r, g, b, a = px[..., 0], px[..., 1], px[..., 2], px[..., 3]
    warm = (r - b > 25) & (r > 120)
    strong = warm & (r - b > 60)
    a[strong] = 0
    tint = warm & ~strong
    grey = (r + g + b) // 3
    for c in range(3):
        px[..., c][tint] = grey[tint]
    px[..., 3] = a
    return Image.fromarray(px.astype("uint8"), "RGBA")


def bare_cloud(im: Image.Image) -> Image.Image:
    """Erase both the sun (warm hues) and the raindrops (cool blues),
    leaving a bare opaque white cloud — reads clearly at row size where
    the frosted derivative looked like a flat grey glyph."""
    px = np.asarray(erase_sun(im).convert("RGBA")).astype(int)
    r, g, b, a = px[..., 0], px[..., 1], px[..., 2], px[..., 3]
    blue = (b - r > 25) & (b > 110)
    a[blue] = 0
    px[..., 3] = a
    return Image.fromarray(px.astype("uint8"), "RGBA")


def dehaze(im: Image.Image) -> Image.Image:
    """Remove the baked white card: keep saturated (beige) content and
    darker grey shadows, fade pure-white low-saturation pixels out."""
    px = np.asarray(im.convert("RGBA")).astype(float)
    r, g, b, a = px[..., 0], px[..., 1], px[..., 2], px[..., 3]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / 255.0
    whiteness = mn / 255.0
    keep = np.clip(np.maximum(sat * 8.0, (1.0 - whiteness) * 4.0), 0.0, 1.0)
    px[..., 3] = a * keep
    return Image.fromarray(px.astype("uint8"), "RGBA")


TREATMENTS = {"erase_sun": erase_sun, "dehaze": dehaze,
              "bare_cloud": bare_cloud, None: lambda im: im}


def optical_normalize(images: dict) -> dict:
    """Equalise perceived size: a solid disc (sun) reads much bigger than
    an irregular cloud at the same geometric size. Scale each icon's
    content so its alpha mass (sqrt of total alpha) matches the median,
    clamped so nothing shrinks/grows absurdly or clips its frame."""
    mass = {c: float(np.sqrt(np.asarray(im)[:, :, 3].astype(float).sum()))
            for c, im in images.items()}
    target = sorted(mass.values())[len(mass) // 2]
    # solid discs still read large even at equal alpha mass; bias them down
    bias = {"clear-day": 0.92, "clear-night": 0.94}
    out = {}
    for cond, im in images.items():
        f = max(0.78, min(1.12, target / mass[cond])) * bias.get(cond, 1.0)
        if abs(f - 1) < 0.03:
            out[cond] = im
            continue
        w = max(1, int(im.width * f))
        scaled = im.resize((w, w), Image.LANCZOS)
        frame = Image.new("RGBA", im.size, (0, 0, 0, 0))
        off = (im.width - w) // 2
        frame.paste(scaled, (off, off), scaled)
        out[cond] = frame
        print(f"  optical: {cond} x{f:.2f}")
    return out


def main():
    for d in (OUT, HERO):
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.png"):
            old.unlink()
    treated = {cond: TREATMENTS[t](Image.open(SRC / f"{src_id}.png"))
               for cond, (src_id, t) in PICKS.items()}

    images = optical_normalize(
        {cond: trim_pad_resize(im) for cond, im in treated.items()})
    for cond, im in images.items():
        src_id, treatment = PICKS[cond]
        path = OUT / f"{cond}.png"
        im.save(path, optimize=True)
        note = f" ({treatment})" if treatment else ""
        print(f"{cond:22s} <- {src_id}{note}  {path.stat().st_size // 1024}KB")

    for cond, im in treated.items():
        hero = trim_pad_resize(im, margin=HERO_MARGIN, size=HERO_SIZE)
        hero.save(HERO / f"{cond}.png", optimize=True)
    print(f"hero variants: {len(treated)} at {HERO_SIZE}px, margin {HERO_MARGIN}")


if __name__ == "__main__":
    main()
