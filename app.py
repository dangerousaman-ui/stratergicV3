from flask import Flask, jsonify, render_template, request, send_from_directory
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

STATE = {
    "name": "Dehradun, Uttarakhand",
    "lat": 30.3165,
    "lon": 78.0322,
    "bbox": [28.43, 77.18, 31.50, 81.03],
}

PEOPLE = {
    "governor": {
        "name": "LT. GEN. GURMIT SINGH AVSM, PVSM, UYSM, VSM",
        "role": "Governor of Uttarakhand",
        "summary": "Official Raj Bhavan reference for the Governor of Uttarakhand.",
        "source": "https://governoruk.gov.in/our-governor-bioprofile-of-honble-governor-uttarakhand/",
    },
    "chief_minister": {
        "name": "Shri Pushkar Singh Dhami",
        "role": "Chief Minister of Uttarakhand",
        "summary": "Official Chief Minister profile and public portal for Uttarakhand government updates.",
        "source": "https://cm.uk.gov.in/about-chief-minister/",
    },
    "prime_minister": {
        "name": "Shri Narendra Modi",
        "role": "Prime Minister of India",
        "summary": "Official Prime Minister profile and PMO-linked public information entry point.",
        "source": "https://www.pmindia.gov.in/en/pms-profile/",
    },
    "pmo_social": {
        "name": "PMO India",
        "role": "Public social updates",
        "summary": "Official PMO X profile for current public posts and announcements.",
        "source": "https://x.com/PMOIndia",
    },
}

NEWS_QUERIES = {
    "uttarakhand": 'Uttarakhand news OR Dehradun news when:7d',
    "laws": 'Uttarakhand law OR Uttarakhand policy OR Uttarakhand government order when:14d',
    "cm": 'Pushkar Singh Dhami when:14d',
    "governor": 'Gurmit Singh Uttarakhand Governor when:30d',
    "pm": 'Narendra Modi OR PMO India when:7d',
}


def fetch_text(url: str, headers: dict | None = None, timeout: int = 20) -> str:
    req = Request(url, headers=headers or {"User-Agent": "Mozilla/5.0 StrategicDashboard/3.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_json(url: str, headers: dict | None = None, timeout: int = 20):
    return json.loads(fetch_text(url, headers=headers, timeout=timeout))


def parse_google_news_rss(query: str, limit: int = 8):
    url = (
        "https://news.google.com/rss/search?q="
        + quote_plus(query)
        + "&hl=en-IN&gl=IN&ceid=IN:en"
    )
    xml_text = fetch_text(url)
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    items = []
    if channel is None:
        return items
    for item in channel.findall("item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        source = "Google News"
        source_el = item.find("source")
        if source_el is not None and source_el.text:
            source = source_el.text.strip()
        items.append({
            "title": title,
            "link": link,
            "published": pub_date,
            "source": source,
        })
    return items


@app.route("/")
def index():
    return render_template("index.html", people=PEOPLE)


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory("static", "service-worker.js")


@app.route("/health")
def health():
    return jsonify({"ok": True, "service": "strategic-dashboard-render-v2"})


@app.route("/api/people")
def api_people():
    return jsonify({"ok": True, "people": PEOPLE})


@app.route("/api/news")
def api_news():
    topic = request.args.get("topic", "uttarakhand")
    query = NEWS_QUERIES.get(topic, NEWS_QUERIES["uttarakhand"])
    try:
        items = parse_google_news_rss(query=query)
        return jsonify({"ok": True, "topic": topic, "query": query, "items": items})
    except Exception as exc:
        return jsonify({"ok": False, "topic": topic, "items": [], "error": str(exc)}), 500


@app.route("/api/weather")
def api_weather():
    lat = request.args.get("lat", type=float, default=STATE["lat"])
    lon = request.args.get("lon", type=float, default=STATE["lon"])
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=Asia%2FKolkata&forecast_days=3"
    )
    try:
        data = fetch_json(url)
        return jsonify({"ok": True, "place": STATE["name"], "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/finance")
def api_finance():
    try:
        fx = fetch_json("https://api.frankfurter.app/latest?from=USD&to=INR,EUR")
        btc = fetch_json("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=inr,usd")
        return jsonify({
            "ok": True,
            "as_of": fx.get("date"),
            "rates": {
                "USD_INR": fx.get("rates", {}).get("INR"),
                "USD_EUR": fx.get("rates", {}).get("EUR"),
                "BTC_INR": btc.get("bitcoin", {}).get("inr"),
                "BTC_USD": btc.get("bitcoin", {}).get("usd"),
            },
        })
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/api/satellite")
def api_satellite():
    layer = request.args.get("layer", "MODIS_Terra_CorrectedReflectance_TrueColor")
    day = request.args.get("date")
    if not day:
        day = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    south, west, north, east = STATE["bbox"]
    url = (
        "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
        "?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
        f"&LAYERS={quote_plus(layer)}"
        "&STYLES=&FORMAT=image/jpeg&TRANSPARENT=FALSE"
        "&WIDTH=1400&HEIGHT=820&CRS=EPSG:4326"
        f"&BBOX={south},{west},{north},{east}"
        f"&TIME={day}"
    )
    return jsonify({"ok": True, "date": day, "layer": layer, "image_url": url})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
