from aiogram import types
from database.controller import session_factory
from database.models import Moderator
from content.manager import Manager
import logging as log


class CheckModerator:
    def __init__(self, message: types.Message) -> None:
        self.session = session_factory()
        self.message = message

    @property
    def _check_user(self) -> bool:
        user_check = Manager(message=self.message).check_user
        log.debug("Error check user.") if not user_check else None
        x = self.session.query(Moderator).filter_by(
            tg_user_id=self.message.from_user.id)
        return True if x.count() else False

    @property
    def get(self) -> bool:
        return self._check_user
