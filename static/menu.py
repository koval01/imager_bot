from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


dictionary = {
    "start_menu": ["Смотреть", "Добавить"],
    "moderator_start_menu": ["Смотреть", "Добавить", "Проверить"],
    "select_mode": ["Фото", "Видео", "Голосовые"],
    "cancel": ["🙅‍♂️"],
    "next_content": ["🙅‍♂️", "➡️"]
}

def build_menu(name: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
        *tuple(KeyboardButton(e) for e in dictionary[name])
    )
