import copy
import json
import os
import pathlib
import time
from datetime import datetime, timezone
import requests

GRAPHQL_URL = "https://www.facebook.com/api/graphql/"

GRAPHQL_HEADERS = {
    "Spb-sec-fetch-site": "same-origin",
    "Spb-user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
}


def getLocations(locationQuery: str) -> tuple:
    """Get a list of locations from a location query.

    :param locationQuery: (str) The location query.
    :return: (tuple) A tuple containing the status, error, and data.
    """
    data = {}

    requestPayload = {
        "variables": f"""{{
            "params": {{
                "caller": "MARKETPLACE",
                "page_category": ["CITY", "SUBCITY", "NEIGHBORHOOD","POSTAL_CODE"],
                "query": "{locationQuery}"
            }}
        }}""",
        "doc_id": "5585904654783609",
    }

    status, error, facebookResponse = getFacebookResponse(requestPayload)

    if status == "Success":
        data["locations"] = []  # Create a locations object within data
        facebookResponseJSON = json.loads(facebookResponse.text)
        # pylint: disable=E211
        for location in facebookResponseJSON["data"]["city_street_search"][
            "street_results"
        ]["edges"]:
            locationName = location["node"]["subtitle"].split(" \u00b7")[0]

            if locationName == "City":
                locationName = location["node"]["single_line_address"]

            locationLatitude = location["node"]["location"]["latitude"]
            locationLongitude = location["node"]["location"]["longitude"]

            data["locations"].append(
                {
                    "name": locationName,
                    "latitude": str(locationLatitude),
                    "longitude": str(locationLongitude),
                }
            )

    return status, error, data


def getListings(
    locationLatitude, locationLongitude, listingQuery, numPageResults: int = 2
) -> tuple:
    """
    Get a list of listings from a location and listing query.

    :param locationLatitude: The latitude of the location.
    :param locationLongitude: The longitude of the location.
    :param listingQuery: The listing query.
    :param numPageResults: The number of pages of results to get.
    :return: (tuple) A tuple containing the status, error, and data.
    """
    data = {}

    # used for commerce_search_and_rp_ctime_days
    num_days = (
        datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    ).days
    last_24hr = ";".join(f"{num_days - i}" for i in range(2))
    last_7d = ";".join(f"{num_days - i}" for i in range(8))
    last_30d = ";".join(f"{num_days - i}" for i in range(31))
    os.chdir(pathlib.Path(__file__).parent.absolute())
    with open("config.json") as f:
        config = json.load(f)
        options = config["resultsOptions"]
        values = [
            options[key] for key in ["query_count", "filter_radius", "date_option"]
        ]
        if all(isinstance(value, int) and value for value in values):
            queryNum, dateOption, filterRadius = (
                options[key] for key in ["query_count", "filter_radius", "date_option"]
            )
        dateOption = {1: last_24hr, 2: last_7d, 3: last_30d}.get(dateOption, last_24hr)
        # TODO: Add documentation about options
        # * query_count   :
        # *       1 - 24 results
        # *
        # * date_option   :
        # *       1 (last 24 hours),
        # *       2 (last 7 days),
        # *       3 (last 30 days),
        # *
        # * filter_radius :
        # *       1 (km = <1 mi),
        # *       2 (km = 1 mi),
        # *       5 (km = 3 mi),
        # *      10 (km = 6 mi),
        # *      20 (km = 12 mi),
        # *      40 (km = 25 mi),
        # *      60 (km = 37 mi),
        # *      80 (km = 50 mi),
        # *     100 (km = 62 mi),
        # *     250 (km = 155 mi),
        # *     500 (km = 311 mi)

    requestPayload = {
        "variables": f"""{{
            "count":{queryNum},
            "params":{{
                "bqf":{{
                    "callsite":"COMMERCE_MKTPLACE_WWW",
                    "query":"{listingQuery.replace('+', ' ')}"
                }},
                "browse_request_params":{{
                    "commerce_enable_local_pickup":true,
                    "commerce_enable_shipping":true,
                    "commerce_search_and_rp_available":true,
                    "commerce_search_and_rp_condition":null,
                    "commerce_search_and_rp_ctime_days": "{dateOption}",
                    "filter_location_latitude":{locationLatitude},
                    "filter_location_longitude":{locationLongitude},
                    "filter_price_lower_bound":0,
                    "filter_price_upper_bound":214748364700,
                    "filter_radius_km":{filterRadius}
                }},
                "custom_request_params":{{
                    "surface":"SEARCH"
                }}
            }}
        }}""",
        "doc_id": "7111939778879383",
    }

    # 24 hour as of 6:14pm 1/7/2023 - 19364;19363
    # 24 hour as of 7:37pm 1/7/2023 - 19365;19364
    # 7  day as of 6:14pm 1/7/2023 - 19364;19363;19362;19361;19360;19359;19358;19357
    # 30 day as of 6:14pm 1/7/2023 - 19364;19363;19362;19361;19360;19359;
    # 19358;19357;19356;19355;19354;19353;19352;19351;19350;19349;19348;19347;
    # 19346;19345;19344;19343;19342;19341;19340;19339;19338;19337;19336;19335;19334

    status, error, facebookResponse = getFacebookResponse(requestPayload)

    if status != "Success":
        return status, error, data

    facebookResponseJSON = json.loads(facebookResponse.text)

    rawPageResults = [facebookResponseJSON]
    for _ in range(1, numPageResults):
        pageInfo = facebookResponseJSON["data"]["marketplace_search"]["feed_units"][
            "page_info"
        ]

        if pageInfo["has_next_page"]:
            cursor = facebookResponseJSON["data"]["marketplace_search"]["feed_units"][
                "page_info"
            ]["end_cursor"]

            requestPayloadCopy = copy.copy(requestPayload)

            requestPayloadCopy["variables"] = requestPayloadCopy["variables"].split()
            requestPayloadCopy["variables"].insert(1, f""""cursor":'{cursor}',""")
            requestPayloadCopy["variables"] = "".join(requestPayloadCopy["variables"])
            status, error, facebookResponse = getFacebookResponse(requestPayloadCopy)

            if status != "Success":
                return status, error, data

            facebookResponseJSON = json.loads(facebookResponse.text)
            rawPageResults.append(facebookResponseJSON)
    data["listingPages"] = parsePageResults(rawPageResults)
    return status, error, data


