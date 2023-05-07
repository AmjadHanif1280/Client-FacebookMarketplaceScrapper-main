"""
This was a total failure ignore this file - Aidan (05/03/2023)
"""
import json

from telegram_bot.custom_bot import CustomBot

with open("../config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

token = config["telegram_bot_api"]
dev_id = config["dev_channel_id"]
announcement_channel = config["channel_id"]

bot = CustomBot(token, dev_id, announcement_channel)
bot.main()
