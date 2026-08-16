# Widgy widgets

Widgy widgets export/import as JSON (`.widgy` file, widgy.app link, QR, or clipboard JSON). Images are embedded as base64, so widgets are fully editable as text — which is what these sessions do.

## Projects

### weather-widget (in progress)

Goal: a standalone weather widget based on MachineWashCold_'s **Simpl.weather** (3 side buttons → now / +3h / +3d pages), with a custom icon set replacing the icons in its "Weather (Custom Images)" mapping.

Status — waiting on two inputs:

- [ ] **Share Widget** export of Simpl.weather (`.widgy` file or widgy.app link). This is the template — Widgy's schema is undocumented, so all edits are surgery on a real export.
- [ ] The custom icon directory (owner has one ready).

Plan once inputs land:

1. Commit the original export to `widgy/weather-widget/original/`
2. Commit icons to `widgy/weather-widget/icons/`, mapped to Widgy's weather-condition slots (clear day/night, partly cloudy, cloudy, rain, thunderstorm, snow, fog, wind, … — exact slot list comes from the export)
3. Resize/re-encode icons as needed and embed them as base64 into the export's custom-image weather layers
4. Output `widgy/weather-widget/dist/<name>.widgy` for re-import on device (Widgy → Create tab → Import)
