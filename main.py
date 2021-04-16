from PIL import Image, ImageDraw, ImageFont

from typing import List, Tuple, Dict, Callable
import SH1106
import json
import config
import time
import datetime
import pytz
import math
import requests


def fetch_ohlc(symbol: str) -> List[Tuple[float, ...]]:
    res = requests.get(
        "https://api.binance.com/api/v3/klines", params={"symbol": symbol.upper(), "interval": "1h", "limit": 25})
    res.raise_for_status()

    json_data = json.loads(res.text)

    ohlc = []
    for data_entry in json_data:
        ohlc.append(tuple([float(data_entry[i]) for i in [1, 2, 3, 4]]))

    return ohlc


def fetch_crypto_data(symbol: str) -> Tuple[float, float, List[Tuple[float, ...]]]:
    ohlc_data = fetch_ohlc(symbol)
    price_current = ohlc_data[-1][-1]
    price_day_ago = ohlc_data[0][0]
    price_diff = price_current - price_day_ago

    return price_current, price_diff, ohlc_data


def price_to_str(price: float) -> str:
    exp10 = math.floor(math.log10(abs(price)))
    num_decimals = int(min(5, max(0, 3 - exp10)))
    return "%.*f" % (num_decimals, price)


def main():
    disp = SH1106.SH1106()
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()

    font = ImageFont.truetype("OpenSans-Regular.ttf", 20)
    font_small = ImageFont.truetype("OpenSans-Regular.ttf", 16)
    font_tiny = ImageFont.truetype("OpenSans-Regular.ttf", 12)
    font_super_tiny = ImageFont.truetype("OpenSans-Regular.ttf", 10)

    while True:
        price, diff, ohlc = fetch_crypto_data(
            "dogeusdt")  # TODO: use any binance symbol you want (Ex.: DOGE = dogeusdt)

        # Clear Screen
        image1 = Image.new('1', (disp.width, disp.height), "WHITE")
        draw = ImageDraw.Draw(image1)

        # Title
        draw.rectangle((0, 0, 127, 17), outline=255, fill=0)  # Background rectangle
        draw.text((35, 0), 'DOGECOIN ', font=font_tiny, fill=1)

        # Actual Price
        draw.text((30, 20), text="{} $".format(
            price_to_str(price)), font=font, fill=0)

        # Set price diff symbol
        diff_symbol = ""
        if diff > 0:
            diff_symbol = "+"
        if diff < 0:
            diff_symbol = "-"

        # Draw diff price
        draw.text((35, 40), text="{}{}$".format(diff_symbol, price_to_str(diff)), font=font_small, fill=0)

        disp.ShowImage(disp.getbuffer(image1))
        time.sleep(5)

if __name__ == "__main__":
    main()