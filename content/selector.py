from static.menu import build_menu, dictionary as menu_dict
from static.messages import dictionary as dict_reply
from aiogram.types import Message
from content.manager import Manager
import logging as log


class Selector:
    def __init__(self, msg: Message, text_order_mode: str) -> None:
        self.msg = msg
        self.user_text = self.msg.text
        self.text_order_mode = text_order_mode

    @property
    def select_type(self) -> str:
        return [
            ["photo", "video", "voice"][i]
            for i, x in enumerate(menu_dict["select_mode"])
            if x == self.user_text
        ][0]

    @property
    def _select_order_mode(self) -> bool or None:
        _mode = lambda x: self.text_order_mode == menu_dict["rand_or_last"][x]
        return True if _mode(0) else (False if _mode(1) else None)

    async def reply_selector(self) -> Message:
        try:
            type_ = self.select_type
            content_id, file_id = await Manager(
                type_content=type_, message=self.msg, get_content_random=self._select_order_mode
            ).get_content
            log.info(f"Get content. Data: content_id = {content_id}, file_id = {file_id}")
            if not content_id or not file_id:
                return await self.msg.reply(dict_reply["no_content"])
            else:
                menu = await build_menu("next_content")
                return await eval(
                    f"self.msg.reply_{type_}(file_id, "
                    f"caption=str(content_id), reply_markup=menu, protect_content=True)"
                )
        except Exception as e:
            return await self.msg.reply(dict_reply["internal_error"] % e.__class__.__name__)
            log.error("Error send content (selector). Details: %s" % e)
