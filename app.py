# app.py
from flask import Flask, render_template
import requests
import datetime
import pytz

app = Flask(__name__)

# ---------------------- HELPERS ----------------------
def get_fgi():
    try:
        res = requests.get("https://api.alternative.me/fng/?limit=1")
        val = res.json()['data'][0]['value']
        return int(val), None
    except Exception as e:
        return 0, f"FGI error: {e}"

def get_price():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        val = res.json()['bitcoin']['usd']
        return float(val), None
    except Exception as e:
        return 0.0, f"Price error: {e}"

def get_volume():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/global")
        return res.json()['data']['total_volume']['usd'], None
    except Exception as e:
        return 0.0, f"Volume error: {e}"

def get_coin_glass(metric):
    try:
        url = f"https://open-api.coinglass.com/public/v2/indicator/bitcoin?metric={metric}"
        headers = {"coinglassSecret": "test"}  # Placeholder header if needed
        res = requests.get(url, headers=headers)
        data = res.json()['data']
        return data['value'], None
    except Exception as e:
        return 0.0, f"{metric} error: {e}"

# ---------------------- MAIN ROUTE ----------------------
@app.route("/")
def index():
    price, price_error = get_price()
    fgi, fgi_error = get_fgi()
    volume, vol_error = get_volume()
    funding_rate, fr_error = get_coin_glass("fundingRate")
    open_interest, oi_error = get_coin_glass("openInterest")

    cet_time = datetime.datetime.now(pytz.timezone("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")

    return render_template("index.html",
                           price=price,
                           fgi=fgi,
                           volume=volume,
                           funding_rate=funding_rate,
                           open_interest=open_interest,
                           errors=[price_error, fgi_error, vol_error, fr_error, oi_error],
                           timestamp=cet_time)

# ---------------------- DEPLOY ENTRY ----------------------
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
