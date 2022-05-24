from static.menu import build_menu, dictionary as menu_dict
from static.messages import dictionary as dict_reply
from aiogram.types import Message
from content.manager import Manager


class Selector:
    def __init__(self, msg: Message) -> None:
        self.msg = msg
        self.user_text = self.msg.text

    @property
    def select_type(self) -> str:
        return [
            ["photo", "video", "voice"][i]
            for i, x in enumerate(menu_dict["select_mode"])
            if x == self.user_text
        ][0]

    @property
    async def reply(self) -> Message:
        try:
            type_ = self.select_type
            data = str(Manager(type_content=type_, message=self.msg))
            if not data:
                await self.msg.reply(dict_reply["no_content"])
            else:
                await eval(f"self.msg.reply_{type_}(data, reply_markup=build_menu(\"next_content\"))")
        except Exception as e:
            await self.msg.reply(dict_reply["internal_error"] % e.__class__.__name__)
