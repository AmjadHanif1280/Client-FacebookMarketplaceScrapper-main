"""
This was a total failure ignore this file - Aidan (05/03/2023)
"""
import contextlib
import csv
import os
import re
import signal
import time
import traceback
from datetime import datetime, timedelta
from typing import Any

import pytz
import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

from helpers.cfg_loader import *

config_vars = load_config()
globals().update(config_vars)


def get_usage(status: str, sleep_time: str) -> None:
    """
    Update the usage status message in the specified Telegram channel.

    :param status: The status of the bot and scrapper, either "online" or "sleeping"
    :param sleep_time: The remaining time until the bot wakes up
    """
    # Get usage data from the ScrapingBee API
    response = requests.get(
        "https://app.scrapingbee.com/api/v1/usage",
        params={"api_key": SCRAPING_BEE_API_KEY},
        timeout=None,
    ).json()

    # Prepare timezones for display
    est = pytz.timezone("US/Eastern")
    victoria = pytz.timezone("Australia/Victoria")
    # Generate status message text
    text = (
        f"""
Telegram Bot: **🟢 Online!**
Scrapper: **🟢 Online!**

*Max Credits:* {response['max_api_credit']}
*Used Credits:* {response['used_api_credit']}
*Credits Left:* {int(response['max_api_credit']) - int(response['used_api_credit'])}


*Last Updated at:*
- {datetime.now(victoria).strftime('%I:%M:%S %p %Z, %b %d, %Y')}
- {datetime.now(est).strftime('%I:%M:%S %p %Z, %b %d, %Y')}"""
        if status == "online"
        else f"""
Telegram Bot: **🟢 Online!**
Scrapper: **💤 Sleeping!**

*Max Credits:* {response['max_api_credit']}
*Used Credits:* {response['used_api_credit']}
*Credits Left:* {int(response['max_api_credit']) - int(response['used_api_credit'])}

{sleep_time} until I wake up!

*Last Updated at:*
- {datetime.now(victoria).strftime('%I:%M:%S %p %Z, %b %d, %Y')}
- {datetime.now(est).strftime('%I:%M:%S %p %Z, %b %d, %Y')}"""
    )

    # Send the updated message
    session = requests.Session()
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    editMessageTextData = {
        "chat_id": CHANNEL,
        "message_id": 49,
        "text": text,
        "parse_mode": PARSE_MODE,
    }

    session.post(url, data=editMessageTextData, timeout=None).json()


def discord_webhook(
    messageType: str = None, message: str = None, DEV: bool = False
) -> None:
    """
    Send a message to the Discord webhook.

    :param messageType: Optional type of message to send (e.g. "Error", "Message") (default: None)
    :param message: Optional message to send (default: None)
    :param DEV: Optional flag to send the message to the development channel (default: False)
    """
    est = pytz.timezone("US/Eastern")
    if messageType == "Error":
        message = f"""
Current Time: `{datetime.now(est).strftime('%I:%M:%S %p %Z, %b %d, %Y')}`

_Error Message:_
```{traceback.format_exc()}```
        """
    elif messageType == "Message":
        message = f"""
Current Time: `{datetime.now(est).strftime('%I:%M:%S %p %Z, %b %d, %Y')}`
Message: 
```{message}```
        """
    if DEV:
        webhook_url = (
            "https://discord.com/api/webhooks/1097958108518699090"
            "/g1qqCPQt5awLb4gp_PmSayky80gkIqkKZxv9iWDm7Qme76HMZmvkhy6YorqJJhp9XcLN"
        )
    else:
        webhook_url = (
            "https://discord.com/api/webhooks/1096567273256390737/Pe05i9FG_N1iZC8XNoHesl-I88kNeE7lmEC_bNWK-x"
            "-A5Hf65XfjZD22B8Cnexy8T5XO"
        )
    temp_data = {"content": message}
    requests.post(
        webhook_url,
        data=json.dumps(temp_data),
        headers={"Content-Type": "application/json"},
    )
    return None


def handler(signum, frame) -> None:
    """
    Signal handler function for handling exceptions and updating the
    status message in the specified Telegram channel.

    :param signum: Signal number
    :param frame: Frame object
    """
    temp_vic = pytz.timezone("Australia/Victoria")
    est = pytz.timezone("US/Eastern")
    session = requests.Session()

    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    editMessageTextData = {
        "chat_id": CHANNEL,
        "message_id": 49,
        "text": f"""
Telegram Bot: **🔴 Offline**
Scrapper: **🔴 Offline**

*Last Updated at:*
- {datetime.now(temp_vic).strftime('%I:%M:%S %p %Z, %b %d, %Y')}
- {datetime.now(est).strftime('%I:%M:%S %p %Z, %b %d, %Y')}

_Error Message:_
```{traceback.format_exc()}```

Sorry for the inconvenience, I will be back online soon!""",
        "parse_mode": PARSE_MODE,
    }

    try:
        session.post(url, data=editMessageTextData, timeout=None).json()
        discord_webhook("Error", DEV=True)
    except Exception as temp_err:
        discord_webhook("Error", DEV=True)
        print(temp_err)
    finally:
        pass


def calculate_distance(location1: str, location2: str) -> str | Any:
    """
    Calculate the distance between two locations using the geodesic distance.

    :param location1: First location
    :param location2: Second location
    :return: Distance between the two locations in kilometers
    """
    while True:
        try:
            geolocator = Nominatim(
                user_agent="my_email@myserver.com", timeout=100, scheme="http"
            )
            location1 = geolocator.geocode(location1)
            location2 = geolocator.geocode(location2)
            break
        except Exception as calc_err:
            print(calc_err)
            discord_webhook("Error", DEV=True)
            return "bad request"

    return geodesic(location1.point, location2.point).kilometers


