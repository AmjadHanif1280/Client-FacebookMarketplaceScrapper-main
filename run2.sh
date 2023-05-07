while ! ping -c1 google.com &>/dev/null; do sleep 1; done

clear

echo "System has finished rebooting"
echo "Installing Virtualenv, and requirements!"
cd ~/ || exit
apt install python3.10-venv -y
sudo apt --fix-broken install -y
sudo apt update && sudo apt upgrade -y
python3 -m venv venv
cd ~/Client-FacebookMarketplaceScrapper || exit
source venv/bin/activate
pip install pypandoc
pip install -r requirements.txt

clear

echo "Copying start_screens.sh to /etc/init.d directory"
sudo cp start_screens.sh /etc/init.d/
sudo update-rc.d start_screens.sh defaults
sudo chmod +x /etc/init.d/start_screens.sh
echo "[Unit]
Description=Start Screens

[Service]
ExecStart=/etc/init.d/start_screens.sh
Type=oneshot
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/start_screens.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable start_screens.service

clear

sudo systemctl status start_screens.service | grep 'Loaded: loaded' && echo "start_screens.service is working" || echo "start_screens.service is not working"

sleep 1

sudo
cd ~/Client-FacebookMarketplaceScrapper || exit

echo "Running Telegram Bot on Separate Screen"
screen -dmSL telegram_bot bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python Telegram-Bot.py; exec sh'

echo "Running Marketplace API on Separate Screen"
screen -dmSL Marketplace_API bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceAPI.py; exec sh'

echo "Running MarketplaceBot on Separate Screen"
screen -dmSL Marketplace_Bot bash -c 'cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceBot.py; exec sh'

sleep 5

echo 'alias refresh="killall screen && sleep 2 && screen -dmSL telegram_bot bash -c '\''cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python Telegram-Bot.py; exec sh'\'' && screen -dmSL Marketplace_API bash -c '\''cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceAPI.py; exec sh'\'' && screen -dmSL Marketplace_Bot bash -c '\''cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceBot.py; exec sh'\''" && alias start="screen -dmSL telegram_bot bash -c '\''cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python Telegram-Bot.py; exec sh'\'' && screen -dmSL Marketplace_API bash -c '\''cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceAPI.py; exec sh'\'' && screen -dmSL Marketplace_Bot bash -c '\''cd ~/Client-FacebookMarketplaceScrapper/ && ([ ! -d "venv" ] && python3 -m venv venv || true) && source venv/bin/activate && pip install pypandoc && pip install -r requirements.txt && python MarketplaceBot.py; exec sh'\''"' >> ~/.bashrc
# shellcheck disable=SC1090
source ~/.bashrc
echo "Successfully started all scripts!"

sleep 5

clear
# if you want to stop: pkill -f python
# or killall python
#
# kill screen: screen -X -S my_screen quit
# or to kill all screens: killall screen