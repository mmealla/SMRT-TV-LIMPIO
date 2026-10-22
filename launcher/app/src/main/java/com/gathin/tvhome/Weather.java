package com.gathin.tvhome;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.Locale;

/**
 * Weather widget for the launcher. Uses Open-Meteo (free, no API key).
 * Place is from config.json weather_city, or auto-detected by IP (ipwho.is -> geojs.io).
 * Cached for 30 min; place cached for 24h. All in SharedPreferences.
 */
final class Weather {

    private static final String TAG = "TvHome.Weather";
    private static final long STALE_MS = 30 * 60_000L;      // 30 min
    private static final long PLACE_MS = 24 * 60 * 60_000L;  // 24h
    private static final int TIMEOUT_MS = 8000;
    private static final String PREFS = "weather";

    /** Sky condition for theming the backdrop (SkyView). */
    enum Sky { CLEAR, PARTLY, CLOUDY, FOG, RAIN, SNOW, THUNDER }

    /** One weather report: place, current temp, today's range, WMO code, day/night, feels-like, humidity, wind, tomorrow high/low/code/rain%. */
    static final class Report {
        final String place;
        final double temp, high, low;
        final int code;
        final boolean day;
        final double feels, wind;
        final int humidity;
        final double tomorrowHigh, tomorrowLow;
        final int tomorrowCode, tomorrowRain;
        final long fetchedAt;

        Report(String place, double temp, double high, double low, int code, boolean day,
               double feels, int humidity, double wind,
               double tomorrowHigh, double tomorrowLow, int tomorrowCode, int tomorrowRain, long fetchedAt) {
            this.place = place;
            this.temp = temp;
            this.high = high;
            this.low = low;
            this.code = code;
            this.day = day;
            this.feels = feels;
            this.humidity = humidity;
            this.wind = wind;
            this.tomorrowHigh = tomorrowHigh;
            this.tomorrowLow = tomorrowLow;
            this.tomorrowCode = tomorrowCode;
            this.tomorrowRain = tomorrowRain;
            this.fetchedAt = fetchedAt;
        }

        boolean stale(long now) {
            return now - fetchedAt > STALE_MS;
        }
    }

    /** Where the widget reports on: a name and coordinates. */
    static final class Place {
        final String name;
        final double lat, lon;
        Place(String name, double lat, double lon) {
            this.name = name;
            this.lat = lat;
            this.lon = lon;
        }
    }

    private Weather() {}

    /** WMO weather interpretation code -> Sky enum for theming. */
    static Sky sky(int wmo) {
        if (wmo <= 0) return Sky.CLEAR;
        if (wmo <= 2) return Sky.PARTLY;
        if (wmo == 3) return Sky.CLOUDY;
        if (wmo == 45 || wmo == 48) return Sky.FOG;
        if (wmo >= 71 && wmo <= 77 || wmo == 85 || wmo == 86) return Sky.SNOW;
        if (wmo >= 95) return Sky.THUNDER;
        return Sky.RAIN; // drizzle 51-57, rain 61-67, showers 80-82
    }

    /** Icon resource for a Sky condition. */
    static int icon(Sky sky, boolean day) {
        switch (sky) {
            case CLEAR: return day ? R.drawable.ic_w_sunny : R.drawable.ic_w_clear_night;
            case PARTLY: return day ? R.drawable.ic_w_partly_day : R.drawable.ic_w_partly_night;
            case CLOUDY: return R.drawable.ic_w_cloud;
            case FOG: return R.drawable.ic_w_fog;
            case SNOW: return R.drawable.ic_w_snow;
            case THUNDER: return R.drawable.ic_w_thunder;
            default: return R.drawable.ic_w_rain;
        }
    }

    /** String resource label for a Sky condition. */
    static int label(Sky sky) {
        switch (sky) {
            case CLEAR: return R.string.weather_clear;
            case PARTLY: return R.string.weather_partly;
            case CLOUDY: return R.string.weather_cloudy;
            case FOG: return R.string.weather_fog;
            case SNOW: return R.string.weather_snow;
            case THUNDER: return R.string.weather_thunder;
            default: return R.string.weather_rain;
        }
    }

    /** The last cached report, or null. */
    static Report cached(Context context) {
        SharedPreferences p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        if (!p.contains("fetched")) return null;
        long fetched = p.contains("t_code") ? p.getLong("fetched", 0) : 0;
        return new Report(p.getString("place", ""), p.getFloat("temp", 0), p.getFloat("high", 0), p.getFloat("low", 0),
                p.getInt("code", 0), p.getBoolean("day", true), p.getFloat("feels", 0), p.getInt("humidity", 0),
                p.getFloat("wind", 0), p.getFloat("t_high", 0), p.getFloat("t_low", 0), p.getInt("t_code", 0),
                p.getInt("t_rain", 0), fetched);
    }

