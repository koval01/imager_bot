from aiogram import types
from aiogram.types import ChatType, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import Throttled
from dispatcher import dp, bot
from static.messages import dictionary as dict_reply
from static.menu import build_menu, dictionary as dict_menu
from handlers.fsm import ViewContent, TakeContent
from content.selector import Selector
from content.loader import LoaderContent
from content.manager import Manager
from utils.throttling import rate_limit
import logging as log


@dp.message_handler(chat_type=[ChatType.SUPERGROUP, ChatType.GROUP])
@rate_limit(60, 'group_init')
async def group_handler(msg: types.Message):
    await msg.reply(dict_reply["group_answer"])


@dp.message_handler(is_full_banned=True)
@rate_limit(2, 'full_banned_user')
async def full_banned_user(msg: types.Message):
    await msg.reply(dict_reply["full_ban"])


@dp.message_handler(lambda message: message.text == dict_menu["next_content"][0], state=[
    ViewContent.view_mode, TakeContent.wait_content
])
async def cancel_action(msg: types.Message, state: FSMContext):
    await msg.reply(dict_reply["canceled_action"], reply_markup=build_menu("start_menu"))
    await state.finish()


@dp.message_handler(commands=['start', 'help'], state="*")
@rate_limit(1, 'start_command')
async def send_welcome(msg: types.Message):
    await msg.reply(dict_reply["start_message"], reply_markup=build_menu("start_menu"))


@dp.message_handler(commands=['test_log'], state="*", is_owner=True)
async def test_log_handler(msg: types.Message):
    await msg.reply(dict_reply["test_log_reply"])
    log.info("Test log called from bot by admin.")


@dp.message_handler(commands=['news'], is_moderator=True)
async def news_send_handler(msg: types.Message):

    async def _send_messages() -> int:
        users = Manager().get_all_users_ids
        successes = 0
        for user_id in users:
            try:
                await bot.send_message(user_id, msg.get_args())
                successes += 1
            except Exception as e:
                log.info("Error send message. Details: %s" % e)
        return successes

    await msg.reply(dict_reply["init_news_send"])
    successes_count = \
        await _send_messages()
    await msg.reply(dict_reply["finish_news_send"] % successes_count)


@dp.message_handler(lambda msg: msg.text == dict_menu["start_menu"][0])
async def init_select(msg: types.Message):
    await ViewContent.select_mode.set()
    await msg.reply(dict_reply["select_mode"], reply_markup=build_menu("select_mode"))


@dp.message_handler(lambda msg: msg.text == dict_menu["start_menu"][1], is_banned=True)
@rate_limit(1.5, 'banned_user_init_load_content')
async def banned_user_init_load_content(msg: types.Message):
    await msg.reply(dict_reply["banned_user"])


@dp.message_handler(lambda msg: msg.text == dict_menu["start_menu"][1])
async def init_load_content(msg: types.Message):
    await TakeContent.wait_content.set()
    await msg.reply(dict_reply["take_content"], reply_markup=build_menu("cancel"))


@dp.message_handler(content_types=[
    ContentType.PHOTO, ContentType.VIDEO, ContentType.VIDEO_NOTE, ContentType.VOICE
], state=TakeContent.wait_content, is_banned=True)
@rate_limit(1, 'banned_user_try_load_content')
async def wait_content_user_banned(msg: types.Message):
    await msg.reply(dict_reply["banned_user"])


@dp.message_handler(content_types=[
    ContentType.PHOTO, ContentType.VIDEO, ContentType.VIDEO_NOTE, ContentType.VOICE
], state=TakeContent.wait_content)
async def wait_content_handler(msg: types.Message):
    response_status = str(LoaderContent(msg))
    if response_status != dict_reply["content_success"]:
        return await msg.reply(response_status)
    try:
        await dp.throttle('start', rate=1)
    except Throttled:
        pass
    else:
        await msg.answer(response_status)


@dp.message_handler(content_types=ContentType.DOCUMENT, state=TakeContent.wait_content)
async def wait_content_handler_file(msg: types.Message):
    await msg.reply(dict_reply["content_is_file"])


@dp.message_handler(content_types=ContentType.ANY, state=TakeContent.wait_content)
async def wait_content_handler_invalid_type(msg: types.Message):
    await msg.reply(dict_reply["invalid_content_type"])


@dp.message_handler(lambda message: message.text not in dict_menu["select_mode"], state=ViewContent.select_mode)
@rate_limit(0.6, 'error_select_content_type')
async def invalid_select_content(msg: types.Message):
    await msg.reply(dict_reply["error_select"], reply_markup=build_menu("select_mode"))


@dp.message_handler(lambda message: message.text not in dict_menu["next_content"], state=ViewContent.view_mode)
@rate_limit(0.6, 'error_select_content_action')
async def invalid_select_action(msg: types.Message):
    await msg.reply(dict_reply["error_action"], reply_markup=build_menu("next_content"))


@dp.message_handler(lambda message: message.text == dict_menu["next_content"][1], state=ViewContent.view_mode)
@rate_limit(0.3, 'next_content')
async def next_action(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        msg.text = data["select"]
        await Selector(msg).reply_selector


@dp.message_handler(lambda message: message.text in dict_menu["select_mode"], state=ViewContent.select_mode)
async def select_content(msg: types.Message, state: FSMContext):
    await ViewContent.next()
    await state.update_data(select=msg.text)
    await msg.reply(dict_reply["view_content"], reply_markup=build_menu("next_content"))
    await Selector(msg).reply_selector


@dp.message_handler()
@rate_limit(0.3, 'any_data')
async def any_messages(msg: types.Message):
    await msg.reply(dict_reply["unknown_answer"], reply_markup=build_menu("start_menu"))
