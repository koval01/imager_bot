import datetime

from sqlalchemy import Column, Integer, String, TypeDecorator
from sqlalchemy.types import Boolean, DateTime

from database.controller import Base


class ChoiceType(TypeDecorator):
    """A tool for creating a selection method"""

    impl = String

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
    file_id = Column(String(255), nullable=False, index=True)
    add_time = Column(DateTime)
    moderated = Column(Boolean)
