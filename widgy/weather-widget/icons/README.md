# 3dweather icon pack

45 unique PNGs (RGBA, ~400–700px) in `src/`, keeping their original Android MediaStore names. From the owner's Android days; uploaded 2026-08-16 as `3dweather_.zip` (90 files → 45 after byte-identical `* 2.png` dedupe).

**Transparency warning:** only 12 of the 45 are genuinely transparent — `1068 1069 1075 1078 1080 1087 1088 1092 1096 1097 1098 1101 1102 1105 1112` minus the near-misses; the other ~33 have a baked-in, near-opaque white card behind the artwork (alpha ≈255 edge to edge) and are unusable on transparent widgets without background removal. This is what "some of them look wonky" turned out to be. All four frosted icons are clean.

## Style families

The pack mixes three renderings of the same 3D-clay style:

- **frosted** — translucent glass clouds you can see through: `1069` (sun), `1078` (moon+rain), `1080` (moon+thunder), `1087` (sleet mix)
- **glow** — soft white clouds with a large baked-in halo: `1063–1067`, `1070–1073`, `1075–1082`, `1084`, `1086`
- **solid** — crisp opaque white clouds: `1090–1092`, `1096–1104`, `1107`, `1109–1112`
- **beige/dust** — intentionally tan: `1085`, `1094` (dust/sand + wind lines), `1088`, `1105` (tornado)

**Owner preference: frosted-first.** Use the four frosted icons wherever their condition matches; fill remaining slots from the *glow* family (closest texture match), not the solid family. Solid variants are the fallback for small sizes if frosted/glow read too faint.

## Final picks (build/prep_icons.py; prepped output in `prepped/`)

Simpl.weather has one custom-image slot per Dark Sky condition (no day/night rain split), so neutral sources are preferred for the day/night-agnostic slots. Treatments are applied by `prep_icons.py`.

| Condition | Source | Treatment / notes |
|---|---|---|
| clear-day | `1068` | big sun |
| clear-night | `1075` | glow moon (clean) |
| rain | `1096` | **sun erased** → neutral cloud + drops |
| snow | `1097` | neutral, clean (swapped from white-carded `1084`) |
| sleet | `1087` ★frosted | neutral flakes+drops |
| wind | `1094` | **de-hazed** (white card removed; beige content survives) |
| fog | `1085` | **de-hazed** |
| cloudy | `1069` ★frosted | **sun erased** → derived bare frosted cloud (no such icon in pack) |
| partly-cloudy-day | `1069` ★frosted | |
| partly-cloudy-night | `1112` | big moon wrap (swapped from white-carded `1081`) |
| hail | `1092` | keeps its small sun — only clean hail variant |
| thunderstorm | `1080` ★frosted | has a moon; acceptable, frosted wins |
| tornado | `1088` | |

Known wonky (avoid): `1071` (ghost cloud, near-invisible on light backgrounds), `1073` (orange-tinted cloud), and every white-carded icon per the transparency warning above.
