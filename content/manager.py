import copy

from typing import List, Dict, Any

from database.controller import session_factory
from database.models import Content, User
from aiogram.types import Message
from database.caching_query import FromCache
from utils.decorators import timer
from static.messages import dictionary as msg_dict
import logging as log
import numpy as np


class Manager:
    def __init__(
            self, type_content: str = "photo", message: Message = None,
            get_content_random: bool = False
    ) -> None:
        self.session = session_factory()
        self.type_content = type_content
        self.message = message
        self.user_id = message.from_user.id if message else None
        self.get_content_random = get_content_random

    @timer
    def add_content(self, file_id: str) -> bool:
        try:
            self.session.add(Content(
                type_content=self.type_content,
                file_id=file_id,
                moderated=False
            ))
            self.session.commit()
            self.session.close()
            return True
        except Exception as e:
            log.error("Error add content. Details: %s" % e)
            return False

    @property
    @timer
    def _get_user(self) -> User or None:
        try:
            data = self.session.query(User).options(
                FromCache("get_user", expiration_time=300)
            ).filter_by(
                user_id=self.user_id).one()
            self.session.close()
            return data
        except Exception as e:
            log.error("Error get user. Details: %s" % e)

    @property
    @timer
    def _get_all_users(self) -> List[User] or None:
        try:
            data = self.session.query(User).options(
                FromCache("get_all_users", expiration_time=180)).all()
            self.session.close()
            return data
        except Exception as e:
            log.error("Error get user. Details: %s" % e)

    @property
    def get_all_users_ids(self) -> List[int] or None:
        return [user.user_id for user in self._get_all_users]

    @property
    def check_ban(self) -> bool:
        if self.check_user:
            return True if self._get_user.banned else False
        return False

    @property
    def check_full_ban(self) -> bool:
        if self.check_user:
            return True if self._get_user.full_banned else False
        return False

    @property
    def check_user(self) -> bool:
        user = self._get_user
        if not user:
            return True if self._add_user else False
        elif (user.tg_name_user != self.message.from_user.full_name) \
                or (user.tg_username_user != self.message.from_user.username and (
                self.message.from_user.username)):
            _ = self._update_user_name
        return True

    @property
    @timer
    def _update_user_name(self) -> bool:
        try:
            username = self.message.from_user.username
            self.session.query(User).filter_by(
                user_id=self.user_id
            ).update(
                {
                    User.tg_name_user: self.message.from_user.full_name,
                    User.tg_username_user: username if username else "N/A"
                }
            )
            self.session.commit()
            self.session.close()
        except Exception as e:
            log.warning("Error update user. Details: %s" % e)
            return False

    @property
    @timer
    def _add_user(self) -> bool:
        try:
            self.session.add(User(
                user_id=self.user_id,
                tg_name_user=self.message.from_user.full_name,
                tg_username_user=self.message.from_user.username,
                banned=False,
                full_banned=False,
                last_photo=0,
                last_video=0,
                last_voice=0
            ))
            self.session.commit()
            self.session.close()
            return True
        except Exception as e:
            log.error("Error add user. Details: %s" % e)
            return False

    @property
    @timer
    def _get_content_query(self) -> Content:
        data = self.session.query(Content).options(
            FromCache("get_content_query", expiration_time=600)
        ).filter_by(
            moderated=True, type_content=self.type_content)
        self.session.close()
        return data

    @timer
    def _get_all_content(self, moderated: bool = True) -> Content:
        data = self.session.query(Content).options(
            FromCache("get_all_content", expiration_time=600)
        ).filter_by(moderated=moderated)
        self.session.close()
        return data

    @staticmethod
    @timer
    def _sort_content(content: Content) -> List[Content]:
        return sorted(
            [el for el in copy.deepcopy(content.all())],
            key=lambda x: x.id, reverse=False
        )

    @staticmethod
    @timer
    def _build_top_list(content: Content, users: User, len_: int = 10) -> List[dict]:

        def _sort_by_ids() -> Dict[list, Any]:
            loaders = list(dict.fromkeys([u.loader_id for u in content[:]]))
            return {
                loader: [
                    c for c in content[:] if c.loader_id == loader
                ] for loader in loaders}

        def _sort_users_by_len(users_dict: dict) -> list:
            return sorted(
                [v for v in users_dict.items()],
                key=lambda x: len(x[1]), reverse=True
            )

        def _get_user_name(user_id: int) -> str:
            return [
                user.tg_name_user
                for user in users[:]
                if user.user_id == user_id
            ][0]

        _template = msg_dict["top_list_template"]
        _users = _sort_users_by_len(_sort_by_ids())
        return [
            {
                "message": _template % (
                    i + 1, _get_user_name(_users[i][0]), len(_users[i][1])),
                "data": {
                    "index": i,
                    "user": _users[i]
                }
            }
            for i in range(len_)
        ]

    @property
    def get_top(self) -> str:
        return "%s\n(%s)" % ("\n".join([
            line["message"] for line in self._build_top_list(
                self._get_all_content(moderated=True), self._get_all_users)
        ]), msg_dict["top_list_comment"])

    @property
    def _get_content(self) -> tuple or None:

        @timer
        def _random_select(content_data: list, samples: int = 10) -> int:
            _array = np.random.choice(len(content_data[:]), samples, replace=True)
            np.random.shuffle(_array)
            return _array[0]

        content = self._get_content_query
        log.debug("Random get content = %s" % self.get_content_random)
        if not self.get_content_random:
            _content_sorted = self._sort_content(content)
            _selector = self._get_last_id
            try:
                content[_selector]
            except IndexError:
                return
            content_list = _content_sorted
            log.debug("Get content: last_id = %d" % _selector)
        else:
            _selector = _random_select(content, samples=50)
            content_list = content
            log.debug("Get content: rand = %d" % _selector)
        return None if not self._update_last_id_content \
            else \
            (
                (content_list[_selector].id, content_list[_selector].file_id)
                if content.count() else ""
            )

    @property
    @timer
    def _get_last_id(self) -> int:
        x = self.session.query(User).filter_by(
            user_id=self.user_id).all()
        self.session.close()
        return eval(f"int(x[0].last_{self.type_content})")

    @property
    @timer
    def _update_last_id_content(self) -> bool:
        try:
            self.session.query(User).filter_by(
                user_id=self.user_id
            ).update(
                eval("{User.last_%s: User.last_%s + 1}" % (self.type_content, self.type_content))
            )
            self.session.commit()
            self.session.close()
            return True
        except Exception as e:
            log.error("Error update last id content for user. Details: %s" % e)
            return False

    @property
    def get_content(self) -> tuple:
        data = self._get_content
        return data if data.__class__.__name__ == "tuple" else (None, None)

    def __str__(self) -> str:
        data = self._get_content
        return data
