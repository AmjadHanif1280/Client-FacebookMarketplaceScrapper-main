"""
WARNING: this is awful code, but it works... for now. - Aidan (05/03/2023)
"""

import json

# Define global variables
GH_TOKEN = None
DEV_CHANNEL = None
TOKEN = None
CHANNEL_ID = None
IP = None
SCRAPING_BEE_API_KEY = None
PORT = None
CHANNEL = None
PARSE_MODE = None
LAT = None
LON = None
REGIONNAME = None
CITY = None
GRAPHQL_URL = None
GRAPHQL_HEADERS = None
SCRAPING_BEE_PARAMS = None


def load_config() -> dict:
    """ Loads the configuration file and returns a dictionary of the configuration

    :return: dict - configuration file as a dictionary object
    """
    # Load configuration
    config = json.load(open("/root/Client-FacebookMarketplaceScrapper/config.json", encoding="utf-8"))
    return {
        "GH_TOKEN": config["github"]["token"],
        "DEV_CHANNEL": config["telegram"]["dev_channel_id"],
        "TOKEN": config["telegram"]["telegram_bot_api"],
        "CHANNEL_ID": config["telegram"]["channel_id"],
        "IP": config["network"]["ip"],
        "SCRAPING_BEE_API_KEY": config["scraping_bee"]["api_key"],
        "PORT": config["network"]["port"],
        "CHANNEL": config["telegram"]["message_relay_channel_id"],
        "PARSE_MODE": "Markdown",
        "LAT": config["PERSONALINFO"]["lat"],
        "LON": config["PERSONALINFO"]["lon"],
        "REGIONNAME": config["PERSONALINFO"]["regionName"],
        "CITY": config["PERSONALINFO"]["city"],
        "GRAPHQL_URL": "https://www.facebook.com/api/graphql/",
        "GRAPHQL_HEADERS": {
            "Spb-sec-fetch-site": "same-origin",
            "Spb-user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/99.0.4844.74 Safari/537.36",
        },
        "SCRAPING_BEE_PARAMS": {
            "api_key": config["scraping_bee"]["api_key"],
            "url": "https://www.facebook.com/api/graphql/",
            "render_js": "false",
            "forward_headers": "true",
        },
    }
