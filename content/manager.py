import logging as log
from typing import List, Dict, Any

import numpy as np
from aiogram.types import Message
from sqlalchemy import update
from sqlalchemy.future import select

from database.controller import async_sql_session
from database.models import Content, User
from static.messages import dictionary as msg_dict
from utils.decorators import async_timer


class Manager:
    def __init__(
            self, type_content: str = "photo", message: Message = None,
            get_content_random: bool = False
    ) -> None:
        self.type_content = type_content
        self.message = message
        self.user_id = message.from_user.id if message else None
        self.get_content_random = get_content_random
        self.session = async_sql_session

    @async_timer
    async def _get_user(self) -> User or None:
        """
        Get user by user id
        """
        try:
            async with self.session.begin() as session:
                q = select(User).where(User.user_id == self.user_id)
                result = await session.execute(q)
                curr = result.scalars()
                data = curr.one()
                await session.close()
            return data
        except Exception as e:
            log.warning(
                "Error search user in database. Details: %s" % e)

    @property
    @async_timer
    async def _get_all_users(self) -> List[User] or None:
        """
        Get full list users
        """
        async with self.session.begin() as session:
            q = select(User).order_by(User.id)
            result = await session.execute(q)
            curr = result.scalars()
            data = curr.all()
            await session.close()
        return data

    @property
    @async_timer
    async def get_all_users_ids(self) -> List[int] or None:
        """
        Convert all users query to python list
        """
        return [user.user_id for user in await self._get_all_users]

    @property
    async def check_ban(self) -> bool:
        """
        Check ban content load
        """
        if await self.check_user():
            user = await self._get_user()
            return True if user.banned else False
        return False

    @property
    async def check_full_ban(self) -> bool:
        """
        Check full close access to bot
        """
        if await self.check_user():
            user = await self._get_user()
            return True if user.full_banned else False
        return False

    @async_timer
    async def check_user(self) -> bool:
        """
        Check user status
        """
        user = await self._get_user()
        if not user:
            return True if \
                await self._add_user() else False
        elif (user.tg_name_user != self.message.from_user.full_name) \
                or (
                user.tg_username_user != self.message.from_user.username
                and (
                        self.message.from_user.username)):
            _ = await self._update_user_name
        return True

    @property
    @async_timer
    async def _update_user_name(self) -> bool:
        """
        Update name user and username in database
        """
        try:
            async with self.session.begin() as session:
                username = self.message.from_user.username
                q = update(User). \
                    where(User.id == self.user_id). \
                    values(
                    tg_name_user=self.message.from_user.full_name,
                    tg_username_user=username if username else "N/A"
                )
                log.debug("Update name for user. Request: %s" % q)
                await session.commit()
                await session.close()
            return True
        except Exception as e:
            log.warning("Error update user. Details: %s" % e)
            return False

    @async_timer
    async def _add_user(self) -> bool:
        """
        Add user to database
        """
        try:
            async with self.session.begin() as session:
                session.add(User(
                    user_id=self.user_id,
                    tg_name_user=self.message.from_user.full_name,
                    tg_username_user=self.message.from_user.username,
                    banned=False,
                    full_banned=False,
                    last_photo=0,
                    last_video=0,
                    last_voice=0
                ))
                await session.commit()
                await session.close()
            return True
        except Exception as e:
            log.warning("Error add user. Details: %s" % e)
            return False

    @property
    @async_timer
    async def _get_content_query(self) -> Content:
        """
        Get moderated content by category
        """
        async with self.session.begin() as session:
            moderated_ = True
            q = select(Content). \
                where(
                Content.moderated == moderated_,
                Content.type_content == self.type_content). \
                order_by(Content.id)
            result = await session.execute(q)
            curr = result.scalars()
            data = curr.all()
            await session.close()
        return data

    @async_timer
    async def _get_all_content(self, moderated: bool = True) -> Content:
        """
        Get all content
        """
        async with self.session.begin() as session:
            q = select(Content). \
                order_by(Content.id). \
                where(Content.moderated == moderated)
            result = await session.execute(q)
            curr = result.scalars()
            data = curr.all()
            await session.close()
        return data

    @staticmethod
    def _build_top_list(content: Content, users: User, len_: int = 10) -> List[dict]:
        """
        Builder top list
        """

        def _sort_by_ids_top_list() -> Dict[list, Any]:
            content_ = content[:]
            result = {}
            for c in content_:
                if c.loader_id in result:
                    result[c.loader_id] += 1
                else:
                    result.update({c.loader_id: 1})
            return result

        def _sort_users_by_len_top(users_dict: dict) -> list:
            return sorted(
                [v for v in users_dict.items()],
                key=lambda x: x[1], reverse=True
            )

        def _get_user_name_top(user_id: int, users_: list) -> str:
            return [
                user.tg_name_user
                for user in users_[:]
                if user.user_id == user_id
            ][0]

        _template = msg_dict["top_list_template"]
        _users = \
            _sort_users_by_len_top(
                _sort_by_ids_top_list())
        _users_array = users[:]

        return [
            {
                "message": _template % (
                    i + 1, _get_user_name_top(
                        _users[i][0], _users_array),
                    _users[i][1]),
                "data": {
                    "index": i,
                    "user": _users[i]
                }
            }
            for i in range(len_)
        ]

    @property
    async def get_top(self) -> str:
        return "%s\n(%s)" % ("\n".join([
            line["message"] for line in
            self._build_top_list(
                await self._get_all_content(moderated=True),
                await self._get_all_users)
        ]), msg_dict["top_list_comment"])

    @property
    async def _get_content(self) -> tuple or None:
        """
        Order formatted content data
        """

        async def _random_select(content_data: list, samples: int = 10) -> int:
            _array = np.random.choice(
                len(content_data[:]), samples, replace=True)
            np.random.shuffle(_array)
            return _array[0]

        content = await self._get_content_query
        log.debug(
            "Random get content = %s" % self.get_content_random)
        if not self.get_content_random:
            _selector = await self._get_last_id
            log.debug("Selector for %d is %d" % (
                self.user_id, _selector))
            try:
                content[_selector]
            except IndexError:
                return
            content_list = content[:]
            log.debug("Get content: last_id = %d" % _selector)
        else:
            _selector = await _random_select(content, samples=50)
            content_list = content[:]
            log.debug("Get content: rand = %d" % _selector)
        return None if not await self._update_last_id_content \
            else \
            (
                (
                    content_list[_selector].id,
                    content_list[_selector].file_id)
                if len(content) else ""
            )

    @property
    @async_timer
    async def _get_last_id(self) -> int:
        """
        Get id last viewed content by category
        """
        x = await self._get_user()
        return eval(
            f"int(x.last_{self.type_content})",
            {"x": x})

    @property
    @async_timer
    async def _update_last_id_content(self) -> bool:
        """
        Update counter last ordered content by category
        """
        try:
            async with self.session.begin() as session:
                q = update(User).values(
                    eval("{User.last_%s: User.last_%s + 1}"
                         % tuple([self.type_content] * 2))).where(
                    User.user_id == self.user_id)
                await session.execute(q)
                await session.commit()
                await session.close()
                log.debug("Update last id. Request: %s" % q)
            return True
        except Exception as e:
            log.error(
                "Error update last id content for user. Details: %s" % e)
            return False

    @async_timer
    async def add_dislike(self, content_id: int) -> bool:
        """
        Add user to disliked users list for content
        """
        try:
            async with self.session.begin() as session:
                q = update(Content). \
                    where(Content.id == content_id). \
                    values({Content.dislikes: Content.dislikes + 1})
                await session.execute(q)
                await session.commit()
                await session.close()
                log.debug(
                    "Add dislike for content. Request: %s" % q)
            return True
        except Exception as e:
            log.error(
                "Error add dislike for content id: %d. Details: %s" %
                (content_id, e))
            return False

    async def get_content(self) -> tuple:
        data = await self._get_content
        return data if data.__class__.__name__ == "tuple" else (None, None)
