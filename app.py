from flask import Flask, render_template
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

def get_fgi():
    response = requests.get("https://api.alternative.me/fng/")
    data = response.json()
    value = int(data["data"][0]["value"])
    return value

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    return float(response.json()["price"])

def get_funding_rate(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
        response = requests.get(url)
        rate = float(response.json()["lastFundingRate"])
        return rate
    except:
        return None

def get_open_interest(symbol="BTCUSDT"):
    try:
        url = f"https://fapi.binance.com/futures/data/openInterestHist?symbol={symbol}&period=5m&limit=1"
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return float(data[0]["sumOpenInterestValue"]) / 1e9
    except:
        pass
    return None

def get_volume(symbol="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url)
        return float(response.json()["quoteVolume"]) / 1e9
    except:
        return None

def get_cet_time():
    cet = pytz.timezone("Europe/Stockholm")
    now = datetime.now(cet)
    return now.strftime("%Y-%m-%d %H:%M:%S")

@app.route("/")
def index():
    fgi = get_fgi()
    price = get_price("BTCUSDT")
    funding_rate = get_funding_rate("BTCUSDT")
    open_interest = get_open_interest()
    volume = get_volume()
    timestamp = get_cet_time()

    def tolka(param, value):
        if value is None:
            return "N/A", "gray"
        if param == "fgi":
            if value < 50:
                return "Fear", "red"
            elif value <= 54:
                return "Neutral", "orange"
            else:
                return "Greed", "green"
        elif param == "fr":
            if value < -0.01:
                return "Bearish", "red"
            elif value <= 0.01:
                return "Neutral", "orange"
            else:
                return "Bullish", "green"
        elif param == "oi":
            if value < 6:
                return "Weak activity", "red"
            elif value <= 10:
                return "Neutral", "orange"
            else:
                return "Strong activity", "green"
        elif param == "vol":
            if value < 5:
                return "Low volume", "red"
            elif value <= 10:
                return "Neutral", "orange"
            else:
                return "High volume", "green"
        return "Unknown", "gray"

    def jämför(par, a, b):
        if a is None or b is None:
            return "Unknown", "gray", "Data unavailable"
        if par == "fr+vol":
            if a > 0.01 and b > 10:
                return "Bullish", "green", "High FR & Volume = strong conviction"
            elif a < -0.01 and b > 10:
                return "Bearish", "red", "Negative FR & High Volume = strong short pressure"
            elif abs(a) <= 0.01 and 5 <= b <= 10:
                return "Neutral", "orange", "Normal funding & volume"
            else:
                return "Unclear", "gray", "Inconsistent signal"
        elif par == "oi+vol":
            if a > 10 and b > 10:
                return "Bullish", "green", "High OI & Volume = strong trend"
            elif a < 6 and b < 5:
                return "Bearish", "red", "Low OI & Volume = weak market"
            elif 6 <= a <= 10 and 5 <= b <= 10:
                return "Neutral", "orange", "Balanced OI and Volume"
            else:
                return "Unclear", "gray", "Mixed signals"
        elif par == "fgi+vol":
            if a > 54 and b > 10:
                return "Bullish", "green", "Greed with High Volume = momentum"
            elif a < 50 and b < 5:
                return "Bearish", "red", "Fear with Low Volume = no buyers"
            elif 50 <= a <= 54 and 5 <= b <= 10:
                return "Neutral", "orange", "Neutral sentiment and volume"
            else:
                return "Unclear", "gray", "No clear signal"
        elif par == "alla":
            if funding_rate and open_interest and volume and fgi:
                if funding_rate > 0.01 and open_interest > 10 and volume > 10 and fgi > 54:
                    return "Strong Bullish", "green", "All indicators point up"
                elif funding_rate < -0.01 and open_interest < 6 and volume < 5 and fgi < 50:
                    return "Strong Bearish", "red", "All indicators point down"
            return "Mixed", "orange", "Conflicting or moderate signals"
        return "Unknown", "gray", "No logic applied"

    context = {
        "fgi": fgi,
        "fgi_text": tolka("fgi", fgi),
        "price": price,
        "funding_rate": funding_rate if funding_rate is not None else "N/A",
        "fr_text": tolka("fr", funding_rate),
        "open_interest": open_interest if open_interest is not None else "N/A",
        "oi_text": tolka("oi", open_interest),
        "volume": volume if volume is not None else "N/A",
        "vol_text": tolka("vol", volume),
        "fr_vol": jämför("fr+vol", funding_rate, volume),
        "oi_vol": jämför("oi+vol", open_interest, volume),
        "fgi_vol": jämför("fgi+vol", fgi, volume),
        "all_combo": jämför("alla", funding_rate, open_interest),
        "timestamp": timestamp
    }

    return render_template("index.html", **context)

if __name__ == "__main__":
    app.run(debug=True)
