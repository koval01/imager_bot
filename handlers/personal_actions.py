from aiogram import types
from dispatcher import dp
from static.messages import dictionary as dict_reply
from static.menu import build_menu


@dp.message_handler(commands=['start', 'help'], is_moderator=True)
async def send_welcome_moderator(msg: types.Message):
    await msg.reply(dict_reply["start_message"], reply_markup=build_menu("moderator_start_menu"))


@dp.message_handler(commands=['start', 'help'], is_moderator=False)
async def send_welcome(msg: types.Message):
    await msg.reply(dict_reply["start_message"], reply_markup=build_menu("start_menu"))


@dp.message_handler()
async def any_messages(msg: types.Message):
    await msg.reply(dict_reply["unknown_answer"])
