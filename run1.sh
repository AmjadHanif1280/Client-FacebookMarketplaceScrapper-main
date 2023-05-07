# TODO: FIRST:
#
# git clone "https://livxy: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@github.com/livxy/Client-FacebookMarketplaceScrapper.git" ~/Client-FacebookMarketplaceScrapper
# sudo apt update && sudo apt install nano -y && sudo apt upgrade -y && sudo apt dist-upgrade -y && reboot
# TODO: REBOOTS HERE:
# clear && echo "Fixing dpkg error" && cd /var/lib/dpkg && sudo mv info info.bak && sudo mkdir info && sudo apt-get upgrade -y && cd ~
# cd ~/Client-FacebookMarketplaceScrapper && chmod +x run1.sh run2.sh start_screens.sh
# ./run1.sh
# after reboot:
# ./run2.sh
#
# if error:
clear
echo "Fixing dpkg error"
cd /var/lib/dpkg || exit
sudo mv info info.bak
sudo mkdir info
sudo apt-get upgrade -y
cd ~ || exit

clear
echo "Updating packages"
sudo apt-get update
sudo apt-get upgrade -y
clear

echo "Installing Python 3.11"
sudo apt-get install -y python3.11
sudo apt-get update
curl "https://bootstrap.pypa.io/get-pip.py" -o get-pip.py
python3.11 get-pip.py
alias python=python3.11
alias python3=python3.11
sudo apt install -y python-is-python3
sudo apt-get update
sudo apt-get install -y python3-pip
pip install --upgrade pip
pip install pypandoc
pip install -r requirements.txt --force-reinstall
clear

echo "Installing virtualenv"
pip install virtualenv
apt install python3.10-venv -y --no-upgrade
apt update && apt upgrade -y
echo "Rebooting the system"
reboot