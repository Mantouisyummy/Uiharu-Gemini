import asyncio
import re
from typing import Union

from disnake.abc import Messageable


async def keep_typing(channel: Messageable):
    while True:
        await channel.trigger_typing()
        await asyncio.sleep(9)


def remove_mentions(message):
    mention_pattern = r"<@!?\d+>"

    cleaned_message = re.sub(mention_pattern, "", message)

    return cleaned_message


def load_initial_prompt() -> str:
    with open("./prompt.txt", "r", encoding="utf-8") as f:
        return f.read()


def get_initial_prompt(nickname: Union[str, None]) -> Union[str, None]:
    if not nickname:
        nickname = "主人"

    return StaticVariables.INITIAL_PROMPT.replace("%nickname%", nickname)


class StaticVariables:
    INITIAL_PROMPT = load_initial_prompt()