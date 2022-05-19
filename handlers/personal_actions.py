from aiogram import types
from aiogram.dispatcher import FSMContext
from dispatcher import dp
from static.messages import dictionary as dict_reply
from static.menu import build_menu, dictionary as dict_menu
from handlers.fsm import ViewContent
from content.selector import Selector, Manager
from utils.throttling import rate_limit


async def start_bot(msg: types.Message, moderator: bool = False):
    menu = "moderator_start_menu" if moderator else "start_menu"
    await msg.reply(dict_reply["start_message"], reply_markup=build_menu(menu)) \
        if Manager(user_id=msg.from_user.id).check_user \
        else await msg.reply(dict_reply["internal_error"] % "ErrorUserModel")


@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
@rate_limit(120, 'group_init')
async def group_handler(msg: types.Message):
    await msg.reply(dict_reply["group_answer"])


@dp.message_handler(is_banned=True)
@rate_limit(600, 'banned_user')
async def send_welcome_moderator(msg: types.Message):
    await msg.answer(dict_reply["banned_user"])


@dp.message_handler(commands=['start', 'help'], is_moderator=True)
async def send_welcome_moderator(msg: types.Message):
    await start_bot(msg, moderator=True)


@dp.message_handler(commands=['start', 'help'])
@rate_limit(3, 'start_command')
async def send_welcome(msg: types.Message):
    await start_bot(msg)


@dp.message_handler(lambda msg: msg.text == dict_menu["start_menu"][0])
async def init_select(msg: types.Message):
    await ViewContent.select_mode.set()
    await msg.reply(dict_reply["select_mode"], reply_markup=build_menu("select_mode"))


@dp.message_handler(lambda message: message.text not in dict_menu["select_mode"], state=ViewContent.select_mode)
@rate_limit(2, 'error_select_content_type')
async def invalid_select_content(msg: types.Message):
    await msg.reply(dict_reply["error_select"], reply_markup=build_menu("select_mode"))


@dp.message_handler(lambda message: message.text not in dict_menu["next_content"], state=ViewContent.view_mode)
@rate_limit(2, 'error_select_content_action')
async def invalid_select_action(msg: types.Message):
    await msg.reply(dict_reply["error_action"], reply_markup=build_menu("next_content"))


@dp.message_handler(lambda message: message.text == dict_menu["next_content"][0], state=ViewContent.view_mode)
async def cancel_action(msg: types.Message, state: FSMContext):
    await msg.reply(dict_reply["canceled_action"], reply_markup=build_menu("start_menu"))
    await state.finish()


@dp.message_handler(lambda message: message.text == dict_menu["next_content"][1], state=ViewContent.view_mode)
@rate_limit(1, 'next_content')
async def next_action(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        msg.text = data["select"]
        await Selector(msg).reply


@dp.message_handler(lambda message: message.text in dict_menu["select_mode"], state=ViewContent.select_mode)
async def select_content(msg: types.Message, state: FSMContext):
    await ViewContent.next()
    await state.update_data(select=msg.text)
    await msg.reply(dict_reply["view_content"], reply_markup=build_menu("next_content"))
    await Selector(msg).reply


@dp.message_handler()
@rate_limit(3, 'any_data')
async def any_messages(msg: types.Message):
    await msg.reply(dict_reply["unknown_answer"])
