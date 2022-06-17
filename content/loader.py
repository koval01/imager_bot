from aiogram import types
from database.controller import async_sql_session, engine as sql_engine
from sqlalchemy.future import select
from database.models import Content
from static import config
from utils.moderator import CheckModerator
from static.messages import dictionary as dict_reply
from utils.decorators import async_timer
from utils.log_module import logger


class LoaderContent:
    def __init__(self, message: types.Message) -> None:
        self.session = async_sql_session
        self.message = message

    @property
    async def _content_type(self) -> str:
        try:
            _type = self.message.content_type
            return "video" if _type == "video_note" else \
            [
                t for t in ["photo", "video", "voice"]
                if t == _type
            ][0]
        except Exception as e:
            await logger.warning("Error resolve content type (%s). Details: %s" % (
                self._content_type.__name__, e))
            return ""

    @property
    @async_timer
    async def _check_content_on_moderation(self) -> int:
        async with self.session.begin() as session:
            moderated_ = False
            q = select(Content).where(
                Content.moderated == moderated_,
                Content.loader_id == self.message.from_user.id)
            result = await session.execute(q)
            curr = result.scalars()
            data = curr.all()
            await session.close()
        return len(data)

    @property
    async def _allow_load(self) -> bool:
        return True if (await self._content_type and (
                await self._check_content_on_moderation <= 100)
        ) else False

    @property
    async def _this_is_moderator(self) -> bool:
        user_id = self.message.from_user.id
        return True if await CheckModerator(self.message).get \
                       or user_id == config.BOT_OWNER else False

    async def _video_note_check(self, current_type: str) -> str:
        try:
            if self.message.video_note:
                return "video_note"
        except Exception as e:
            await logger.error("Error check content type (%s). Details: %s" % (
                self._video_note_check.__name__, e))
        return current_type

    @property
    async def _get_file_id(self) -> str:
        _type = await self._content_type
        if _type == "photo":
            return self.message.photo[-1:][0].file_id
        return eval(f"self.message.{self._video_note_check(_type)}.file_id")

    @property
    async def _check_file_size(self) -> bool:
        _type = await self._content_type
        if _type == "photo":
            return True
        else:
            _size = eval(f"self.message.{self._video_note_check(_type)}.file_size")
            return True if _size < 20971520 else False

    @property
    @async_timer
    async def _write_content_to_database(self) -> bool:
        try:
            async with self.session.begin() as session:
                session.add(Content(
                    type_content=self._content_type,
                    loader_id=self.message.from_user.id,
                    file_id=await self._get_file_id,
                    moderated=await self._this_is_moderator
                ))
                await session.commit()
                await session.close()
            return True
        except Exception as e:
            await logger.error("Error add content to database. Details: %s" % e)
            return False

    @property
    async def add_content(self) -> str:
        try:
            if not await self._check_file_size:
                return dict_reply["big_size_file"]

            if not await self._allow_load:
                return dict_reply["content_load_not_allowed"]

            if not await self._write_content_to_database:
                return dict_reply["database_error_content"]

            return dict_reply["content_success"]
        except Exception as e:
            await logger.warning("Add content init error. Details: %s" % e)
            return dict_reply["internal_error"] % e.__class__.__name__

    @property
    async def load(self) -> str:
        return await self.add_content
