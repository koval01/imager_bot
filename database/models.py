import datetime

from sqlalchemy import Column, Integer, String, TypeDecorator, BigInteger
from sqlalchemy.types import Boolean, DateTime

from database.controller import Base


class ChoiceType(TypeDecorator):
    """A tool for creating a selection method"""

    impl = String
    cache_ok = False

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.items() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]


class DictMixIn:
    """Provides a to_dict method to a SQLAlchemy database model."""

    # def __init__(self):
    #     self.__table__ = None

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            if not isinstance(
                getattr(self, column.name), (datetime.datetime, datetime.date)
            )
            else getattr(self, column.name).isoformat()
            for column in self.__table__.columns
        }


class Content(Base):
    """Content bot model"""

    __tablename__ = "imager_content"

    id = Column(Integer, primary_key=True, index=True)
    type_content = Column(
        ChoiceType({"photo": "photo", "video": "video", "voice": "voice"}), nullable=False
    )
    loader_id = Column(BigInteger, nullable=False)
    file_id = Column(String(255), nullable=False, index=True, unique=True)
    moderated = Column(Boolean, default=False)
    dislikes = Column(Integer, nullable=False, default=0)

    def __init__(self, type_content, loader_id, file_id, moderated):
        self.type_content = type_content
        self.loader_id = loader_id
        self.file_id = file_id
        self.moderated = moderated


class User(Base):
    """User bot model"""

    __tablename__ = "imager_user"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True, unique=True)
    tg_name_user = Column(String(255), default="Unknown", nullable=False)
    tg_username_user = Column(String(255), default="@Unknown", nullable=False)
    banned = Column(Boolean, default=False)
    full_banned = Column(Boolean, default=False)
    last_photo = Column(BigInteger, default=0, nullable=False)
    last_video = Column(BigInteger, default=0, nullable=False)
    last_voice = Column(BigInteger, default=0, nullable=False)

    def __init__(
            self, user_id, tg_name_user, tg_username_user,
            banned, full_banned, last_photo, last_video, last_voice):
        self.user_id = user_id
        self.tg_name_user = tg_name_user
        self.tg_username_user = tg_username_user
        self.banned = banned
        self.full_banned = full_banned
        self.last_photo = last_photo
        self.last_video = last_video
        self.last_voice = last_voice


class Moderator(Base):
    """Moderators list"""

    __tablename__ = "imager_telegram"

    id = Column(Integer, primary_key=True, index=True)
    tg_user_id = Column(BigInteger, nullable=False, index=True, unique=True)
    user_id = Column(Integer, nullable=False, index=True, unique=True)

    def __init__(self, tg_user_id, user_id):
        self.tg_user_id = tg_user_id
        self.user_id = user_id
