# 3dweather icon pack

45 unique PNGs (RGBA, ~400–700px, transparent bg) in `src/`, keeping their original Android MediaStore names. From the owner's Android days; uploaded 2026-08-16 as `3dweather_.zip` (90 files → 45 after byte-identical `* 2.png` dedupe).

## Style families

The pack mixes three renderings of the same 3D-clay style:

- **frosted** — translucent glass clouds you can see through: `1069` (sun), `1078` (moon+rain), `1080` (moon+thunder), `1087` (sleet mix)
- **glow** — soft white clouds with a large baked-in halo: `1063–1067`, `1070–1073`, `1075–1082`, `1084`, `1086`
- **solid** — crisp opaque white clouds: `1090–1092`, `1096–1104`, `1107`, `1109–1112`
- **beige/dust** — intentionally tan: `1085`, `1094` (dust/sand + wind lines), `1088`, `1105` (tornado)

**Owner preference: frosted-first.** Use the four frosted icons wherever their condition matches; fill remaining slots from the *glow* family (closest texture match), not the solid family. Solid variants are the fallback for small sizes if frosted/glow read too faint.

## Proposed slot mapping (v1 — final slots come from the Widgy export)

| Condition | Pick | Alternates / notes |
|---|---|---|
| clear day | `1068` | big sun; `1066`/`1095` are sun+haze waves |
| clear night | `1075` | soft-glow moon; `1093` is the crisp solid moon |
| partly cloudy day | `1069` ★frosted | `1072`, `1107`, `1073` (odd warm-tinted cloud) |
| partly cloudy night | `1081` | `1082`, `1111`, `1112` |
| cloudy (bare cloud) | — none in pack | derive: erase sun from `1069` (keeps frosted) or from `1072` |
| rain day | `1063` | sun-shower; `1065` drizzle, `1067`, `1090`/`1096` solid |
| rain night | `1078` ★frosted | `1077`, `1079`, `1102`, `1103` |
| thunderstorm day | `1070` | `1100`/`1104` solid; **avoid `1071`** (ghost cloud, near-invisible) |
| thunderstorm night | `1080` ★frosted | `1076`, `1109`, `1110` |
| snow | `1084` | `1064`, `1086` (single big flake), `1091`/`1097`/`1098` solid |
| sleet / wintry mix | `1087` ★frosted | `1098` solid |
| hail / freezing rain | `1092` (day) / `1101` (night) | slash-streak variants, solid only |
| fog / haze day | `1095` | `1066`; night: `1106` (moon + waves) |
| dust / sand / wind | `1094` | `1085` |
| tornado | `1088` | `1105` |

Known wonky (avoid unless desperate): `1071` (cloud almost fully transparent white — vanishes on light backgrounds), `1073` (cloud tinted orange, doesn't match either family).

Gaps: no bare "cloudy" icon, no pure white wind icon, no day-side frosted variants — day slots therefore use the glow family.
