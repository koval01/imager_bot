from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


dictionary = {
    "start_menu": ["Смотреть", "Добавить", "Топ"],
    "select_mode": ["Фото", "Видео", "Голосовые"],
    "cancel": ["🙅‍♂️"],
    "next_content": ["🙅‍♂️", "➡️"],
    "rand_or_last": ["Рандом", "По порядку"]
}

def build_menu(name: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).row(
        *tuple(KeyboardButton(e) for e in dictionary[name])
    )
