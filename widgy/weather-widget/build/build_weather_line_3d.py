#!/usr/bin/env python3
"""Build "Weather Line 3D" — a from-scratch small Widgy widget after PC's
Weather Line: city + condition header, hi/lo top-right, four hourly columns
stepping down a static staircase (temp over live 3D icon via the Web URL
service), an hour-axis band, and a feels-like footer. Dark card, no frost,
Numans, 3dweather icons. Companion to "33" (build_33.py), same schema notes.

Usage: python3 build_weather_line_3d.py
"""
import json
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIST = HERE.parent / "dist"

FONT = "Numans-Regular"
STATE = 646
SERVICE = "https://cusyejearwlwbqeabspa.supabase.co/functions/v1/icon?offset={o}"

COL_X = (230, 610, 990, 1370)    # column centers
TEMP_Y = (300, 420, 540, 660)    # staircase: static downward stagger
ICON = 300                        # Miniiii-scale: ~3x the temp text height

_d0 = iter(range(1, 200))


def V(v):
    return {"a": [{"a": v, "b": STATE}], "b": 0}


def frame(x, y, w, h):
    return {"b": V(x), "c": V(y), "d": V(w), "e": V(h)}


def text(x, y, w, h, fields, color="uicol_white-100", name=None, fmt=None):
    L = {"z": "1", "d0": next(_d0), "1": FONT, "f": color, **frame(x, y, w, h),
         "66": [{"34": FONT, **f} for f in fields]}
    if name:
        L["s"] = name
    if fmt is not None:  # number-format key from the original export;
        L["8"] = V(fmt)  # suppresses the unit suffix (no more 107°F°)
    return L


def t(s):
    return {"5": "Custom Text", "6": "Text", "25": s}


def wnow(field):
    return {"5": "Weather (Now)", "6": field}


def main():
    hour_js = ("var main = function() {\n    today = new Date();\n"
               "    today.setHours(today.getHours() + {N});\n"
               "    return today.toLocaleString([], {hour: 'numeric'});\n}")

    layers = [
        {"z": "11", "d0": next(_d0), "4a": "openURL_weather://",
         **frame(0, 0, 1600, 1600)},
        # header
        text(70, 85, 760, 100, [{"5": "Location", "6": "City"}], name="City"),
        text(70, 195, 860, 85, [wnow("Status (Simple)")],
             "uicol_white-50", "Condition"),
        text(1000, 95, 530, 85,
             [t("↑"), wnow("Max. Temperature Today"), t("°  "),
              t("↓"), wnow("Min. Temperature Today"), t("°")],
             "uicol_white-50", "Hi-Lo", fmt=2),
    ]
    # staircase columns: temp over live icon
    for i, (cx, ty) in enumerate(zip(COL_X, TEMP_Y), start=1):
        layers += [
            text(cx - 160, ty, 320, 95,
                 [{"5": "Weather (Hourly)",
                   "6": f"+{i}h - Temperature (Always In F°)"}, t("°")],
                 name=f"+{i}h temp", fmt=2),
            {"z": "5", "d0": next(_d0), "s": f"+{i}h icon",
             "1": "Web URL", "2": SERVICE.format(o=f"{i}h"),
             **frame(cx - ICON / 2, ty + 105, ICON, ICON)},
        ]
    # hour labels straight on the card (dark Weather Line style)
    for i, cx in enumerate(COL_X, start=1):
        layers.append(
            text(cx - 150, 1130, 300, 75,
                 [{"5": "Javascript", "6": "Script",
                   "10": hour_js.replace("{N}", str(i))}],
                 "uicol_white-50", f"+{i}h hour"))
    layers += [
        text(150, 1265, 1300, 85,
             [t("Feels like "), wnow("Feels Like Temperature (Always In F°)"),
              t("°")], "uicol_white-50", "Footer", fmt=2),
        {"z": "2", "d0": next(_d0), "s": "Card", "g": "uicol_black-100",
         "f0": V(10), **frame(0, 0, 1600, 1600)},
        {"z": "5", "d0": next(_d0), "1": "Transparent Background",
         **frame(0, 0, 1600, 1600)},
    ]

    doc = {
        "3": "Weather Line 3D",
        "4": ("City, hi/lo, and the next four hours on a staircase — a "
              "from-scratch remake of PC's Weather Line with the 3dweather "
              "icon set, Numans, and live per-hour icons."),
        "5": "AI et al.",
        "1": layers,
        "0": 27, "6": 2, "9": 33, "10": True, "20": False, "21": False,
        "29": True, "a2": len(layers),
        "l2": "", "m2": "", "n2": "", "o2": "", "p2": "", "q2": "", "zzz": "",
    }

    DIST.mkdir(exist_ok=True)
    payload = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode()
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    out = DIST / "weather-line-3d.widgy"
    out.write_bytes(comp.compress(payload) + comp.flush())
    (DIST / "weather-line-3d.debug.json").write_text(
        json.dumps(doc, indent=1, ensure_ascii=False))
    back = json.loads(zlib.decompress(out.read_bytes(), -15))
    assert back == doc, "round-trip mismatch"
    print(f"Weather Line 3D: {len(layers)} layers, {out.stat().st_size} bytes "
          f"(json {len(payload)}), round-trip OK")


if __name__ == "__main__":
    main()
