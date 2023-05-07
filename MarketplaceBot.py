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
from helpers.grab_ip import get_ip

config_vars = load_config()
globals().update(config_vars)


# TODO: get rid of this monstrosity 😎
def get_usage(status: str, sleep_time: str) -> None:
    """
    Update the usage status message in the specified Telegram channel.

    :param status: The status of the bot and scrapper, either "online" or "sleeping"
    :param sleep_time: The remaining time until the bot wakes up
    """
    # Prepare timezones for display
    est = pytz.timezone("US/Eastern")

    # Generate status message text
    text = (
        f"""
Telegram Bot: **🟢 Online!**
Scrapper: **🟢 Online!**

*Last Updated at:*
- {datetime.now(victoria).strftime('%I:%M:%S %p %Z, %b %d, %Y')}
- {datetime.now(est).strftime('%I:%M:%S %p %Z, %b %d, %Y')}"""
        if status == "online"
        else f"""
Telegram Bot: **🟢 Online!**
Scrapper: **💤 Sleeping!**

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


def discord_webhook(messageType: str = None, message: str = None) -> None:
    """
    Send a message to the Discord webhook.

    :param messageType: Optional type of message to send (e.g. "Error", "Message")
    :param message: Optional message to send
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
        discord_webhook("Error")
    except Exception as temp_err:
        discord_webhook("Error")
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
            discord_webhook("Error")
            return "bad request"

    return geodesic(location1.point, location2.point).kilometers


def error_handler() -> None:
    """
    Send an error message to the Telegram developer channel with the
    traceback information of the exception raised.
    """
    message = f" * An exception was raised! *\n\n```python\n {traceback.format_exc()} ```\n\n\n"
    try:
        discord_webhook("Error")
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={DEV_CHANNEL}&text={message}&parse_mode=Markdown",
            timeout=None,
        )
    except Exception as e:
        discord_webhook("Error")
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
    ) else discord_webhook("Error") and print(
        "ERROR SENDING IMAGE TO TELEGRAM CHANNEL!"
    )


def time_until_6am_melbourne() -> str:
    """
    Calculate the time remaining until 6 AM in Melbourne timezone.

    :return: Time remaining until 6 AM in Melbourne as a formatted string
    """
    vicTZ_temp = pytz.timezone("Australia/Victoria")
    nowTZ_temp = datetime.now(vicTZ_temp)
    six_am = nowTZ_temp.replace(hour=6, minute=0, second=0, microsecond=0)
    return (
        str(six_am - nowTZ_temp).split(".")[0]
        if six_am > nowTZ_temp
        else str(six_am + timedelta(days=1) - nowTZ_temp).split(".")[0]
    )


signal.signal(signal.SIGINT, handler)

while True:
    # check if time is between 6am and 10pm in Melbourne
    victoria = pytz.timezone("Australia/Victoria")
    try:
        # make sure in right directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        config = json.load(open("config.json", encoding="utf-8"))
        queries = [query.lstrip() for query in config["queries"]["title_include"]]
        title_exclude = [query.lstrip() for query in config["queries"]["title_exclude"]]
        get_usage("online", sleep_time="0")
        for query in queries:
            try:
                query = query.lstrip()
                query = query.replace(" ", "+")
                ip = get_ip()
                url = f"http://{ip}:5000/search?locationLatitude={LAT}&locationLongitude={LON}&listingQuery={query}"
                print(f"URL: {url}")  # Add this line to print the URL
                resp = requests.get(url, timeout=None).json()
            except Exception as err1:
                try:
                    with contextlib.suppress(Exception):
                        discord_webhook(message=resp.text)
                except Exception as err2:
                    with contextlib.suppress(Exception):
                        discord_webhook(message=resp)
                print(err1)
                discord_webhook("Error")
                print("Error: API request failed")
                continue

            data = (
                json.load(open("response.json", encoding="utf-8"))
                if os.path.exists("response.json")
                else {}
            )

            if query not in data:
                data[query] = []

            curList = []
            for listing in resp["data"]["listingPages"][0]["listings"]:
                # Checks the following:
                # 1. If the listing is in the exclude list in the file "config.json"
                # 2. If the listing is already in the results from the API call
                # 3. If the listing is already in the current list of results (curList)
                # 4. If the listing is already in the data dictionary (data[query]) (data = response.json)
                if (
                    any(
                        excluder in listing["name"].lower()
                        for excluder in title_exclude
                    )
                    or any(result["id"] == listing["id"] for result in data[query])
                    or any(listing["id"] == result["id"] for result in curList)
                    or any(listing["id"] in result["id"] for result in data[query])
                ):
                    print(
                        f"Missed {listing['name']}.\nReason: Already in results or excluded."
                        f"URL: https://www.facebook.com/marketplace/item/{listing['id']}"
                    )
                    continue

                markdown = f"""
        *{listing['name']}*

        *Distance*: {round(calculate_distance(listing['sellerLocation'], f"{CITY}, {REGIONNAME}"), 2)} km away
        *Location*: {listing['sellerLocation']}
        *Seller Name*: {listing['sellerName']}
        *Current Price*: {listing['currentPrice']}

        *URL*: https://www.facebook.com/marketplace/item/{listing['id']}"""
                send_markdown_img(markdown.encode(), listing["primaryPhotoURL"])
                # save the markdown and image to a folder called "results" if there is stuff in the files just
                # append to it: FileNotFoundError: [Errno 2] No such file or directory:
                # 'results/548182787240837.md':

                data[query].append(listing)
                curList.append(listing)

            with open("response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            if "data.csv" not in os.listdir():
                with open("data.csv", "w", encoding="utf-8") as f:
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

            with open("data.csv", "a", encoding="utf-8") as f:
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
            _query = query.replace("+", " ")
            print(f"Found {len(curList)} new listings for {_query}")

            time.sleep(60)
    except Exception as e:
        print(e)
        discord_webhook("Error")