def parsePageResults(rawPageResults: list) -> list:
    """
    Parses the raw page results into a more readable format

    :param rawPageResults: The raw page results
    :return: The parsed page results
    """
    listingPages = []
    for pageIndex, rawPageResult in enumerate(rawPageResults):
        # Create a new listings object within the listingPages array
        listingPages.append({"listings": []})

        for listing in rawPageResult["data"]["marketplace_search"]["feed_units"][
            "edges"
        ]:  # If object is a listing
            if listing["node"]["__typename"] == "MarketplaceFeedListingStoryObject":
                listingID = listing["node"]["listing"]["id"]
                listingName = listing["node"]["listing"]["marketplace_listing_title"]
                listingCurrentPrice = listing["node"]["listing"]["listing_price"][
                    "formatted_amount"
                ]

                # If listing has a previous price
                listingPreviousPrice = (
                    listing["node"]["listing"]["strikethrough_price"][
                        "formatted_amount"
                    ]
                    if listing["node"]["listing"]["strikethrough_price"]
                    else ""
                )
                listingSaleIsPending = listing["node"]["listing"]["is_pending"]
                listingPrimaryPhotoURL = listing["node"]["listing"][
                    "primary_listing_photo"
                ]["image"]["uri"]
                sellerName = listing["node"]["listing"]["marketplace_listing_seller"][
                    "name"
                ]
                sellerLocation = listing["node"]["listing"]["location"][
                    "reverse_geocode"
                ]["city_page"]["display_name"]
                sellerType = listing["node"]["listing"]["marketplace_listing_seller"][
                    "__typename"
                ]

                # Add the listing to its corresponding page
                listingPages[pageIndex]["listings"].append(
                    {
                        "id": listingID,
                        "name": listingName,
                        "currentPrice": listingCurrentPrice,
                        "previousPrice": listingPreviousPrice,
                        "saleIsPending": str(listingSaleIsPending).lower(),
                        "primaryPhotoURL": listingPrimaryPhotoURL,
                        "sellerName": sellerName,
                        "sellerLocation": sellerLocation,
                        "sellerType": sellerType,
                    }
                )

    return listingPages


def getFacebookResponse(requestPayload: dict) -> tuple:
    """
    Gets the response from Facebook

    :param requestPayload: (dict) The request payload
    :return: (tuple) The status, error, and response
    """
    status = "Success"
    error = {}

    while True:
        try:
            with open("output.txt", "r", encoding="utf-8") as f:
                proxies = f.read().splitlines()
            if len(proxies) > 3:
                break
            if len(proxies) == 0:
                print("No proxies found")
                print("Retrying...")
                time.sleep(1)
                continue
        except Exception as _e:
            print(f"Error reading proxies: {_e}")
            print("Possibly due to the file being used by another process")
            print("Retrying...")
            time.sleep(1)
            continue

    while True:
        try:
            proxy = {
                "http": "http://user-sphdy6qbal:ZeQnf2x25sVaWdek1z@gate.smartproxy.com:7000",
                "https": "http://user-sphdy6qbal:ZeQnf2x25sVaWdek1z@gate.smartproxy.com:7000",
            }
            facebookResponse = requests.post(
                url="https://www.facebook.com/api/graphql/",
                headers=GRAPHQL_HEADERS,
                data=requestPayload,
                proxies=proxy,
                timeout=None,
            )
            print(facebookResponse.text)
        except requests.exceptions.RequestException as requestError:
            print(f"Request error: {requestError}")
            print("Retrying...")
            continue

        if facebookResponse.status_code == 200:
            facebookResponseJSON = json.loads(facebookResponse.text)

            if facebookResponseJSON.get("errors"):
                print(f"Facebook error: {facebookResponseJSON['errors'][0]['message']}")
                print("Retrying...")
                continue
            if facebookResponseJSON.get("data") is None:
                print("Facebook error: Rate limit exceeded")
                print("Retrying...")
                continue
        else:
            print(f"Status code {facebookResponse.status_code}")
            print("Retrying...")
            continue

        return status, error, facebookResponse


# def main():
#     listingQuery = "iphone"
#     locationLatitude = 37.774929
#     locationLongitude = -122.419418
#     if all((locationLatitude, locationLongitude, listingQuery)):
#         status, error, data = getListings(
#             locationLatitude=locationLatitude,
#             locationLongitude=locationLongitude,
#             listingQuery=listingQuery,
#         )
#         return {"status": status, "error": error, "data": data}
#     return {
#         "status": "Failure",
#         "error": {"source": "User", "message": "Missing required parameter(s)"},
#     }
#
#
# if __name__ == '__main__':
#     import time
#
#     start = time.perf_counter()
#     for _ in range(10):
#         print(main())
#     elapsed = time.perf_counter() - start
#     print(f"{__file__} executed in {elapsed:.9f} seconds.")
