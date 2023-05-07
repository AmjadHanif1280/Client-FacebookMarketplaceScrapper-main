"""
A Customized Bot Made for My Program, API wrapper for Telegram API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic usage:

   >>> from telegram_bot.custom_bot import CustomBot
   >>> CustomBot = CustomBot(token, dev_id, announcement_channel)
   >>> CustomBot.main()

Define your own class:
    Token: Token of the telegram bot. (Get it from @BotFather)
    Channel: Channel id of the telegram channel. (Get it from @getidsbot)
    Parse Mode: Parse mode of the message. (Markdown, HTML or None)
    Status: Status of the bot. (Online, Offline or None)

Author: @livxy/bruhs/aidan
Github: https://github.com/livxy/

:license: Apache 2.0, see LICENSE for more details.
"""

import html
import json
import logging
import traceback
import re

# Make sure to install the latest version of python-telegram-bot
from telegram import Update
from telegram import __version__ as TG_VER
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class CustomBot:
    """
    A Customized Bot Made for My Program, API wrapper for Telegram API

    Basic usage:

        >>> from telegram_bot.custom_bot import CustomBot
        >>> CustomBot = CustomBot(token, dev_id, announcement_channel)
        >>> CustomBot.main()

    Define your own class:
        Token: Token of the telegram bot. (Get it from @BotFather)
        Channel: Channel id of the telegram channel. (Get it from @getidsbot)
        Parse Mode: Parse mode of the message. (Markdown, HTML or None)
        Status: Status of the bot. (Online, Offline or None)

    """

    def __init__(self, token: str, dev_id: int, announcement_channel: int):
        self.token = token
        self.dev_id = dev_id
        self.announcement_channel = announcement_channel
        self.logging_enabled = False
        self.log_messages = []

    @staticmethod
    async def greet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Hello! Welcome to the Facebook Scrapper Bot. Please write /help to see the commands available.",
        )

    @staticmethod
    async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        with open("config.json", "r") as f:
            config = json.load(f)
            _allow_duplicates = config["queries"]["allow_duplicates"]
        help_msg = f"""
    <b>Available Commands:</b>
    
    <b>General:</b>
    - /help -- Show this message
    
    <b>Scraping:</b>
    - /list_query -- List all the queries in the database
          Example: <code>/list_query</code>
    - /add_query -- Add a query to the database
          Examples: <code>/add_query dog</code>
                    <code>/add_query cat, dog, fish</code>
    - /remove_query -- Remove a query from the database
          Examples: <code>/remove_query dog</code>
                    <code>/remove_query cat, dog, fish</code>
    
    <b>Title Excluders:</b>
    - /list_title_excluder -- List all the title excluders in the database
          Example: <code>/list_title_excluder</code>
    - /add_title_excluder -- Add a title excluder to the database
          Examples: <code>/add_title_excluder dog</code>
                    <code>/add_title_excluder cat, dog, fish</code>
    - /remove_title_excluder -- Remove a title excluder from the database
          Examples: <code>/remove_title_excluder dog</code>
                    <code>/remove_title_excluder cat, dog, fish</code>
    
    <b>Settings:</b>
    - /allow_duplicates -- Allow/Disallow duplicate <code>list_query</code>. (Default: False)
        Currently: <code>{_allow_duplicates}</code>
    
    \u2015 <i>end of available commands</i> \u2015
    """

        await context.bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=ParseMode.HTML,
            text=help_msg,
        )

    async def error_handler(
        self, update: object, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        tb_string = "".join(tb_list)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="An error occured! Reporting to developer!",
            parse_mode=ParseMode.HTML,
        )

        # Finally, send the message
        await context.bot.send_message(
            chat_id=self.dev_id, text=message, parse_mode=ParseMode.HTML
        )

    #     @staticmethod
    #     async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #         """Send a message when the command /end is issued."""
    #         await update.message.reply_text("Ending the bot...")
    #
    #     async def message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #         """Send a message when the command /message is issued."""
    #         # replace the /message in update.message.text
    #         update.message.text = update.message.text.replace("/message ", "")
    #         await context.bot.send_message(
    #             chat_id=self.dev_id,
    #             text=f"""
    # Message from {update.message.from_user.name}:
    #
    # \"{update.message.text}\"
    #
    # (Chat ID: {update.message.chat_id})
    # (Message ID: {update.message.message_id})
    # """,
    #         )
    #
    #         # Link to a telegram message given the chat_id and message_id:
    #         # https://t.me/c/CHAT_ID/MESSAGE_ID
    #         await update.message.reply_text("Sent!")

    @staticmethod
    async def list_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends the current query to the user."""
        # open it  open config.json it's path is not in the same directory as the bot.py file
        with open("config.json", "r") as f:
            cfg = json.load(f)
        with open("config.json", "w") as f:
            json.dump(cfg, f, indent=4)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=ParseMode.HTML,
            text=f"""
