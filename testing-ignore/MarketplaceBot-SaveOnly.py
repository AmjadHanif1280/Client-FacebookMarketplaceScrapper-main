"""
This was a total failure ignore this file - Aidan (05/03/2023)
"""
import csv
import re
import time
import traceback
from datetime import datetime
from typing import Any

import pytz
import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

from helpers.cfg_loader import *

config_vars = load_config()
globals().update(config_vars)

def get_usage(cur: int, queries: int):
    try:
        response = requests.get(
            "https://app.scrapingbee.com/api/v1/usage",
            params={
                "api_key": SCRAPING_BEE_API_KEY
            },
            timeout=None,
        ).json()
        tz = pytz.timezone("Australia/Victoria")
        est = pytz.timezone("US/Eastern")
        text = f"""
Telegram Bot: **🔴 Offline!**
Scrapper: **🚧👷‍♂️ Preparing! - {cur} out of {queries} left!**

*Max Credits:* {response['max_api_credit']}
*Used Credits:* {response['used_api_credit']}
*Credits Left:* {int(response['max_api_credit']) - int(response['used_api_credit'])}


*Last Updated at:*
- {datetime.now(tz).strftime('%I:%M:%S %p %Z, %b %d, %Y')}
- {datetime.now(est).strftime('%I:%M:%S %p %Z, %b %d, %Y')}"""

        session = requests.Session()
        url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
        data = {
            "chat_id": CHANNEL,
            "message_id": 49,
            "text": text,
            "parse_mode": PARSE_MODE,
        }

        temp_post = session.post(url, data=data, timeout=None).json()
        print(temp_post)
    except Exception:
        print(traceback.format_exc())


def calculate_distance(location1: str, location2: str) -> str | Any:
    while True:
        try:
            geolocator = Nominatim(user_agent="my_email@myserver.com", timeout=100, scheme="http")
            location1 = geolocator.geocode(location1)
            location2 = geolocator.geocode(location2)
            break
        except Exception as e:
            print(e)
            return "bad request"

    return geodesic(location1.point, location2.point).kilometers


def error_handler():
    message = f" * An exception was raised! *\n\n```python\n {traceback.format_exc()} ```\n\n\n"
    try:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={DEV_CHANNEL}&text={message}&parse_mode=Markdown",
            timeout=None)
    except Exception as e:
        print(e)


def handle_api_error(e: Exception, url: str) -> requests.models.Response:
    print(e)
    print(f"Error: {url}")
    error_handler()
    return requests.models.Response()


def send_markdown_img(markdown: str, img: str) -> None:
    markdown = markdown.decode()
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    params = {
        "chat_id": CHANNEL_ID,
        "caption": markdown.encode(),
        "parse_mode": "Markdown",
        "photo": img,
    }
    response = requests.post(url, params=params)
    print("SUCCESSFULLY SENT IMAGE TO TELEGRAM CHANNEL!") if re.search(
        r'{"ok":true',
        response.text) else print("ERROR SENDING IMAGE TO TELEGRAM CHANNEL!")


if not os.path.exists("response.json"):
    input("-")

config = json.load(open("../config.json", encoding="utf-8"))
queries = [query.lstrip() for query in config["queries"]["title_include"]]

for cur, query in enumerate(queries, start=1):
    get_usage(cur=cur, queries=len(queries))

    url = f"https://dev-fb-mk-bot.aidan4043.repl.co/search?locationLatitude={LAT}&locationLongitude=" \
          f"{LON}&listingQuery={query.lstrip()}"
    try:
        resp = requests.get(url, timeout=None).json()
    except requests.exceptions.ConnectionError as connErr:
        err = handle_api_error(connErr, url)
        continue
    except requests.exceptions.Timeout as timeoutErr:
        err = handle_api_error(timeoutErr, url)
        continue
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        continue

    data = json.load(
        open("../response.json",
             encoding="utf-8")) if os.path.exists("response.json") else {}

    if query not in data:
        data[query] = []

    curList = []

    for listing in resp["data"]["listingPages"][0]["listings"] if resp is not None else []:
        if listing["name"] in config["queries"]["title_exclude"] or any(
                result["id"] == listing["id"] for result in data[query]):
            continue
        if any(listing["id"] == result["id"] for result in curList):
            continue

        # check if listing["id"] is anywhere in the data file if so, continue
        if any(listing["id"] in result["id"] for result in data[query]):
            continue

        try:
            distance = calculate_distance(listing['sellerLocation'], f"{CITY}, {REGIONNAME}")
            if distance == "bad request":
                continue
            distance = f"*Distance*: {str(round(distance, 2))} km away"
        except Exception as err_dist:
            print(err_dist)
            distance = ""

        markdown = f"""
*{listing['name']}*

{distance}
*Location*: {listing['sellerLocation']}
*Seller Name*: {listing['sellerName']}
*Current Price*: {listing['currentPrice']}

*URL*: https://www.facebook.com/marketplace/item/{listing['id']}"""

        data[query].append(listing)
        curList.append(listing)

    with open("../response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    if "data.csv" not in os.listdir():
        with open("../data.csv", "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "name",
                "sellerName",
                "sellerLocation",
                "currentPrice",
                "primaryPhotoURL",
            ])

    with open("../data.csv", "a", encoding="utf-8") as f:
        writer = csv.writer(f)
        for listing in curList:
            writer.writerow([
                listing["id"],
                listing["name"],
                listing["sellerName"],
                listing["sellerLocation"],
                listing["currentPrice"],
                listing["primaryPhotoURL"],
            ])

    print(f"Found {len(curList)} new listings for {query}")
    time.sleep(60)
