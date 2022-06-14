from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from static.config import DONATE_LINK


dictionary = {
    "start_menu": ["Смотреть", "Добавить", "Топ", "Донат"],
    "select_mode": ["Фото", "Видео", "Голосовые"],
    "cancel": ["🙅‍♂️"],
    "next_content": ["🙅‍♂️", "➡️"],
    "rand_or_last": ["Рандом", "По порядку"]
}

donate_inline_button = InlineKeyboardMarkup().add(
    InlineKeyboardButton('Донат', url=DONATE_LINK)
)

def build_menu(name: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).add(
        *tuple(KeyboardButton(e) for e in dictionary[name])
    )
