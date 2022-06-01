import logging as log

from aiogram import types
from database.controller import session_factory
from database.models import Content
from static import config
from utils.moderator import CheckModerator
from static.messages import dictionary as dict_reply


class LoaderContent:
    def __init__(self, message: types.Message) -> None:
        self.session = session_factory()
        self.message = message

    @property
    def _content_type(self) -> str:
        try:
            _type = self.message.content_type
            return "video" if _type == "video_note" else \
            [
                t for t in ["photo", "video", "voice"]
                if t == _type
            ][0]
        except Exception as e:
            log.warning("Error resolve content type (%s). Details: %s" % (self._content_type.__name__, e))
            return ""

    @property
    def _check_content_on_moderation(self) -> int:
        content = self.session.query(Content).filter_by(
            moderated=False, loader_id=self.message.from_user.id)
        self.session.close()
        return content.count()

    @property
    def _allow_load(self) -> bool:
        return True if (self._content_type and (
                self._check_content_on_moderation <= 100)
        ) else False

    @property
    def _this_is_moderator(self) -> bool:
        user_id = self.message.from_user.id
        return True if CheckModerator(self.message).get \
                       or user_id == config.BOT_OWNER else False

    def _video_note_check(self, current_type: str) -> str:
        try:
            if self.message.video_note:
                return "video_note"
        except Exception as e:
            log.error("Error check content type (%s). Details: %s" % (self._video_note_check.__name__, e))
        return current_type

    @property
    def _get_file_id(self) -> str:
        _type = self._content_type
        if _type == "photo":
            return self.message.photo[-1:][0].file_id
        return eval(f"self.message.{self._video_note_check(_type)}.file_id")

    @property
    def _check_file_size(self) -> bool:
        _type = self._content_type
        if _type == "photo":
            return True
        else:
            _size = eval(f"self.message.{self._video_note_check(_type)}.file_size")
            return True if _size < 20971520 else False


    @property
    def _write_content_to_database(self) -> bool:
        try:
            self.session.add(Content(
                type_content=self._content_type,
                loader_id=self.message.from_user.id,
                file_id=self._get_file_id,
                moderated=self._this_is_moderator
            ))
            self.session.commit()
            self.session.close()
            return True
        except Exception as e:
            log.error("Error add content to database. Details: %s" % e)
            return False

    @property
    def add_content(self) -> str:
        try:
            if not self._check_file_size:
                return dict_reply["big_size_file"]

            if not self._allow_load:
                return dict_reply["content_load_not_allowed"]

            if not self._write_content_to_database:
                return dict_reply["database_error_content"]

            return dict_reply["content_success"]
        except Exception as e:
            log.warning("Add content init error. Details: %s" % e)
            return dict_reply["internal_error"] % e.__class__.__name__

    def __str__(self) -> str:
        return self.add_content
