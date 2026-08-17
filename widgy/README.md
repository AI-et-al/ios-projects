# Widgy widgets

Widgy widgets export/import as JSON (`.widgy` file, widgy.app link, QR, or clipboard JSON). A `.widgy` file is that JSON raw-deflate-compressed (zlib, wbits −15); custom images are referenced by URL and downloaded at import. Either way, widgets are fully editable as text — which is what these sessions do.

## Projects

### weather-widget (in progress)

Goal: a standalone weather widget based on MachineWashCold_'s **Simpl.weather** (3 side buttons → now / +3h / +3d pages), with a custom icon set replacing the icons in its "Weather (Custom Images)" mapping.

Status:

- [x] Icon set — 45-icon `3dweather` pack in `icons/src/`; curation table and the **frosted-first** style preference live in `icons/README.md`
- [x] Font — **Numans** (family `Numans`, PostScript `Numans-Regular`), vendored in `fonts/` (latin subset via Fontsource, OFL). Install `Numans-Regular.ttf` on-device with a font-installer app so Widgy can render it; all text layers get set to it during the build.
- [x] **Original export** in `original/` (as JSON). Format discoveries: custom weather images are top-level `f3`–`u3` **URL** keys (no base64 — Widgy downloads them at import); fonts are name strings (`"System Bold"`) in text-layer key `1` and data-field key `34`; the custom images render as the big 1400-unit orb behind the temperature, not the small condition glyph (that's an SF symbol).
- [x] **Build pipeline** in `build/`: `prep_icons.py` (trim/square/resize + sun-erase & de-haze treatments; output in `icons/prepped/`) → `build_widgy.py <sha>` (font swap, slot repoint to commit-pinned raw.githubusercontent URLs, deflate to `dist/simpl-weather-3d.widgy`).
- [ ] **Slot mapping unverified**: `build/slot-map.json` assumes Dark Sky enum order for `f3`–`u3` (fits: author filled `f3`–`p3`, left the 5 rare trailing slots broken). Verify with a screenshot of Widgy's Weather (Custom Images) editor showing which image sits in which named slot; correct the map and rebuild if wrong. `s3`–`u3` unknown, left untouched.
- [ ] **On-device**: import `dist/simpl-weather-3d.widgy` (open it from the GitHub app/Files and share to Widgy, or Widgy → Create → Import). Install `fonts/Numans-Regular.ttf` (Fontcase, iFont, …) so text renders in Numans — it falls back to the system font until then.
