#!/usr/bin/env python3
"""Build "Weather Line 3D" v3 — synthesis of three references:

- iWeather 2 (Chad Widgy Prouducer): full-bleed photo background (Web URL
  image layer), location pin + city mark, clean minimal composition
- Weather Line (PC): three hourly columns on a staircase with an hour axis
- DeSolarised (Zooropalg): big-temp presence, icon-forward ratios

Big type throughout (owner mandate: fonts bigger than before), Numans,
plain Temperature fields + custom degree (clean units, per the iWeather 2
recipe), live per-hour 3D icons via the Supabase Web URL service.

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
# iWeather 2's hosted night-sky photo (widgy CDN, proven to load on device).
# Swap for a repo-hosted image any time.
BG_URL = ("https://widgy.fra1.digitaloceanspaces.com/images/"
          "0mWssaHECXOsMzxR7cIWpxWRxVC6AK4EnT03FiA5.heic")

COL_X = (300, 800, 1300)      # three columns on the line
TEMP_Y = (650, 760, 870)      # staircase: static downward stagger
ICON = 290                     # column icon edge
COL_TEMP_H = 170               # column temp text height (was 150)
NOW_TEMP_H = 400               # big now-temp height (was 300)

_d0 = iter(range(1, 200))


def V(v):
    return {"a": [{"a": v, "b": STATE}], "b": 0}


def frame(x, y, w, h):
    return {"b": V(x), "c": V(y), "d": V(w), "e": V(h)}


def text(x, y, w, h, fields, color="uicol_white-100", name=None):
    L = {"z": "1", "d0": next(_d0), "1": FONT, "f": color, **frame(x, y, w, h),
         "66": [{"34": FONT, **f} for f in fields]}
    if name:
        L["s"] = name
    return L  # plain Temperature fields + custom ° = clean units


def t(s):
    return {"5": "Custom Text", "6": "Text", "25": s}


def main():
    hour_js = ("var main = function() {\n    today = new Date();\n"
               "    today.setHours(today.getHours() + {N});\n"
               "    return today.toLocaleString([], {hour: 'numeric'});\n}")

    layers = [
        {"z": "11", "d0": next(_d0), "4a": "openURL_weather://",
         **frame(0, 0, 1600, 1600)},
        # big now-temp, top left (DeSolarised presence, bigger than ever)
        text(50, 90, 760, NOW_TEMP_H,
             [{"5": "Weather (Now)", "6": "Temperature"}, t("°")],
             name="Temp now"),
        # iWeather mark: pin + city, top right
        {"z": "4", "d0": next(_d0), "s": "Pin", "3": "location.fill",
         "1": 1, "f": "uicol_white-100", **frame(1120, 135, 85, 95)},
        text(1215, 120, 340, 115, [{"5": "Location", "6": "City"}],
             name="City"),
        # condition under the temp
        text(70, 500, 800, 110,
             [{"5": "Weather (Now)", "6": "Status (Simple)"}],
             "uicol_white-50", "Condition"),
    ]
    # staircase columns: big temp over live icon
    for i, (cx, ty) in enumerate(zip(COL_X, TEMP_Y), start=1):
        layers += [
            text(cx - 190, ty, 380, COL_TEMP_H,
                 [{"5": "Weather (Hourly)", "6": f"+{i}h - Temperature"},
                  t("°")], name=f"+{i}h temp"),
            {"z": "5", "d0": next(_d0), "s": f"+{i}h icon",
             "1": "Web URL", "2": SERVICE.format(o=f"{i}h"),
             **frame(cx - ICON / 2, ty + 180, ICON, ICON)},
        ]
    # hour axis, big
    for i, cx in enumerate(COL_X, start=1):
        layers.append(
            text(cx - 180, 1380, 360, 115,
                 [{"5": "Javascript", "6": "Script",
                   "10": hour_js.replace("{N}", str(i))}],
                 "uicol_white-50", f"+{i}h hour"))
    # full-bleed photo background (iWeather 2 style), bottommost
    layers.append({"z": "5", "d0": next(_d0), "s": "Backdrop",
                   "1": "Web URL", "2": BG_URL,
                   **frame(0, 0, 1600, 1600)})

    doc = {
        "3": "Weather Line 3D",
        "4": ("Big temp, three hours on a staircase, photo backdrop — a "
              "synthesis of Weather Line (PC), iWeather 2 (Chad Widgy "
              "Prouducer), and DeSolarised (Zooropalg), with the 3dweather "
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
    print(f"Weather Line 3D v3: {len(layers)} layers, {out.stat().st_size} "
          f"bytes (json {len(payload)}), round-trip OK")


if __name__ == "__main__":
    main()
