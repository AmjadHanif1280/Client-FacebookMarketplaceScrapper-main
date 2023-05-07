#!/bin/bash

cd ~/Client-FacebookMarketplaceScrapper || exit

echo "Running Telegram Bot on Separate Screen"
screen -dmSL telegram_bot bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python Telegram-Bot.py; exec sh'


echo "Running Marketplace API on Separate Screen"
screen -dmSL Marketplace_API bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceAPI.py; exec sh'


echo "Running MarketplaceBot on Separate Screen"
screen -dmSL Marketplace_Bot bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceBot.py; exec sh'

