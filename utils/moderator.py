from typing import List

from aiogram import types
from sqlalchemy.future import select

from database.controller import async_sql_session
from database.models import Moderator
from utils.decorators import async_timer


class CheckModerator:
    def __init__(self, message: types.Message = None) -> None:
        self.session = async_sql_session
        self.message = message

    @property
    @async_timer
    async def _check_user(self) -> bool:
        async with self.session.begin() as session:
            q = select(Moderator).where(
                Moderator.tg_user_id == self.message.from_user.id)
            result = await session.execute(q)
            curr = result.scalars()
            data = curr.all()
            await session.close()
        return True if len(data) else False

    @property
    @async_timer
    async def get_moderators(self) -> List[int] or None:
        async with self.session.begin() as session:
            q = select(Moderator).order_by(Moderator.tg_user_id)
            result = await session.execute(q)
            curr = result.scalars()
            data = curr.all()
            await session.close()
        return [int(el.tg_user_id) for el in data] \
            if len(data) else None

    @property
    async def get(self) -> bool:
        return bool(
            await self._check_user)
