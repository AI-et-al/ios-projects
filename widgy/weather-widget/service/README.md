# widgy-icons service

Serves the right prepped 3dweather icon for a forecast offset, so Widgy
image layers can show per-hour/per-day 3D icons (Widgy has no native
per-forecast custom images — probe-verified 2026-08-17).

**Live endpoint** (Supabase Edge Function `icon`, project `cusyejearwlwbqeabspa`, org AI-et-al-dev, free tier):

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

Deploy history: Vercel was the original target but the session's connector
cannot create Vercel projects (403), so it landed on Supabase. Redeploy by
passing `supabase/index.ts` to the Supabase MCP `deploy_edge_function`
(name `icon`, `verify_jwt: false`).
