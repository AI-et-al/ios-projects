# widgy-icons service

> **STATUS — DISCONTINUED FOR NOW (2026-09-13).** The Supabase project is
> deliberately paused at the owner's request: no installed widget
> currently calls it. `INACTIVE` is the *intended* state, not an outage —
> **do not restore it just because it is found paused.** Restore only
> when the owner asks, or re-imports a widget whose forecast rows need
> it: Supabase MCP `restore_project` on `cusyejearwlwbqeabspa` (~2 min,
> same URL comes back). Everything below describes the service as it
> runs when active.

Serves the right prepped 3dweather icon for a forecast offset, so Widgy
image layers can show per-hour/per-day 3D icons (Widgy has no native
per-forecast custom images — probe-verified 2026-08-17).

**Endpoint when active** (Supabase Edge Function `icon`, project `cusyejearwlwbqeabspa`, org AI-et-al-dev, free tier):

```
https://cusyejearwlwbqeabspa.supabase.co/functions/v1/icon?offset=1h
```

- `offset`: `now` | `1h` | `2h` | `3h` | `1d` | `2d` | `3d`
- `lat` / `lon`: optional, default Dallas (32.7767, −96.797)
- `debug=1`: JSON `{offset, when, code, isDay, condition}` instead of the PNG

Weather comes from Open-Meteo (keyless); WMO weather codes map to the 13
prepped conditions; icons are proxied from this repo pinned at commit
`c73c4cc`. Public endpoint, deliberately no JWT — Widgy sends bare GETs
and the only thing served is already-public PNGs. Responses cache ~10–15
minutes.

Widget impact while the service is off: only the six forecast-row images
(and, in the repo-lineage dist, the small service-backed Now glyph) go
blank. The hero icons, temperatures, and all text are unaffected — they
come from raw.githubusercontent.com and Widgy's own data sources.

Deploy history: Vercel was the original target but the session's connector
cannot create Vercel projects (403), so it landed on Supabase. Redeploy by
passing `supabase/index.ts` to the Supabase MCP `deploy_edge_function`
(name `icon`, `verify_jwt: false`).

## Outages & lifecycle

**2026-08-29:** project found `INACTIVE` — Supabase free-tier projects
auto-pause after ~1 week without qualifying activity, and a paused
project's DNS stops resolving entirely (`ENOTFOUND`), so every
forecast-row image in the widget went blank. Restored via the Supabase
MCP `restore_project`. Widget traffic evidently did not count
as (or did not generate) enough activity to prevent the pause; durable
fixes are a keep-alive with qualifying activity or moving the function
to a host that does not pause (Vercel was attempted 2026-08-18 and
failed with a 403 on project creation — worth retrying if the service
is ever revived for real use).

**2026-09-05 (approx.):** auto-paused again, on the same ~7-day clock.

**2026-09-13:** briefly restored during a performance investigation,
then **deliberately paused — discontinued for now** (owner request; no
installed widget uses it). See STATUS at the top.
