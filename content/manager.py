import copy

from typing import List

from database.controller import session_factory
from database.models import Content, User
from aiogram.types import Message
import logging as log


class Manager:
    def __init__(self, type_content: str = "photo", message: Message = None) -> None:
        self.session = session_factory()
        self.type_content = type_content
        self.message = message
        self.user_id = message.from_user.id if message else None

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
    def _get_user(self) -> User or None:
        try:
            data = self.session.query(User).filter_by(
                user_id=self.user_id).one()
            self.session.close()
            return data
        except Exception as e:
            log.error("Error get user. Details: %s" % e)

    @property
    def _get_all_users(self) -> List[User] or None:
        try:
            data = self.session.query(User).all()
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
    def _get_content_query(self) -> Content:
        data = self.session.query(Content).filter_by(
            moderated=True, type_content=self.type_content)
        self.session.close()
        return data

    @staticmethod
    def _sort_content(content: Content) -> List[Content]:
        return sorted(
            [el for el in copy.deepcopy(content.all())],
            key=lambda x: x.id, reverse=False
        )

    @property
    def _get_content(self) -> tuple or None:
        content = self._get_content_query
        last_id = self._get_last_id
        try:
            content[last_id]
        except IndexError:
            return
        content_sorted = self._sort_content(content)
        return None if not self._update_last_id_content \
            else \
            (
                (content_sorted[last_id].id, content_sorted[last_id].file_id)
                if content.count() else ""
            )

    @property
    def _get_last_id(self) -> int:
        x = self.session.query(User).filter_by(
            user_id=self.user_id).all()
        self.session.close()
        return eval(f"int(x[0].last_{self.type_content})")

    @property
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
