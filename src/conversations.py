from typing import TYPE_CHECKING

# noinspection PyProtectedMember
from disnake.abc import MISSING

from google.generativeai import GenerativeModel, ChatSession
from src.utils import get_initial_prompt

if TYPE_CHECKING:
    from src.bot import Uiharu


class Conversation:
    def __init__(self, bot: "Uiharu", author_id: int, nickname: str = MISSING):
        self.bot: "Uiharu" = bot

        self.author_id: int = author_id
        self.nickname: str = nickname
        self.chat: ChatSession = self.new_chat()

        self.ready: bool = False

    async def ask(self, text: str) -> str:
        await self.chat.send_message_async(text)
        return self.chat.last.text

    def new_chat(self) -> ChatSession:
        # Set up the model
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]

        model = GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        conversation = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": get_initial_prompt(self.nickname),
                },
                {"role": "model", "parts": "知道了！"},
            ]
        )
        return conversation


class ConversationManager:
    def __init__(self, bot: "Uiharu"):
        self.bot = bot

        self.conversations: dict[int, Conversation] = {}

    async def close_conversation(self, user_id: int):
        if user_id not in self.conversations:
            return

        del self.conversations[user_id]

    async def get_conversation(self, user_id: int) -> Conversation:
        if user_id in self.conversations:
            return self.conversations[user_id]

        self.conversations[user_id] = Conversation(
            self.bot, user_id, self.bot.nickname_manager.get_nickname(user_id=user_id)
        )

        return self.conversations[user_id]
