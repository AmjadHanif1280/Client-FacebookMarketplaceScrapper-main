from flask import Flask, request

import MarketplaceScraper
from helpers.grab_ip import get_ip

app = Flask(__name__)


@app.route("/locations", methods=["GET"])
def locations():
    if locationQuery := request.args.get("locationQuery"):
        status, error, data = MarketplaceScraper.getLocations(
            locationQuery=locationQuery
        )
        return {"status": status, "error": error, "data": data}
    return {
        "status": "Failure",
        "error": {"source": "User", "message": "Missing required parameter"},
    }


@app.route("/search", methods=["GET"])
def search():
    listingQuery = request.args.get("listingQuery")
    locationLatitude = request.args.get("locationLatitude")
    locationLongitude = request.args.get("locationLongitude")
    if all((locationLatitude, locationLongitude, listingQuery)):
        # replace the + with a space
        listingQuery = listingQuery.replace("+", " ")
        status, error, data = MarketplaceScraper.getListings(
            locationLatitude=locationLatitude,
            locationLongitude=locationLongitude,
            listingQuery=listingQuery,
        )
        return {"status": status, "error": error, "data": data}
    return {
        "status": "Failure",
        "error": {"source": "User", "message": "Missing required parameter(s)"},
    }


if __name__ == "__main__":
    app.run(host=get_ip(), port=5000)  # ip:port, where port = 5000 by default
