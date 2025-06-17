from flask import Flask, render_template
import requests
import datetime
import pytz

app = Flask(__name__)

def get_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        if "bitcoin" in data and "usd" in data["bitcoin"]:
            return float(data["bitcoin"]["usd"]), None
        else:
            return 0.0, f"API error: Unexpected response: {data}"
    except Exception as e:
        return 0.0, f"Request failed: {e}"

@app.route("/")
def index():
    price, price_error = get_price()

    cet_time = datetime.datetime.now(pytz.timezone("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")

    return render_template("index.html",
                           price=price,
                           price_error=price_error,
                           timestamp=cet_time)

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
