from aiogram.types import Message, ReplyKeyboardMarkup

from content.manager import Manager
from static.config import DISLIKE_DISABLED
from static.menu import build_menu, dictionary as menu_dict
from static.messages import dictionary as dict_reply
from utils.log_module import logger
from utils.moderator import CheckModerator


class Selector:
    def __init__(self, msg: Message, text_order_mode: str, real_text: str = None) -> None:
        self.msg = msg
        self.user_text = self.msg.text
        self.text_order_mode = text_order_mode
        self.real_text = real_text
        self.order_mode = lambda x: \
            self.text_order_mode == menu_dict["rand_or_last"][x]
        self.reply_lambda = lambda x, menu: \
            dict(text=dict_reply[x], reply_markup=menu)

    @property
    async def select_type(self) -> str:
        return [
            ["photo", "video", "voice"][i]
            for i, x in enumerate(menu_dict["select_mode"])
            if x == self.user_text
        ][0]

    @property
    async def _select_order_mode(self) -> bool or None:
        return True if self.order_mode(0) else (
            False if self.order_mode(1) else None)

    async def reply_selector(self) -> Message:
        async def _dislike_try(content_id_: int, menu_: ReplyKeyboardMarkup) -> Message:
            dislike_process = await Manager().add_dislike(content_id_) \
                if menu_dict["next_content"][2] == self.real_text else "skip"
            if not dislike_process:
                return await self.msg.reply(**self.reply_lambda(
                    "dislike_sent_error", menu_))
            elif dislike_process != "skip":
                if DISLIKE_DISABLED:
                    return await self.msg.reply(**self.reply_lambda(
                        "error_action", menu_))
                return await self.msg.reply(**self.reply_lambda(
                    "dislike_sent", menu_))

        try:
            type_ = await self.select_type
            content_id, file_id = await Manager(
                type_content=type_, message=self.msg,
                get_content_random=await self._select_order_mode
            ).get_content()
            await logger.info(
                f"Get content. Data: content_id = {content_id}, file_id = {file_id}")
            if not content_id or not file_id:
                return await self.msg.reply(dict_reply["no_content"])
            menu = await build_menu("next_content")
            moderator_status = await CheckModerator(self.msg)._check_user
            need_protect = True \
                if not moderator_status \
                else False
            await _dislike_try(content_id, menu)
            return await eval(
                f"self.msg.reply_{type_}(file_id, "
                f"caption=caption, reply_markup=menu, protect_content=need_protect)",
                {"caption": str(content_id), "menu": menu, "need_protect": need_protect}
            )
        except Exception as e:
            await logger.error("Error send content (selector). Details: %s" % e)
            return await self.msg.reply(dict_reply["internal_error"] % e.__class__.__name__)
