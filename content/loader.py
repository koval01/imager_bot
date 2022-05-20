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
            log.error("Error detect content type. Details: %s" % e)
            return ""

    @property
    def _check_content_on_moderation(self) -> int:
        x = self.session.query(Content).filter_by(
            moderated=False, loader_id=self.message.from_user.id)
        return x.count()

    @property
    def _allow_load(self) -> bool:
        return True if (self._content_type and (
                self._check_content_on_moderation <= 100)
        ) else False

    @property
    def _this_is_moderator(self) -> bool:
        user_id = self.message.from_user.id
        return True if user_id in config.MODERATORS \
                       or user_id == config.BOT_OWNER else False

    @property
    def _get_file_id(self) -> str:
        _type = self._content_type
        if _type == "photo":
            return self.message.photo[-1:][0].file_id
        return eval(f"self.message.{_type}.file_id")

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
            log.error("Error write content to database. Details: %s" % e)
            return False

    @property
    def add_content(self) -> str:
        try:
            return dict_reply["content_success"] \
                if self._write_content_to_database else (
                    dict_reply["database_error_content"]
                    if self._allow_load
                    else dict_reply["content_load_not_allowed"]
            )
        except Exception as e:
            log.error("Error add content. Details: %s" % e)
            return dict_reply["internal_error"] % e.__class__.__name__

    def __str__(self) -> str:
        return self.add_content
