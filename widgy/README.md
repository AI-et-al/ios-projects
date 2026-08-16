# Widgy widgets

Widgy widgets export/import as JSON (`.widgy` file, widgy.app link, QR, or clipboard JSON). Images are embedded as base64, so widgets are fully editable as text — which is what these sessions do.

## Projects

### weather-widget (in progress)

Goal: a standalone weather widget based on MachineWashCold_'s **Simpl.weather** (3 side buttons → now / +3h / +3d pages), with a custom icon set replacing the icons in its "Weather (Custom Images)" mapping.

Status:

- [x] Icon set — 45-icon `3dweather` pack in `icons/src/`; curation table and the **frosted-first** style preference live in `icons/README.md`
- [x] Font — **Numans** (family `Numans`, PostScript `Numans-Regular`), vendored in `fonts/` (latin subset via Fontsource, OFL). Install `Numans-Regular.ttf` on-device with a font-installer app so Widgy can render it; all text layers get set to it during the build.
- [ ] **Share Widget export of Simpl.weather** (`.widgy` file or widgy.app link) — still needed. This is the template; Widgy's schema is undocumented, so all edits are surgery on a real export.

Build plan once the export lands:

1. Commit the original export to `original/`
2. Map icons to the export's actual weather-condition slots per `icons/README.md` (frosted variants first; derive a bare frosted "cloudy" from `1069` if the slot exists)
3. Trim/pad/normalize the chosen icons and embed them as base64 into the custom-image weather layers
4. Set every text layer's font to `Numans-Regular`
5. Output `dist/<name>.widgy` for re-import on device (Widgy → Create tab → Import)
