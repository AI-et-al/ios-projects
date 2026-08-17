#!/usr/bin/env python3
"""Build the customized Simpl.weather .widgy from the original export.

A .widgy file is raw-deflate-compressed JSON (zlib, no header). This
script applies two changes to the original:

1. Weather (Custom Images) slots: the top-level ``*3`` URL keys are
   repointed at this repo's prepped icons via commit-pinned
   raw.githubusercontent.com URLs (the repo is public; Widgy downloads
   images on import, exactly as it does for widgy.app-hosted shares).
   Slot -> condition comes from slot-map.json.
2. Fonts: every "System Bold" (text-layer key "1" and data-field key
   "34") becomes "Numans-Regular". Widgy falls back to the system font
   until Numans is installed on-device (fonts/Numans-Regular.ttf).

The two Weather (Custom Images) layers are also rescaled: the original
orb artwork filled a 1400-unit box on the 1600-unit canvas (ambient
backdrop); a literal 3D icon at that size dominates the card. ICON_SCALE
shrinks the box around its own center (top-left-origin coordinates, so
position shifts by old_size*(1-s)/2). Tune and rebuild to taste.

Usage: python3 build_widgy.py <commit-sha> [icon-scale]
"""
import json
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
WW = HERE.parent
ORIGINAL = WW / "original" / "simpl-weather.widgy.json"
DIST = WW / "dist"

FONT_OLD, FONT_NEW = "System Bold", "Numans-Regular"
NAME_NEW = "Simpl.weather 3D"
RAW_BASE = "https://raw.githubusercontent.com/AI-et-al/ios-projects/{sha}/widgy/weather-widget/icons/prepped/{cond}.png"


ICON_SCALE_DEFAULT = 0.62


def scale_icon_layers(layers, s, counts):
    """Shrink Weather (Custom Images) layers around their own center."""
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        if layer.get("z") == "5" and layer.get("1") == "Weather (Custom Images)":
            for pos_key, size_key in (("c", "d"), ("b", "e")):
                size_entries = (layer.get(size_key) or {}).get("a") or []
                pos_entries = (layer.get(pos_key) or {}).get("a") or []
                if not size_entries:
                    continue
                old = size_entries[0]["a"]
                shift = old * (1 - s) / 2
                for entry in size_entries:
                    entry["a"] = entry["a"] * s
                for entry in pos_entries:
                    entry["a"] = entry["a"] + shift
            counts["icon-layers"] += 1
        kids = layer.get("1")
        if isinstance(kids, list):
            scale_icon_layers(kids, s, counts)


def swap_fonts(layers, counts):
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        if layer.get("z") == "1" and layer.get("1") == FONT_OLD:
            layer["1"] = FONT_NEW
            counts["layer-font"] += 1
        for field in layer.get("66", []):
            if isinstance(field, dict) and field.get("34") == FONT_OLD:
                field["34"] = FONT_NEW
                counts["field-font"] += 1
        kids = layer.get("1")
        if isinstance(kids, list):
            swap_fonts(kids, counts)


def main():
    if len(sys.argv) < 2 or len(sys.argv[1]) < 7:
        sys.exit("usage: build_widgy.py <commit-sha of the prepped icons> [icon-scale]")
    sha = sys.argv[1]
    scale = float(sys.argv[2]) if len(sys.argv) > 2 else ICON_SCALE_DEFAULT

    doc = json.loads(ORIGINAL.read_text())
    slot_map = {k: v for k, v in json.loads((HERE / "slot-map.json").read_text()).items()
                if not k.startswith("_")}

    counts = {"layer-font": 0, "field-font": 0, "slots": 0, "icon-layers": 0}
    swap_fonts(doc["1"], counts)
    scale_icon_layers(doc["1"], scale, counts)

    for slot, cond in slot_map.items():
        if cond is None:
            continue
        icon = WW / "icons" / "prepped" / f"{cond}.png"
        if not icon.exists():
            sys.exit(f"missing prepped icon for {cond}")
        doc[slot] = RAW_BASE.format(sha=sha, cond=cond)
        counts["slots"] += 1

    doc["3"] = NAME_NEW

    DIST.mkdir(exist_ok=True)
    payload = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode()
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    blob = comp.compress(payload) + comp.flush()
    out = DIST / "simpl-weather-3d.widgy"
    out.write_bytes(blob)
    (DIST / "simpl-weather-3d.debug.json").write_text(
        json.dumps(doc, indent=1, ensure_ascii=False))

    # round-trip validation
    back = json.loads(zlib.decompress(out.read_bytes(), -15))
    assert back == doc, "round-trip mismatch"
    print(f"fonts swapped: {counts['layer-font']} layer + {counts['field-font']} field")
    print(f"image slots repointed: {counts['slots']} (pinned to {sha[:12]})")
    print(f"icon layers rescaled: {counts['icon-layers']} at scale {scale}")
    print(f"wrote {out.name}: {out.stat().st_size} bytes "
          f"(json {len(payload)} bytes), round-trip OK")


if __name__ == "__main__":
    main()
