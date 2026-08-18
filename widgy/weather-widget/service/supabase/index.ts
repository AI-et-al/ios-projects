// widgy-icons: serves the right 3dweather icon for a forecast offset,
// consumed by Widgy image layers. Public endpoint (no auth): serves only
// weather-condition PNGs that are already public in AI-et-al/ios-projects.
//
// Deployed as Supabase Edge Function "icon" on project cusyejearwlwbqeabspa:
//   https://cusyejearwlwbqeabspa.supabase.co/functions/v1/icon
// GET ?offset=now|1h|2h|3h|1d|2d|3d [&lat=..&lon=..] [&debug=1]
// Weather from Open-Meteo (no key). Default location: Dallas, TX.

const ICON_BASE =
  "https://raw.githubusercontent.com/AI-et-al/ios-projects/c73c4cc60bcde2c9c5c7dc6fd59e082afa436d00/widgy/weather-widget/icons/prepped/";

function condition(code: number, isDay: boolean): string {
  const dn = (d: string, n: string) => (isDay ? d : n);
  if (code === 0) return dn("clear-day", "clear-night");
  if (code === 1 || code === 2) return dn("partly-cloudy-day", "partly-cloudy-night");
  if (code === 3) return "cloudy";
  if (code === 45 || code === 48) return "fog";
  if (code === 56 || code === 57 || code === 66 || code === 67) return "sleet";
  if (code >= 51 && code <= 65) return "rain";
  if ((code >= 71 && code <= 77) || code === 85 || code === 86) return "snow";
  if (code >= 80 && code <= 82) return "rain";
  if (code === 95) return "thunderstorm";
  if (code === 96 || code === 99) return "hail";
  return "cloudy";
}

Deno.serve(async (req: Request) => {
  try {
    const u = new URL(req.url);
    const offset = u.searchParams.get("offset") ?? "now";
    const lat = u.searchParams.get("lat") ?? "32.7767";
    const lon = u.searchParams.get("lon") ?? "-96.797";
    const debug = u.searchParams.get("debug");
    const m = /^(?:now|([1-6])h|([1-3])d)$/.exec(offset);
    if (!m) {
      return Response.json({ error: "offset must be now|1h..6h|1d..3d" }, { status: 400 });
    }

    const wxUrl =
      `https://api.open-meteo.com/v1/forecast?latitude=${encodeURIComponent(lat)}` +
      `&longitude=${encodeURIComponent(lon)}` +
      `&hourly=weather_code,is_day&daily=weather_code&timezone=auto&forecast_days=5`;
    const wx = await (await fetch(wxUrl)).json();

    let code: number, isDay: boolean, when: string;
    if (offset === "now" || m[1]) {
      const n = offset === "now" ? 0 : parseInt(m[1], 10);
      const localNow = new Date(Date.now() + wx.utc_offset_seconds * 1000);
      const hourIso = localNow.toISOString().slice(0, 13) + ":00";
      let i = wx.hourly.time.indexOf(hourIso);
      if (i < 0) i = 0;
      const j = Math.min(i + n, wx.hourly.time.length - 1);
      code = wx.hourly.weather_code[j];
      isDay = wx.hourly.is_day[j] === 1;
      when = wx.hourly.time[j];
    } else {
      // Widgy convention (verified on-device): +1d = TODAY, +2d = tomorrow.
      const n = parseInt(m[2], 10) - 1;
      const j = Math.max(0, Math.min(n, wx.daily.time.length - 1));
      when = wx.daily.time[j];
      // Prefer the 1pm hourly code for that day: Open-Meteo's daily code is
      // the day's most severe condition, which overweights brief events.
      const k = wx.hourly.time.indexOf(when + "T13:00");
      code = k >= 0 ? wx.hourly.weather_code[k] : wx.daily.weather_code[j];
      isDay = true; // daily rows always use day-variant icons
    }

    const cond = condition(code, isDay);
    if (debug) {
      return Response.json({ offset, when, code, isDay, condition: cond });
    }

    const png = await fetch(ICON_BASE + cond + ".png");
    if (!png.ok) throw new Error(`icon fetch ${png.status} for ${cond}`);
    return new Response(await png.arrayBuffer(), {
      headers: {
        "Content-Type": "image/png",
        "Cache-Control": "public, max-age=600, s-maxage=900, stale-while-revalidate=3600",
      },
    });
  } catch (err) {
    return Response.json({ error: String(err) }, { status: 500 });
  }
});
