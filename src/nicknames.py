from typing import TYPE_CHECKING, Union

from .database.models import UiharuDB
from sqlalchemy.orm import Query

if TYPE_CHECKING:
    from src.bot import Uiharu


class NicknameLocked(Exception):
    pass


class NicknameManager:
    # {
    #     "user_id": int,
    #     "nickname": string,
    #     "locked": boolean
    # }

    def __init__(self, bot: "Uiharu"):
        self.bot = bot
        self.query: Query[UiharuDB] = bot.database.query(UiharuDB)

    def list_nicknames(self, **kwargs) -> dict[int, str]:
        """
        List nicknames from the database.
        :param kwargs: kwargs to pass to the filter_by method
        :return: dict of nicknames, key is user_id, value is nickname
        """
        result = self.query.filter_by(**kwargs).all()

        return {entry.user_id: entry.nickname for entry in result}

    def get_nickname(self, **kwargs) -> Union[str, None]:
        """
        Get a nickname from the database.
        :param kwargs: kwargs to pass to the find_one method, possible values are user_id, nickname, locked
        :return: nickname if found, None if not
        """
        result = self.query.filter_by(**kwargs).first()

        if result is None:
            return None

        return result.nickname

    def set_nickname(self, user_id: int, force: bool = False, **kwargs):
        """
        Set a nickname in the database.
        :param user_id:
        :param force: Force the nickname to be set, even if it's locked
        :param kwargs: kwargs to pass to the update_one method, possible values are nickname, locked
        """

        result = self.query.filter_by(user_id=user_id).first()
       
        if result:
            if result.locked and not force:
                raise NicknameLocked(f"{user_id} already has a locked nickname")
            self.query.filter_by(user_id=user_id).update({**kwargs} ,synchronize_session='evaluate')
            self.bot.database.commit()
        else:
            data = UiharuDB(user_id=user_id, **kwargs)
            self.bot.database.add(data)
            self.bot.database.commit()

    def lock_nickname(self, user_id: int) -> bool:
        """
        Toggle the locked status of a nickname.
        :param user_id: user_id to lock
        :return: True if locked, False if unlocked
        """

        result = self.query.filter_by(user_id=user_id).first()

        self.query.filter_by(user_id=user_id).update({"locked": False if result.locked else True}, synchronize_session='evaluate')
        self.bot.database.commit()

        return result.locked

    def remove_nickname(self, user_id: int) -> Union[str, None]:
        """
        Remove a nickname from the database.
        :param user_id: user_id to remove
        :return: Original nickname, None if not found
        """
        result = self.query.filter_by(user_id=user_id).delete(synchronize_session='evaluate')

        if result:
            return result["nickname"]

        return None