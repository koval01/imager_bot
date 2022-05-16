from aiogram import types
from aiogram.dispatcher import FSMContext
from dispatcher import dp
from static.messages import dictionary as dict_reply
from static.menu import build_menu, dictionary as dict_menu
from handlers.fsm import ViewContent


@dp.message_handler(commands=['start', 'help'], is_moderator=True)
async def send_welcome_moderator(msg: types.Message):
    await msg.reply(dict_reply["start_message"], reply_markup=build_menu("moderator_start_menu"))


@dp.message_handler(commands=['start', 'help'], is_moderator=False)
async def send_welcome(msg: types.Message):
    await msg.reply(dict_reply["start_message"], reply_markup=build_menu("start_menu"))


@dp.message_handler(lambda msg: msg.text == dict_menu["start_menu"][0])
async def init_select(msg: types.Message):
    await ViewContent.select_mode.set()
    await msg.reply(dict_reply["select_mode"], reply_markup=build_menu("select_mode"))


@dp.message_handler(lambda message: message.text not in dict_menu["select_mode"], state=ViewContent.select_mode)
async def invalid_select_content(msg: types.Message):
    await msg.reply(dict_reply["error_select"], reply_markup=build_menu("select_mode"))


@dp.message_handler(lambda message: message.text not in dict_menu["next_content"], state=ViewContent.view_mode)
async def invalid_select_action(msg: types.Message):
    await msg.reply(dict_reply["error_action"], reply_markup=build_menu("next_content"))


@dp.message_handler(lambda message: message.text == dict_menu["next_content"][0], state=ViewContent.view_mode)
async def cancel_action(msg: types.Message, state: FSMContext):
    await msg.reply(dict_reply["canceled_action"], reply_markup=build_menu("start_menu"))
    await state.finish()


@dp.message_handler(lambda message: message.text in dict_menu["select_mode"], state=ViewContent.select_mode)
async def select_content(msg: types.Message, state: FSMContext):
    await ViewContent.next()
    await state.update_data(select=msg.text)
    await msg.reply(dict_reply["view_content"], reply_markup=build_menu("next_content"))


@dp.message_handler()
async def any_messages(msg: types.Message):
    await msg.reply(dict_reply["unknown_answer"])
