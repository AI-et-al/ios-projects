#!/usr/bin/env python3
"""Build "33" — an original small Widgy widget, authored from scratch.

A fork of ideas: DeSolarised's structure (dark card, big now-temp + big
icon, next-hours strip) x Weather Line's information density (city, hi/lo,
condition, hour labels), rendered with this repo's assets: 3dweather hero
icon via Weather (Custom Images) slots, live hourly icons via the Supabase
Web URL service, Numans type. Near-solid dark background — no frosted glass.

Schema knowledge (all verified against real exports):
- document skeleton from the "Ithon" reference export
- b=x, c=y, d=width, e=height; values are {"a":[{"a":v,"b":STATE}],"b":0}
- layer array is TOP-first
- text layer: z:"1", layer font key "1", fields in "66" (34=font, 25=text,
  5=data source, 6=field, 10=JS); image: z:"5", source name in "1"
  ("Weather (Custom Images)" mode in "2" / "Web URL" URL in "2");
  shape: z:"2", fill in "g"; tap: z:"11", action in "4a"

Usage: python3 build_33.py
"""
import json
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIST = HERE.parent / "dist"

FONT = "Numans-Regular"
STATE = 646  # single-state widget; constant id, as in the Ithon export
SERVICE = "https://cusyejearwlwbqeabspa.supabase.co/functions/v1/icon?offset={o}"
HERO_SHA = "a7f767282ec54cd8a489f66e1c0f7b222185d645"
HERO_BASE = ("https://raw.githubusercontent.com/AI-et-al/ios-projects/"
             f"{HERO_SHA}/widgy/weather-widget/icons/hero/{{c}}.png")

SLOTS = {  # Dark Sky enum order, same hypothesis as Simpl.weather 3D
    "f3": "clear-day", "g3": "clear-night", "h3": "rain", "i3": "snow",
    "j3": "sleet", "k3": "wind", "l3": "fog", "m3": "cloudy",
    "n3": "partly-cloudy-day", "o3": "partly-cloudy-night", "p3": "hail",
    "q3": "thunderstorm", "r3": "tornado",
}

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
    return L


def t(s):  # custom text field
    return {"5": "Custom Text", "6": "Text", "25": s}


def wnow(field):  # Weather (Now) field
    return {"5": "Weather (Now)", "6": field}


def main():
    hour_js = ("var main = function() {\n    today = new Date();\n"
               "    today.setHours(today.getHours() + {N});\n"
               "    return today.toLocaleString([], {hour: 'numeric'});\n}")

    layers = [
        # topmost: tap-through to the Weather app
        {"z": "11", "d0": next(_d0), "4a": "openURL_weather://",
         **frame(0, 0, 1600, 1600)},
        # header block, left
        text(70, 105, 620, 85, [{"5": "Location", "6": "City"}],
             "uicol_white-50", "City"),
        text(30, 195, 800, 330,
             [wnow("Temperature (Always In F°)"), t("°")], name="Temp now"),
        text(70, 560, 660, 95,
             [t("↑"), wnow("Max. Temperature Today"), t("°  "),
              t("↓"), wnow("Min. Temperature Today"), t("°")],
             "uicol_white-50", "Hi-Lo"),
        text(70, 668, 660, 95, [wnow("Status (Simple)")],
             "uicol_white-50", "Condition"),
        # hero: current-condition 3D icon, top right
        {"z": "5", "d0": next(_d0), "s": "Hero",
         "1": "Weather (Custom Images)", "2": "Symbol",
         **frame(890, 140, 570, 570)},
        # next-hours strip
        text(90, 875, 520, 70, [t("NEXT HOURS")], "uicol_white-50", "Strip label"),
    ]
    for i, cx in enumerate((350, 800, 1250), start=1):
        layers += [
            {"z": "5", "d0": next(_d0), "s": f"+{i}h icon",
             "1": "Web URL", "2": SERVICE.format(o=f"{i}h"),
             **frame(cx - 135, 985, 270, 270)},
            text(cx - 160, 1275, 320, 75,
                 [{"5": "Javascript", "6": "Script",
                   "10": hour_js.replace("{N}", str(i))}],
                 "uicol_white-50", f"+{i}h hour"),
            text(cx - 170, 1360, 340, 115,
                 [{"5": "Weather (Hourly)",
                   "6": f"+{i}h - Temperature (Always In F°)"}, t("°")],
                 name=f"+{i}h temp"),
        ]
    layers += [
        # near-solid dark card; wallpaper whispers through
        {"z": "2", "d0": next(_d0), "s": "Card", "g": "uicol_black-85",
         "f0": V(10), **frame(0, 0, 1600, 1600)},
        # bottommost: wallpaper slice
        {"z": "5", "d0": next(_d0), "1": "Transparent Background",
         **frame(0, 0, 1600, 1600)},
    ]

    doc = {
        "3": "33",
        "4": ("Now + next 3 hours. A fork of ideas from DeSolarised "
              "(Zooropalg) and Weather Line (PC), with the 3dweather icon "
              "set, Numans, and live per-hour icons."),
        "5": "AI et al.",
        "1": layers,
        "0": 27, "6": 2, "9": 33, "10": True, "20": False, "21": False,
        "29": True, "a2": len(layers),
        "l2": "", "m2": "", "n2": "", "o2": "", "p2": "", "q2": "", "zzz": "",
    }
    doc.update({slot: HERO_BASE.format(c=cond) for slot, cond in SLOTS.items()})

    DIST.mkdir(exist_ok=True)
    payload = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode()
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    out = DIST / "33.widgy"
    out.write_bytes(comp.compress(payload) + comp.flush())
    (DIST / "33.debug.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    back = json.loads(zlib.decompress(out.read_bytes(), -15))
    assert back == doc, "round-trip mismatch"
    print(f"33: {len(layers)} layers, {out.stat().st_size} bytes "
          f"(json {len(payload)}), round-trip OK")


if __name__ == "__main__":
    main()
