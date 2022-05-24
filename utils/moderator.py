from aiogram import types
from database.controller import session_factory
from database.models import Content
from static import config
from static.messages import dictionary as dict_reply
import logging as log


class LoaderContent:
    def __init__(self, message: types.Message) -> None:
        self.session = session_factory()
        self.message = message


