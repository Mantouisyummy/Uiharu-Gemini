import logging

from os import getenv
from logging import Logger

from disnake.ext.commands import Bot as OriginalBot
from src.database.db import create_session, create_table

import google.generativeai as Genai

from src.conversations import ConversationManager
from src.nicknames import NicknameManager


class Uiharu(OriginalBot):
    def __init__(self, logger: Logger, *args, **kwargs):
        """
        :param args: args to pass to the bot
        :param kwargs: kwargs to pass to the bot
        """
        super().__init__(*args, **kwargs)

        self.logger = logger

        Genai.configure(
            api_key=getenv("API_KEY"),
        )

        create_table()

        self.database = create_session()

        self.nickname_manager = NicknameManager(self)

        self.conversation_manager = ConversationManager(self)

    async def on_ready(self):
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")