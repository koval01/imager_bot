from database.controller import session_factory
from database.models import Content, User
from aiogram.types import Message
import logging as log


class Manager:
    def __init__(self, type_content: str = "photo", message: Message = None) -> None:
        self.session = session_factory()
        self.type_content = type_content
        self.user_id = message.from_user.id
        self.message = message

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
            log.error("Error database (%s). Details: %s" % (
                self.add_content.__name__, e))
            return False

    @property
    def _get_user(self) -> User or None:
        try:
            return self.session.query(User).filter_by(
                user_id=self.user_id).one()
        except Exception as e:
            log.error("Error get user. Details: %s" % e)

    @property
    def check_ban(self) -> bool:
        if self.check_user:
            return True if self._get_user.banned else False
        return False

    @property
    def check_user(self) -> bool:
        user = self._get_user
        if not user:
            return True if self._add_user else False
        elif (user.tg_name_user != self.message.from_user.full_name) \
                or (user.tg_username_user != self.message.from_user.username):
            self._update_user_name
        return True

    @property
    def _update_user_name(self) -> bool:
        try:
            self.session.query(User).filter_by(
                user_id=self.user_id
            ).update(
                {
                    User.tg_name_user: self.message.from_user.full_name,
                    User.tg_username_user: self.message.from_user.username
                }
            )
            self.session.commit()
        except Exception as e:
            log.warning("Error update user name. Details %s" % e)
            return False

    @property
    def _add_user(self) -> bool:
        try:
            self.session.add(User(
                user_id=self.user_id,
                tg_name_user=self.message.from_user.full_name,
                tg_username_user=self.message.from_user.username,
                banned=False,
                last_photo=0,
                last_video=0,
                last_voice=0
            ))
            self.session.commit()
            self.session.close()
            return True
        except Exception as e:
            log.error("Error database (%s). Details: %s" % (
                self._add_user.__name__, e))
            return False

    @property
    def _get_content(self) -> str:
        x = self.session.query(Content).filter_by(
            moderated=True, type_content=self.type_content)
        l = self._get_last_id
        try: x[l]
        except IndexError: return ""
        return "" if not self._update_last_id_content \
            else (x[l].file_id if x.count() else "")

    @property
    def _get_last_id(self) -> int:
        x = self.session.query(User).filter_by(
            user_id=self.user_id).all()
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
            return True
        except Exception as e:
            log.error("Error in %s. Details: %s" % (self._update_last_id_content.__name__, e))
            return False

    def __str__(self) -> str:
        data = self._get_content
        self.session.close()
        return data
