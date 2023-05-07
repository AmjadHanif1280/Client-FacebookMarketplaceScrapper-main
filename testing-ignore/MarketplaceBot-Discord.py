"""
This was a total failure ignore this file - Aidan (05/03/2023)
"""
import csv
import json
import logging
import os
import subprocess
import time
import traceback
from datetime import datetime, timezone

import pytz
import requests
import schedule
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

config = json.load(open("../config.json", "r", encoding="utf-8"))
GH_TOKEN = config["github"]["token"]
DEV_CHANNEL = config["telegram"]["dev_channel_id"]
TOKEN = config["telegram"]["telegram_bot_api"]
CHANNEL_ID = config["telegram"]["channel_id"]
IP = config["network"]["ip"]
SCRAPING_BEE_API_KEY = config["scraping_bee"]["api_key"]
PORT = config["network"]["port"]
CHANNEL = config["telegram"]["message_relay_channel_id"]
WEBHOOK_URL = config["discord"]["webhook_url"]
PARSE_MODE = "Markdown"


def get_usage():
    response = requests.get(
        "https://app.scrapingbee.com/api/v1/usage",
        params={"api_key": SCRAPING_BEE_API_KEY},
        timeout=None,
    ).json()
    tz = pytz.timezone("Australia/Victoria")

    session = requests.Session()
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    data = {
        "chat_id": CHANNEL,
        "message_id": 49,
        "text": f"*Max Credits:* {response['max_api_credit']}\n*Used Credits:* {response['used_api_credit']}\n*Credits Left:* {int(response['max_api_credit']) - int(response['used_api_credit'])}\n\n*Last Updated at:* {datetime.now(tz).strftime('%I:%M:%S %p %Z')}",
        "parse_mode": PARSE_MODE,
    }

    session.post(url, data=data, timeout=None).json()


def check_for_updates():
    user = "livxy"
    repo = "Client-FacebookMarketplaceScrapper"
    token = GH_TOKEN
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(
        f"https://api.github.com/repos/{user}/{repo}/commits",
        headers=headers,
        timeout=None,
    )
    data = response.json()
    local_copy_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    if data[0]["sha"] != local_copy_sha:
        subprocess.run(["git", "pull"], check=True)


def calculate_distance(location1: str, location2: str) -> float:
    geolocator = Nominatim(user_agent="my_email@myserver.com")
    location1 = geolocator.geocode(location1)
    location2 = geolocator.geocode(location2)
    return geodesic(location1.point, location2.point).kilometers


def error_handler():
    message = f" * An exception was raised! *\n\n```python\n {traceback.format_exc()} ```\n\n\n"
    try:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={DEV_CHANNEL}&text={message}&parse_mode=Markdown",
            timeout=None,
        )
    except Exception as error:
        print(error)


def send_discord_msg(
    name: str,
    distance: float,
    location: str,
    sellerName: str,
    currentPrice: str,
    url: str,
    img: str,
) -> None:
    embed = {
        "title": name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description": "New listing found!",
        "url": url,
        "color": 0x00FF00,
        "image": {"url": img},
        "footer": {
            "text": f"Distance: {distance}km | Location: {location} | Seller: {sellerName} | Price: {currentPrice}"
        },
        "author": {
            "name": "Marketplace Bot",
            "icon_url": "https://du2ha4sdmc25q.cloudfront.net/abhay557/botwebsite/src_PLPmpY9AuMa6WEpt3NDQofU4L5FRjXYBME4m/www/img/logo.png",
        },
        "fields": [
            {"name": "Distance", "value": f"{distance}km", "inline": True},
            {"name": "Location", "value": location, "inline": True},
            {"name": "Seller", "value": sellerName, "inline": True},
            {"name": "Price", "value": currentPrice, "inline": True},
        ],
    }

    data = {
        "username": "Marketplace Bot",
        "avatar_url": "https://cdn.patchbot.io/images/patchbot-logo-400x400.webp",
        "embeds": [embed],
    }

    response = requests.post(WEBHOOK_URL, json=data, timeout=None)


# skipcq: PTC-W0063
ip = requests.get("https://api.ipify.org", timeout=None).text

response = requests.get(f"http://ip-api.com/json/{ip}", timeout=None).json()

lat, long, regionName, city = (
    response["lat"],
    response["lon"],
    response["regionName"],
    response["city"],
)

schedule.every(60).minutes.do(check_for_updates)

while True:
    schedule.run_pending()
    if not os.path.exists("../response.json"):
        input("-")
    config = json.load(open("../config.json", "r", encoding="utf-8"))
    queries = [query.lstrip() for query in config["queries"]["title_include"]]

    for query in queries:
        # TODO: Self-hosted API:
        # resp = requests.get(f"http://{IP}:{PORT}/search?locationLatitude={lat}&locationLongitude={long}&listingQuery={query.lstrip()}").json()

        resp = requests.get(
            f"https://Client-API.aidan4043.repl.co/search?locationLatitude={lat}&locationLongitude={long}&listingQuery={query.lstrip()}",
            timeout=None,
        ).json()

        if not resp:
            print("Error: API request failed")

        data = (
            json.load(open("../response.json", "r", encoding="utf-8"))
            if os.path.exists("../response.json")
            else {}
        )

        if query not in data:
            data[query] = []

        curList = []
        for listing in resp["data"]["listingPages"][0]["listings"][:-1]:
            if listing["name"] in config["queries"]["title_exclude"] or any(
                result["id"] == listing["id"] for result in data[query]
            ):
                continue
            if any(listing["id"] == result["id"] for result in curList):
                continue

            # check if listing["id"] is anywhere in the data file if so, continue
            if any(listing["id"] in result["id"] for result in data[query]):
                continue
            send_discord_msg(
                name=listing["name"],
                distance=round(
                    calculate_distance(
                        listing["sellerLocation"], f"{city}, {regionName}"
                    ),
                    2,
                ),
                location=listing["sellerLocation"],
                sellerName=listing["sellerName"],
                currentPrice=listing["currentPrice"],
                url=f"https://www.facebook.com/marketplace/item/{listing['id']}",
                img=listing["primaryPhotoURL"],
            )

            data[query].append(listing)
            curList.append(listing)

        with open("../response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        if "data.csv" not in os.listdir():
            with open("../data.csv", "w", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "id",
                        "name",
                        "sellerName",
                        "sellerLocation",
                        "currentPrice",
                        "primaryPhotoURL",
                    ]
                )

        with open("../data.csv", "a", encoding="utf-8") as f:
            writer = csv.writer(f)
            for listing in curList:
                writer.writerow(
                    [
                        listing["id"],
                        listing["name"],
                        listing["sellerName"],
                        listing["sellerLocation"],
                        listing["currentPrice"],
                        listing["primaryPhotoURL"],
                    ]
                )

        print(f"Found {len(curList)} new listings for {query}")

        get_usage()
        time.sleep(60)
