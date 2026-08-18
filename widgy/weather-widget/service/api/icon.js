// Serves the right 3dweather icon for a forecast offset, for Widgy image layers.
//
// GET /api/icon?offset=now|1h|2h|3h|1d|2d|3d [&lat=..&lon=..] [&debug=1]
//
// Weather from Open-Meteo (no key). Icons proxied from the pinned commit in
// AI-et-al/ios-projects. Default location: Dallas, TX.

const ICON_BASE =
  'https://raw.githubusercontent.com/AI-et-al/ios-projects/c73c4cc60bcde2c9c5c7dc6fd59e082afa436d00/widgy/weather-widget/icons/prepped/';

function condition(code, isDay) {
  const dn = (d, n) => (isDay ? d : n);
  if (code === 0) return dn('clear-day', 'clear-night');
  if (code === 1 || code === 2) return dn('partly-cloudy-day', 'partly-cloudy-night');
  if (code === 3) return 'cloudy';
  if (code === 45 || code === 48) return 'fog';
  if (code === 56 || code === 57 || code === 66 || code === 67) return 'sleet';
  if (code >= 51 && code <= 65) return 'rain';
  if ((code >= 71 && code <= 77) || code === 85 || code === 86) return 'snow';
  if (code >= 80 && code <= 82) return 'rain';
  if (code === 95) return 'thunderstorm';
  if (code === 96 || code === 99) return 'hail';
  return 'cloudy';
}

module.exports = async (req, res) => {
  try {
    const { offset = 'now', lat = '32.7767', lon = '-96.797', debug } = req.query;
    const m = /^(now|([123])([hd]))$/.exec(offset);
    if (!m) {
      res.status(400).json({ error: 'offset must be now|1h|2h|3h|1d|2d|3d' });
      return;
    }

    const wxUrl =
      `https://api.open-meteo.com/v1/forecast?latitude=${encodeURIComponent(lat)}` +
      `&longitude=${encodeURIComponent(lon)}` +
      `&hourly=weather_code,is_day&daily=weather_code&timezone=auto&forecast_days=5`;
    const wx = await (await fetch(wxUrl)).json();

    let code, isDay, when;
    if (offset === 'now' || m[3] === 'h') {
      const n = offset === 'now' ? 0 : parseInt(m[2], 10);
      const localNow = new Date(Date.now() + wx.utc_offset_seconds * 1000);
      const hourIso = localNow.toISOString().slice(0, 13) + ':00';
      let i = wx.hourly.time.indexOf(hourIso);
      if (i < 0) i = 0;
      const j = Math.min(i + n, wx.hourly.time.length - 1);
      code = wx.hourly.weather_code[j];
      isDay = wx.hourly.is_day[j] === 1;
      when = wx.hourly.time[j];
    } else {
      const n = parseInt(m[2], 10);
      const j = Math.min(n, wx.daily.time.length - 1);
      code = wx.daily.weather_code[j];
      isDay = true; // daily forecast always uses day-variant icons
      when = wx.daily.time[j];
    }

    const cond = condition(code, isDay);
    if (debug) {
      res.setHeader('Cache-Control', 'no-store');
      res.status(200).json({ offset, when, code, isDay, condition: cond });
      return;
    }

    const png = await fetch(ICON_BASE + cond + '.png');
    if (!png.ok) throw new Error(`icon fetch ${png.status} for ${cond}`);
    const buf = Buffer.from(await png.arrayBuffer());
    res.setHeader('Content-Type', 'image/png');
    res.setHeader(
      'Cache-Control',
      'public, max-age=600, s-maxage=900, stale-while-revalidate=3600'
    );
    res.status(200).send(buf);
  } catch (err) {
    res.status(500).json({ error: String(err && err.message ? err.message : err) });
  }
};
