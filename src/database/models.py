from sqlalchemy import Column, Integer, String, Boolean, sql

from . import db

class UiharuDB(db.Base):
    __tablename__ = "uiharu"

    user_id = Column(Integer, primary_key=True)
    nickname = Column(String)
    locked = Column(Boolean, default=False, server_default=sql.false())