Current list of queries: <pre>{[item.lstrip() for item in cfg["queries"]["title_include"]]}</pre>
""",
        )

    @staticmethod
    async def remove_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Removes a query from the database."""
        # get the query from update message text
        query = update.message.text.replace("/remove_query", "").replace('"', "")
        # split the query by commas
        queries_to_remove = [q.strip() for q in query.split(",")]
        # open the config.json file
        with open("config.json", "r") as f:
            cfg = json.load(f)
        removed_queries = []
        for q in queries_to_remove:
            if matching_query := next(
                (
                    x
                    for x in cfg["queries"]["title_include"]
                    if re.sub(r"[^a-zA-Z0-9\s]", "", x).strip()
                    == re.sub(r"[^a-zA-Z0-9\s]", "", q).strip()
                ),
                None,
            ):
                # remove the matching query from the config.json file
                cfg["queries"]["title_include"].remove(matching_query)
                removed_queries.append(q)
            else:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                    text=f"""
        The query does not exist in the database.
    
        Attempted to remove: <pre>{q}</pre>
    
        Current list of queries: <pre>{[item.lstrip() for item in cfg["queries"]["title_include"]]}</pre>
        """,
                )

        if removed_queries:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                text=f"""
        The following queries have been removed from the database:
        <pre>{", ".join(removed_queries)}</pre>
    
        New list of queries: <pre>{[item.lstrip() for item in cfg["queries"]["title_include"]]}</pre>
        """,
            )
            # save the config.json file
            with open("config.json", "w") as f:
                # format the config.json file
                json.dump(cfg, f, indent=4)

    @staticmethod
    async def add_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends the current query to the user."""
        # replace the /query in update.message.text
        query = update.message.text.replace("/add_query", "")
        if not query.strip():
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="The query is empty. Please try again.",
            )
            return

        # split the query string by comma and trim whitespace from each item
        query_list = [q.strip() for q in query.split(",")]

        # open config.json, it's path is not in the same directory as the bot.py file
        with open("config.json", "r") as f:
            cfg = json.load(f)

        # add each query to the list of title_include
        added_queries = []
        for q in query_list:
            if not q:
                continue
            # remove all non-alphanumeric characters
            cleaned_text = re.sub(r"[^a-zA-Z0-9 ]", "", q)
            # check if the query is already in the config.json file
            if (
                cfg["queries"]["allow_duplicates"]
                in ["False", "false", "FALSE", "F", "f"]
                and cleaned_text in cfg["queries"]["title_include"]
            ):
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                    text=f"""
    The query already exists in the database.
    
    Attempted to add: <pre>{cleaned_text}</pre>
    
    Current list of queries: <pre>{[item.lstrip() for item in cfg["queries"]["title_include"]]}</pre>
    """,
                )
                continue

            cfg["queries"]["title_include"].append(cleaned_text)
            added_queries.append(cleaned_text)

        with open("config.json", "w") as f:
            # format the json file
            json.dump(cfg, f, indent=4)

        if added_queries:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                text=f"""
    The following queries have been added to the database:
    <pre>{", ".join(added_queries)}</pre>
    
    Current list of queries: <pre>{[item.lstrip() for item in cfg["queries"]["title_include"]]}</pre>
    """,
            )
        else:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                text=f"""
    All queries already exist in the database.
    
    Current list of queries: <pre>{[item.lstrip() for item in cfg["queries"]["title_include"]]}</pre>
    """,
            )

    @staticmethod
    async def list_title_excluder(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Sends the current title excludes to the user."""
        # open it  open config.json it's path is not in the same directory as the bot.py file
        with open("config.json", "r") as f:
            cfg = json.load(f)
        with open("config.json", "w") as f:
            json.dump(cfg, f, indent=4)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=ParseMode.HTML,
            text=f"""
Current list of title excluders: <pre>{[item.lstrip() for item in cfg["queries"]["title_exclude"]]}</pre>
""",
        )

    @staticmethod
    async def remove_title_excluder(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Removes a title excluder from the database."""
        # replace the /query in update.message.text
        query = update.message.text.replace("/remove_title_excluder", "").replace(
            '"', ""
        )
        # open config.json; its path is not in the same directory as the bot.py file
        with open("config.json", "r") as f:
            config = json.load(f)
        # split the query by commas and remove each title excluder from the config.json file
        for excluder in query.split(","):
            excluder = excluder.strip()
            if excluder in config["queries"]["title_exclude"]:
                config["queries"]["title_exclude"].remove(excluder)
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                    text=f"""
    The title excluder <pre>'{excluder}'</pre> has been removed from the database.
    
    New list of title excluders: <pre>{[item.lstrip() for item in config["queries"]["title_exclude"]]}</pre>
    """,
                )
            else:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                    text=f"""
    The title excluder <pre>'{excluder}'</pre> does not exist in the database.
    
    Current list of title excluders: <pre>{[item.lstrip() for item in config["queries"]["title_exclude"]]}</pre>
    """,
                )
        # save the config.json file
        with open("config.json", "w") as f:
            # format the config.json file
            json.dump(config, f, indent=4)

    @staticmethod
    async def add_title_excluder(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Adds a title excluder to the database."""
        query = update.message.text.replace("/add_title_excluder", "")
        if query == "" or query.isspace():
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text="""
    Please enter a title excluder to add to the database.
    """,
            )
            return

        # Split the query by commas
        queries = [q.strip() for q in query.split(",")]
        cleaned_queries = [re.sub(r"[^a-zA-Z0-9 ]", "", q) for q in queries]

        # open config.json
        with open("config.json", "r") as f:
            config = json.load(f)

        # check if allow_duplicates is set to false
        if config["queries"]["allow_duplicates"] in [
            "False",
            "false",
            "FALSE",
            "F",
            "f",
        ]:
            if existing_queries := [
                q for q in cleaned_queries if q in config["queries"]["title_exclude"]
            ]:
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                    text=f"""
    The following title excluders already exist in the database: <pre>{", ".join(existing_queries)}</pre>
    
    Attempted to add: <pre>{", ".join(cleaned_queries)}</pre>
    
    Current list of title excluders: <pre>{[q.lstrip() for q in config["queries"]["title_exclude"]]}</pre>
    """,
                )
                return

        # add the cleaned queries to the title_exclude list
        config["queries"]["title_exclude"].extend(cleaned_queries)
        with open("config.json", "w") as f:
            # format the json file
            json.dump(config, f, indent=4)

        await context.bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=ParseMode.HTML,
            text=f"""
    The following title excluders have been added to the database: <pre>{", ".join(cleaned_queries)}</pre>
    
    Current list of title excluders: <pre>{[q.lstrip() for q in config["queries"]["title_exclude"]]}</pre>
    """,
        )

    @staticmethod
    async def show_database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends the current database to the user."""
        # open it  open config.json it's path is not in the same directory as the bot.py file
        with open("config.json", "r") as f:
            config = json.load(f)
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=ParseMode.HTML,
            text=f"""