def error_handler() -> None:
    """
    Send an error message to the Telegram developer channel with the
    traceback information of the exception raised.
    """
    message = f" * An exception was raised! *\n\n```python\n {traceback.format_exc()} ```\n\n\n"
    try:
        discord_webhook("Error", DEV=True)
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={DEV_CHANNEL}&text={message}&parse_mode=Markdown",
            timeout=None,
        )
    except Exception as e:
        discord_webhook("Error", DEV=True)
        print(e)


def send_markdown_img(markdown: str, img: str) -> None:
    """
    Send an image with a markdown caption to the Telegram channel.

    :param markdown: The markdown caption text
    :param img: The image URL
    """

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    params = {
        "chat_id": CHANNEL_ID,
        "caption": markdown,
        "parse_mode": "Markdown",
        "photo": img,
    }
    response = requests.post(url, params=params, timeout=None)
    print("SUCCESSFULLY SENT IMAGE TO TELEGRAM CHANNEL!") if re.search(
        r'{"ok":true', response.text
    ) else discord_webhook("Error", DEV=True) and print(
        "ERROR SENDING IMAGE TO TELEGRAM CHANNEL!"
    )


def time_until_6am_melbourne() -> str:
    """
    Calculate the time remaining until 6 AM in Melbourne timezone.

    :return: Time remaining until 6 AM in Melbourne as a formatted string
    """
    vicTZ_temp = pytz.timezone("Australia/Victoria")
    nowTZ_temp = datetime.now(vicTZ_temp)
    tomorrow = nowTZ_temp + timedelta(days=1)
    six_am = tomorrow.replace(hour=6, minute=0, second=0, microsecond=0)
    return str(six_am - nowTZ_temp)


signal.signal(signal.SIGINT, handler)

while True:
    # check if time is between 6am and 10pm in Melbourne
    # victoria = pytz.timezone("Australia/Victoria")
    # if 6 <= datetime.now(victoria).hour < 22:
    try:
        if not os.path.exists("DEV_files/responseDEV.json"):
            with open("DEV_files/responseDEV.json", "w") as f:
                json.dump({}, f, indent=4)
        config = json.load(open("DEV_files/configDEV.json", encoding="utf-8"))
        queries = [query.lstrip() for query in config["queries"]["title_include"]]
        title_exclude = [query.lstrip() for query in config["queries"]["title_exclude"]]
        for query in queries:
            try:
                resp = requests.get(
                    f"https://dev-fb-mk-bot.aidan4043.repl.co/search?locationLatitude={LAT}&locationLongitude={LON}"
                    f"&listingQuery={query.lstrip()}",
                    timeout=None,
                ).json()
            except Exception as err1:
                try:
                    with contextlib.suppress(Exception):
                        discord_webhook(message=resp.text, DEV=True)
                except Exception as err2:
                    with contextlib.suppress(Exception):
                        discord_webhook(message=resp, DEV=True)
                print(err1)
                discord_webhook("Error", DEV=True)
                print("Error: API request failed")
                continue

            data = (
                json.load(open("DEV_files/responseDEV.json", encoding="utf-8"))
                if os.path.exists("DEV_files/responseDEV.json")
                else {}
            )

            if query not in data:
                data[query] = []

            curList = []
            for listing in resp["data"]["listingPages"][0]["listings"]:
                if any(
                    excluder in listing["name"].lower() for excluder in title_exclude
                ) or any(result["id"] == listing["id"] for result in data[query]):
                    if "excluded-dataDEV.csv" not in os.listdir("DEV_files"):
                        with open("excluded-dataDEV.csv", "w", encoding="utf-8") as f:
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
                            continue

                    with open("excluded-dataDEV.csv", "a", encoding="utf-8") as f:
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
                    continue

                if any(listing["id"] == result["id"] for result in curList):
                    continue

                # check if listing["id"] is anywhere in the data file if so, continue
                if any(listing["id"] in result["id"] for result in data[query]):
                    continue

                # check if name is in the title_exclude list if so, continue
                if listing["name"] in title_exclude:
                    continue

                markdown = f"""
    *{listing['name']}*

    *Distance*: {round(calculate_distance(listing['sellerLocation'], f"{CITY}, {REGIONNAME}"), 2)} km away
    *Location*: {listing['sellerLocation']}
    *Seller Name*: {listing['sellerName']}
    *Current Price*: {listing['currentPrice']}

    *URL*: https://www.facebook.com/marketplace/item/{listing['id']}"""
                # save the markdown and image to a folder called "results" if there is stuff in the files just
                # append to it: FileNotFoundError: [Errno 2] No such file or directory:
                # 'results/548182787240837.md':

                discord_webhook(message=markdown, DEV=True)

                data[query].append(listing)
                curList.append(listing)

            with open("DEV_files/responseDEV.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            if "dataDEV.csv" not in os.listdir("DEV_files"):
                with open("DEV_files/dataDEV.csv", "w", encoding="utf-8") as f:
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

            with open("DEV_files/dataDEV.csv", "a", encoding="utf-8") as f:
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

            time.sleep(60)
    except Exception as e:
        print(e)
        discord_webhook("Error", DEV=True)