    /**
     * Off the main thread: the place for city (empty = IP geolocation), looked up at most once a day.
     * Shared by weather widget.
     */
    static Place place(Context context, String city) throws IOException, JSONException {
        SharedPreferences p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String lang = Locale.getDefault().getLanguage(); // "es" for Spanish
        long now = System.currentTimeMillis();
        String placeKey = city + "|" + lang;
        if (!placeKey.equals(p.getString("place_key", null)) || now - p.getLong("place_at", 0) > PLACE_MS
                || !p.contains("place_name")) {
            double[] at = new double[2];
            int bar = city.indexOf('|'); // "name|country": only match in that country
            String name = city.isEmpty() ? placeFromIp(lang, at)
                    : bar < 0 ? geocode(city, lang, null, at) : geocode(city.substring(0, bar), lang, city.substring(bar + 1), at);
            p.edit().putString("place_key", placeKey).putLong("place_at", now).putString("place_name", name)
                    .putFloat("lat", (float) at[0]).putFloat("lon", (float) at[1]).apply();
        }
        return new Place(p.getString("place_name", ""), p.getFloat("lat", 0), p.getFloat("lon", 0));
    }

    /** Off the main thread: a fresh report, saved for next time. city may be empty (use IP's place). */
    static Report fetch(Context context, String city) throws IOException, JSONException {
        SharedPreferences p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        long now = System.currentTimeMillis();
        Place at = place(context, city);
        String place = at.name;
        JSONObject f = get(String.format(Locale.US,
                "https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f"
                        + "&current=temperature_2m,weather_code,is_day,apparent_temperature,relative_humidity_2m,wind_speed_10m"
                        + "&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max"
                        + "&timezone=auto&forecast_days=2",
                at.lat, at.lon));
        JSONObject current = f.getJSONObject("current");
        JSONObject daily = f.getJSONObject("daily");
        JSONArray max = daily.getJSONArray("temperature_2m_max"), min = daily.getJSONArray("temperature_2m_min");
        JSONArray codes = daily.getJSONArray("weather_code"), rain = daily.getJSONArray("precipitation_probability_max");
        Report r = new Report(place, current.getDouble("temperature_2m"), max.getDouble(0), min.getDouble(0),
                current.getInt("weather_code"), current.optInt("is_day", 1) == 1,
                current.optDouble("apparent_temperature", current.getDouble("temperature_2m")),
                current.optInt("relative_humidity_2m", 0), current.optDouble("wind_speed_10m", 0),
                max.getDouble(1), min.getDouble(1), codes.getInt(1), rain.isNull(1) ? 0 : rain.getInt(1), now);
        p.edit().putString("place", r.place).putFloat("temp", (float) r.temp).putFloat("high", (float) r.high)
                .putFloat("low", (float) r.low).putInt("code", r.code).putBoolean("day", r.day)
                .putFloat("feels", (float) r.feels).putInt("humidity", r.humidity).putFloat("wind", (float) r.wind)
                .putFloat("t_high", (float) r.tomorrowHigh).putFloat("t_low", (float) r.tomorrowLow)
                .putInt("t_code", r.tomorrowCode).putInt("t_rain", r.tomorrowRain).putLong("fetched", now).apply();
        return r;
    }

    /** The IP's city and coordinates; name in TV's language when geocoder knows it. */
    private static String placeFromIp(String lang, double[] at) throws IOException, JSONException {
        String city, country = null;
        try {
            JSONObject ip = get("https://ipwho.is/");
            if (!ip.optBoolean("success", false)) throw new IOException("ipwho.is: no answer");
            city = ip.getString("city");
            country = ip.optString("country_code", null);
            at[0] = ip.getDouble("latitude");
            at[1] = ip.getDouble("longitude");
        } catch (IOException | JSONException first) {
            JSONObject ip = get("https://get.geojs.io/v1/ip/geo.json");
            city = ip.getString("city");
            country = ip.optString("country_code", null);
            at[0] = Double.parseDouble(ip.getString("latitude"));
            at[1] = Double.parseDouble(ip.getString("longitude"));
        }
        try {
            double[] ignored = new double[2];
            return geocode(city, lang, country, ignored);
        } catch (IOException | JSONException e) {
            return city;
        }
    }

    /** A city's name in lang and its coordinates; with country set, only a match in that country counts. */
    private static String geocode(String city, String lang, String country, double[] at) throws IOException, JSONException {
        JSONObject g = get("https://geocoding-api.open-meteo.com/v1/search?count=5&language=" + lang
                + "&name=" + URLEncoder.encode(city, "UTF-8"));
        JSONArray results = g.optJSONArray("results");
        if (results != null) {
            for (int i = 0; i < results.length(); i++) {
                JSONObject r = results.getJSONObject(i);
                if (country != null && !country.equalsIgnoreCase(r.optString("country_code"))) continue;
                at[0] = r.getDouble("latitude");
                at[1] = r.getDouble("longitude");
                return r.getString("name");
            }
        }
        throw new IOException("no place called " + city);
    }

    static JSONObject get(String url) throws IOException, JSONException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(TIMEOUT_MS);
        c.setReadTimeout(TIMEOUT_MS);
        c.setRequestProperty("User-Agent", "tvhome-launcher");
        try (InputStream in = c.getInputStream()) {
            if (c.getResponseCode() != 200) throw new IOException(url + ": HTTP " + c.getResponseCode());
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[4096];
            for (int n; (n = in.read(buf)) > 0; ) out.write(buf, 0, n);
            return new JSONObject(out.toString("UTF-8"));
        } finally {
            c.disconnect();
        }
    }
}