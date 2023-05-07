
# Facebook Marketplace Scrapper by Aidan

This is an advanced and extremely poor way of programming, but it is used for my own research + getting deals on Facebook Marketplace, and then sharing all the new results to Telegram for visibility.
## Install `Client-FacebookMarketplaceScrapper`:
(needs [Python 3.10.x or higher](https://www.python.org/downloads/))

```bash
  git clone https://github.com/livxy/Client-FacebookMarketplaceScrapper.git 
  cd Client-FacebookMarketplaceScrapper
  
  python3 -m venv
  pip3 install requirements.txt
```

### Config Settings
From there please edit the `config.json` file to suit your needs:

- Replace `lat` for your latitude, `lon` for your longitude, then `regionName` (country), and `city` as the city

- Replace `telegram_bot_api` for your [Telegram bot API Key](https://www.cytron.io/tutorial/how-to-create-a-telegram-bot-get-the-api-key-and-chat-id), the `channel_id` for a [Telegram Channel's ID](https://community.caribbean.dev/t/get-the-telegram-channel-id/427) that you want to receive the results in, replace the `dev_channel_id` for a new [Channel ID](https://community.caribbean.dev/t/get-the-telegram-channel-id/427) that you want to use to receive errors.

- Replace the `resultsOptions` with the following values (depending on your needs):
 ```
 query_count   :

       1 - 24 results


 date_option   :

       1 (last 24 hours),

       2 (last 7 days),

       3 (last 30 days),


 filter_radius :

       1 (km = <1 mi),

       2 (km = 1 mi),

       5 (km = 3 mi),

      10 (km = 6 mi),

      20 (km = 12 mi),

      40 (km = 25 mi),

      60 (km = 37 mi),

      80 (km = 50 mi),

     100 (km = 62 mi),

     250 (km = 155 mi),

     500 (km = 311 mi)
```

- Ignore the `allow_duplicates`, it's used for having multiple `title_include` values. Replace the `title_include` with any of the queries you want to search for... Replace the `title_exclude` for anything you do not want in your searches.

#### Example
```json
{
    "PERSONALINFO": {
        "lat": "-37.8411",
        "lon": "144.9799",
        "regionName": "Victoria",
        "city": "Melbourne"
    },
    "telegram": {
        "telegram_bot_api": "5903919928:AAG_ty7EFMPuW6q2b06cFnn_v4Stg0sd2vc",
        "channel_id": "-1001856935845",
        "dev_channel_id": "-1001861947909"
    },
    "resultsOptions": {
        "query_count": 2,
        "filter_radius": 250,
        "date_option": 1
    },
    "queries": {
        "allow_duplicates": "True",
        "title_include": [
            " cat",
            " dog"
        ],
        "title_exclude": [
            " rat",
            " fish"
        ]
    }
}
```
## Run Locally

### Windows:

One way of doing this is by separately running each file individually like so:

```bash
  python3 MarketplaceAPI.py
```

```bash
  python3 Telegram-Bot.py
```

```bash
  python3 MarketplaceBot.py
```

### Linux:

I have included a file that I use to quickly set up my servers using [GNU screen](https://www.gnu.org/software/screen/), since this will eventually be a product and I need separate servers for users. If you are using Linux you can try to run the following

**Make sure to change the `~/Client-FacebookMarketplaceScrapper` path to whatever path you downloaded this to, also make sure to already have a `venv` set up.**

```shell
screen -dmSL telegram_bot bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python Telegram-Bot.py; exec sh'
```

```shell
screen -dmSL Marketplace_API bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceAPI.py; exec sh'
```

```shell
screen -dmSL Marketplace_Bot bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceBot.py; exec sh'
```

From there you can simply type `screen -r {name}` where `{name}` can be either "telegram_bot", "Marketplace_API", "Marketplace_Bot". To go back use the keybind <kbd>Ctrl</kbd> <kbd>A</kbd> + <kbd>D</kbd>

And that should be it!