Current database:

<b>Allow duplicates:</b> <pre>{config["queries"]["allow_duplicates"]}</pre>
<b>Title exclude:</b> <pre>{[item.lstrip() for item in config["queries"]["title_exclude"]]}</pre>
<b>Queries/Title include:</b> <pre>{[item.lstrip() for item in config["queries"]["title_include"]]}</pre>
    """,
        )
        # send it as a file
        await context.bot.send_document(
            chat_id=update.message.chat_id,
            document=open("config.json", "rb"),
            filename="config.json",
        )

    @staticmethod
    async def allow_duplicates(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Allows duplicates in the database"""
        with open("config.json", "r") as f:
            config = json.load(f)
        # if it is already allowed, disable it
        if config["queries"]["allow_duplicates"] in ["True", "true", "TRUE", "T", "t"]:
            config["queries"]["allow_duplicates"] = "False"
            with open("config.json", "w") as f:
                # format the config.json file
                json.dump(config, f, indent=4)
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                text=f"""
    Duplicates are now <b>disabled</b> in the database.
    
Current database:
<b>Allow duplicates:</b> <pre>{config["queries"]["allow_duplicates"]}</pre>
<b>Title exclude:</b> <pre>{[item.lstrip() for item in config["queries"]["title_exclude"]]}</pre>
<b>Queries/Title include:</b> <pre>{[item.lstrip() for item in config["queries"]["title_include"]]}</pre>
        """,
            )
        elif config["queries"]["allow_duplicates"] in [
            "False",
            "false",
            "FALSE",
            "F",
            "f",
        ]:
            config["queries"]["allow_duplicates"] = "True"
            with open("config.json", "w") as f:
                # format the config.json file
                json.dump(config, f, indent=4)
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                text=f"""
    Duplicates are now <b>allowed</b> in the database.
    
Current database:
<b>Allow duplicates:</b> <pre>{config["queries"]["allow_duplicates"]}</pre>
<b>Title exclude:</b> <pre>{[item.lstrip() for item in config["queries"]["title_exclude"]]}</pre>
<b>Queries/Title include:</b> <pre>{[item.lstrip() for item in config["queries"]["title_include"]]}</pre>
        """,
            )

        return

    #     @staticmethod
    #     async def clear_database(
    #         update: Update, context: ContextTypes.DEFAULT_TYPE
    #     ) -> None:
    #         """Clears the database."""
    #         # open it  open config.json it's path is not in the same directory as the bot.py file
    #         with open("config.json", "r") as f:
    #             config = json.load(f)
    #         # Modify the "queries" object
    #         config["queries"]["title_include"] = []
    #         config["queries"]["title_exclude"] = []
    #
    #         with open("config.json", "w") as f:
    #             # format the config.json file
    #             json.dump(config, f, indent=4)
    #         await context.bot.send_message(
    #             chat_id=update.message.chat_id,
    #             text=f"""
    # The database has been cleared.
    #
    # Current database: {config["queries"]}
    # """,
    #         )
    #
    #     @staticmethod
    #     async def clear_queries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #         """Clears the queries."""
    #         # open it  open config.json it's path is not in the same directory as the bot.py file
    #         with open("config.json", "r") as f:
    #             config = json.load(f)
    #         # clear the config.json file
    #         config["queries"]["title_include"] = []
    #         with open("config.json", "w") as f:
    #             # format the config.json file
    #             json.dump(config, f, indent=4)
    #         await context.bot.send_message(
    #             chat_id=update.message.chat_id,
    #             text=f"""
    # The queries have been cleared.
    #
    # Current queries: {config["queries"]["title_include"]}
    # """,
    #         )
    #
    #     @staticmethod
    #     async def clear_excluders(
    #         update: Update, context: ContextTypes.DEFAULT_TYPE
    #     ) -> None:
    #         """Clears the excluders."""
    #         # open it  open config.json it's path is not in the same directory as the bot.py file
    #         with open("config.json", "r") as f:
    #             config = json.load(f)
    #         # clear the config.json file
    #         config["queries"]["title_exclude"] = []
    #         with open("config.json", "w") as f:
    #             # format the config.json file
    #             json.dump(config, f, indent=4)
    #         await context.bot.send_message(
    #             chat_id=update.message.chat_id,
    #             text=f"""
    # The excluders have been cleared.
    #
    # Current excluders: {config["queries"]["title_exclude"]}
    # """,
    #         )

    def main(self) -> None:
        """Start the bot."""
        # Create the Updater and pass it your bot
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("greet", self.greet))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(CommandHandler("add_query", self.add_query))
        application.add_handler(CommandHandler("remove_query", self.remove_query))
        application.add_handler(CommandHandler("list_query", self.list_query))
        application.add_handler(
            CommandHandler("add_title_excluder", self.add_title_excluder)
        )
        application.add_handler(
            CommandHandler("remove_title_excluder", self.remove_title_excluder)
        )
        application.add_handler(
            CommandHandler("list_title_excluder", self.list_title_excluder)
        )
        application.add_handler(
            CommandHandler("allow_duplicates", self.allow_duplicates)
        )
        # TODO: Make "show_database" only show the queries and excluders
        # application.add_handler(CommandHandler("show_database", self.show_database))
        # application.add_handler(CommandHandler("clear_database", self.clear_database))
        # application.add_handler(CommandHandler("clear_queries", self.clear_queries))
        # application.add_handler(CommandHandler("clear_excluders", self.clear_excluders))
        application.add_error_handler(self.error_handler)

        try:
            # Start the Bot
            application.run_polling()
        except (KeyboardInterrupt, Exception) as e:
            print(e)
