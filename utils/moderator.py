from aiogram import types
from database.controller import session_factory
from database.models import Moderator
from typing import List


class CheckModerator:
    def __init__(self, message: types.Message = None) -> None:
        self.session = session_factory()
        self.message = message

    @property
    def _check_user(self) -> bool:
        x = self.session.query(Moderator).filter_by(
            tg_user_id=self.message.from_user.id)
        return True if x.count() else False

    @property
    def get_moderators(self) -> List[int] or None:
        x = self.session.query(Moderator).all()
        return [int(el.tg_user_id) for el in x] if len(x) else None

    @property
    def get(self) -> bool:
        return bool(self._check_user)
