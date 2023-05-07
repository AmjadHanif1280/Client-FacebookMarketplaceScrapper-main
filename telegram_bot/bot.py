import requests


# Channels:
#
# -1001856935845 Facebook Marketplace Scrapper
# -1001861947909 dev channel FB MK bot
#
# https://api.telegram.org/bot5903919928:AAG_ty7EFMPuW6q2b06cFnn_v4Stg0sd2vc/sendMessage?chat_id={CHANNEL}&text={text}

status = "Online"


def activity(status):
    if status == "Online":
        status = "Online 🟢"
    elif status == "Offline":
        status = "Offline 🔴"
    else:
        status = "Unknown"
    return status


text = f"""
* Status: {activity(status)} *

[ ‏ ](https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NHx8Y2Fyc3xlbnwwfHwwfHw%3D&w=1000&q=80)
"""


class TelegramBot:
    def __init__(self, token, channel, parse_mode, status):
        self.token = token
        self.channel = channel
        self.parse_mode = parse_mode
        self.status = status

    def send_message(self, text):
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.channel}&text={text}&parse_mode={self.parse_mode}"
        )

    def send_photo(self, photo):
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendPhoto?chat_id={self.channel}&photo={photo}&parse_mode={self.parse_mode}"
        )

    def send_video(self, video):
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendVideo?chat_id={self.channel}&video={video}&parse_mode={self.parse_mode}"
        )

    def send_audio(self, audio):
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendAudio?chat_id={self.channel}&audio={audio}&parse_mode={self.parse_mode}"
        )

    def send_document(self, document):
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendDocument?chat_id={self.channel}&document={document}&parse_mode={self.parse_mode}"
        )

    def send_sticker(self, sticker):
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendSticker?chat_id={self.channel}&sticker={sticker}&parse_mode={self.parse_mode}"
        )

    @staticmethod
    def activity(status):
        if status == "Online":
            status = "Online 🟢"
        elif status == "Offline":
            status = "Offline 🔴"
        else:
            status = "Unknown"
        return status
