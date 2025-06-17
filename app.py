from flask import Flask, render_template
import requests
import datetime
import pytz

app = Flask(__name__)

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url)
        data = response.json()
        if "price" in data:
            return float(data["price"]), None
        else:
            return 0.0, f"API error: {data.get('msg', 'unknown error')}"
    except Exception as e:
        return 0.0, f"Request failed: {e}"

@app.route("/")
def index():
    price, price_error = get_price("BTCUSDT")

    cet_time = datetime.datetime.now(pytz.timezone("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")

    return render_template("index.html",
                           price=price,
                           price_error=price_error,
                           timestamp=cet_time)

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
