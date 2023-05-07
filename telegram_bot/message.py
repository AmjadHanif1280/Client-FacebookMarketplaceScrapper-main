"""
API Wrapper for Telegram Bot API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic usage:

   >>> from telegram_bot.message import TelegramMessage
   >>> TelegramMessage = TelegramMessage(token, channel, parse_mode, status="Online")
   >>> TelegramMessage.send_message(text)

Define your own class:
    Token: Token of the telegram bot. (Get it from @BotFather)
    Channel: Channel id of the telegram channel. (Get it from @getidsbot)
    Parse Mode: Parse mode of the message. (Markdown, HTML or None)
    Status: Status of the bot. (Online, Offline or None)

Author: @livxy/bruhs/aidan
Github: https://github.com/livxy/

:license: Apache 2.0, see LICENSE for more details.
"""

import requests


class TelegramMessage:
    """
    TelegramMessage class:

    This class is used to send messages to a telegram channel.
    """

    def __init__(self, token, channel, parse_mode, status=None):
        """TelegramMessage class constructor.

        Args:
            token (token): Token of the telegram bot. (Get it from @BotFather)
            channel (channel): Channel id of the telegram channel. (Get it from @getidsbot)
            parse_mode (parse_mode): Parse mode of the message. (Markdown, HTML or None)
            status (status, optional): Status of the bot. Defaults to None. (Online, Offline or None)
        """
        self.token = token
        self.channel = channel
        self.parse_mode = parse_mode
        self.status = status

    def __repr__(self):
        """TelegramMessage class representation.

        Returns:
            str: TelegramMessage class representation.
        """
        return f"TelegramMessage(token={self.token}, channel={self.channel}, parse_mode={self.parse_mode}, status={self.status}, debug={self.debug})"

    def send_message(self, text, optchannel):
        """Send a message to the telegram channel.

        Args:
            text (text): Text of the message.
            optchannel (optchannel): Channel id of the telegram channel. (Get it from @getidsbot)
            parser (parser, optional): Parse mode of the message. (Markdown, HTML or None). Defaults to None.

        Returns:
            bool: True if message sent successfully, False if message failed to send.

        Raises:
            Exception: If the message failed to send.

        Example:
            >>> TelegramMessage = TelegramMessage(token, channel, parse_mode, status="Online")
            >>> TelegramMessage.send_message("Hello World!", channel)
        """
        print(f"Sending message to telegram channel: {optchannel}")
        print(f"Message: {text}")
        print(f"Parse Mode: {self.parse_mode}")
        print(f"Status: {self.status}")
        print(
            f"URL: https://api.telegram.org/bot{self.token}/sendMessage?chat_id={optchannel}&text={text}&parse_mode={self.parse_mode}"
        )
        response = requests.get(
            f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={optchannel}&text={text}&parse_mode={self.parse_mode}"
        ).json()
        print(response)
        if response["ok"] is True:
            print("Message sent successfully!")
            return True
        print(f"Message failed to send!\nError: {response['description']}")
        return False

    def send_photo(self, photo):
        """Send a photo to the telegram channel.

        Args:
            photo (photo): Photo url.
        """
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendPhoto?chat_id={self.channel}&photo={photo}&parse_mode={self.parse_mode}"
        )

    def send_video(self, video):
        """Send a video to the telegram channel.

        Args:
            video (video): Video url.
        """
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendVideo?chat_id={self.channel}&video={video}&parse_mode={self.parse_mode}"
        )

    def send_audio(self, audio):
        """Send an audio to the telegram channel.

        Args:
            audio (audio): Audio url.
        """
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendAudio?chat_id={self.channel}&audio={audio}&parse_mode={self.parse_mode}"
        )

    def send_document(self, document):
        """Send a document to the telegram channel.

        Args:
            document (document): Document url.
        """
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendDocument?chat_id={self.channel}&document={document}&parse_mode={self.parse_mode}"
        )

    def send_sticker(self, sticker):
        """Send a sticker to the telegram channel.

        Args:
            sticker (sticker): Sticker url.
        """
        requests.get(
            f"https://api.telegram.org/bot{self.token}/sendSticker?chat_id={self.channel}&sticker={sticker}&parse_mode={self.parse_mode}"
        )

    @staticmethod
    def activity(status):
        """Send a message to the telegram channel when the bot is online or offline. (Optional)

        Args:
            status (status): Status of the bot. (Online or Offline)

        Returns:
            status: Status of the bot. (Online , Offline  or Unknown)
        """
        if status == "":
            return ""
        if status == "Online":
            status = "Online "
        elif status == "Offline":
            status = "Offline "
        else:
            status = "Unknown"
        return status
