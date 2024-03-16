import logging
import asyncio

from os import getenv

from dotenv import load_dotenv

from src.bot import Uiharu

from disnake import Intents

from colorlog import ColoredFormatter


def main():
    load_dotenv()

    setup_logging()

    main_logger = logging.getLogger("uiharu.main")

    uiharu = Uiharu(logger=main_logger, command_prefix="u!", intents=Intents.all(), owner_ids=[int(owner_id) for owner_id in getenv("OWNER_IDS").split(",")])

    uiharu.load_extensions("./src/cogs")

    uiharu.run(getenv("TOKEN"))

def setup_logging():
    """
    Set up the loggings for the bot
    :return: None
    """
    formatter = ColoredFormatter(
        '%(asctime)s %(log_color)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(filename="lava.log", encoding="utf-8", mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        handlers=[stream_handler, file_handler], level=logging.INFO
    )

if __name__ == "__main__":
    main()