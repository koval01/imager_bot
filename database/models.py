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

    __tablename__ = "Content"

    id = Column(Integer, primary_key=True, index=True)
    type_content = Column(
        ChoiceType({"photo": "photo", "video": "video", "voice": "voice"}), nullable=False
    )
    file_id = Column(String(255), nullable=False, index=True, unique=True)
    moderated = Column(Boolean)

    def __init__(self, type_content, file_id, moderated):
        self.type_content = type_content
        self.file_id = file_id
        self.moderated = moderated


class User(Base):
    """User bot model"""

    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True, unique=True)
    banned = Column(Boolean)
    last_photo = Column(BigInteger)
    last_video = Column(BigInteger)
    last_voice = Column(BigInteger)

    def __init__(self, user_id, banned, last_photo, last_video, last_voice):
        self.user_id = user_id
        self.banned = banned
        self.last_photo = last_photo
        self.last_video = last_video
        self.last_voice = last_voice
