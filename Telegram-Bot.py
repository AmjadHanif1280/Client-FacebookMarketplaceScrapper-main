from telegram_bot.custom_bot import CustomBot
import json

with open("config.json", "r") as f:
    config = json.load(f)
    TOKEN = config["telegram"]["telegram_bot_api"]
    DEV_ID = config["telegram"]["dev_channel_id"]
    ANNOUNCEMENT_CHANNEL = config["telegram"]["channel_id"]

CustomBot = CustomBot(TOKEN, DEV_ID, ANNOUNCEMENT_CHANNEL)
CustomBot.main()
