#!/usr/bin/env python3
"""Build "33" — an original small Widgy widget, authored from scratch.

v2: restructured to match the owner's hand-built DschubbaLokki reference —
icon-dominant ratios. Top: now-temp, hairline divider, BIG hero icon
(Weather Custom Images). Below: three horizontal rows, each small +Nh
label / large live icon (Web URL service) / temp. Near-solid dark card,
no frosted glass, Numans everywhere.

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
HERO_SHA = "18c0c465d14150b5f12a731d2b20ca96a55027c1"
HERO_BASE = ("https://raw.githubusercontent.com/AI-et-al/ios-projects/"
             f"{HERO_SHA}/widgy/weather-widget/icons/hero/{{c}}.png")

SLOTS = {  # Dark Sky enum order, same hypothesis as Simpl.weather 3D
    "f3": "clear-day", "g3": "clear-night", "h3": "rain", "i3": "snow",
    "j3": "sleet", "k3": "wind", "l3": "fog", "m3": "cloudy",
    "n3": "partly-cloudy-day", "o3": "partly-cloudy-night", "p3": "hail",
    "q3": "thunderstorm", "r3": "tornado",
}

# icon-dominant ratios, after the DschubbaLokki reference
HERO = 640          # hero icon edge; ~1.7x the temp digit height
TEMP_H = 300        # now-temp text height
ROW_ICON = 250      # row icon edge
ROW_LABEL_H = 90    # +Nh label height
ROW_TEMP_H = 130    # row temp height
ROW_CENTERS = (930, 1190, 1450)

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
    return L  # (plain Temperature fields + custom ° = clean units,
    # per the iWeather 2 reference export; no format keys needed)


def t(s):  # custom text field
    return {"5": "Custom Text", "6": "Text", "25": s}


def main():
    layers = [
        # topmost: tap-through to the Weather app
        {"z": "11", "d0": next(_d0), "4a": "openURL_weather://",
         **frame(0, 0, 1600, 1600)},
        # top block: temp | divider | dominant hero
        text(40, 250, 580, TEMP_H,
             [{"5": "Weather (Now)", "6": "Temperature"},
              t("°")], name="Temp now"),
        {"z": "2", "d0": next(_d0), "s": "Divider", "g": "uicol_white-50",
         "f0": V(3), **frame(668, 180, 6, 440)},
        {"z": "5", "d0": next(_d0), "s": "Hero",
         "1": "Weather (Custom Images)", "2": "Symbol",
         **frame(760, 80, HERO, HERO)},
    ]
    for i, cy in enumerate(ROW_CENTERS, start=1):
        layers += [
            text(90, cy - ROW_LABEL_H / 2, 280, ROW_LABEL_H,
                 [t(f"+{i}h")], "uicol_white-50", f"+{i}h label"),
            {"z": "5", "d0": next(_d0), "s": f"+{i}h icon",
             "1": "Web URL", "2": SERVICE.format(o=f"{i}h"),
             **frame(800 - ROW_ICON / 2, cy - ROW_ICON / 2,
                     ROW_ICON, ROW_ICON)},
            text(1140, cy - ROW_TEMP_H / 2, 390, ROW_TEMP_H,
                 [{"5": "Weather (Hourly)",
                   "6": f"+{i}h - Temperature"}, t("°")],
                 name=f"+{i}h temp"),
        ]
    layers += [
        # near-solid dark card; wallpaper whispers through
        {"z": "2", "d0": next(_d0), "s": "Card", "g": "uicol_black-100",
         "f0": V(10), **frame(0, 0, 1600, 1600)},
        # bottommost: wallpaper slice
        {"z": "5", "d0": next(_d0), "1": "Transparent Background",
         **frame(0, 0, 1600, 1600)},
    ]

    doc = {
        "3": "33",
        "4": ("Now + next 3 hours, icon-forward. A fork of ideas from "
              "DeSolarised (Zooropalg), Weather Line (PC), and "
              "DschubbaLokki, with the 3dweather icon set, Numans, and "
              "live per-hour icons."),
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
    print(f"33 v2: {len(layers)} layers, {out.stat().st_size} bytes "
          f"(json {len(payload)}), round-trip OK")


if __name__ == "__main__":
    main()
