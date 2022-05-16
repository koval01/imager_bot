from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


dictionary = {
    "start_menu": ["Смотреть", "Добавить"],
    "moderator_start_menu": ["Смотреть", "Добавить", "Проверить"],
    "select_type": ["Фото", "Видео", "Голосовые"],
    "cancel": ["Выйти"]
}

def build_menu(name: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).row(
        *tuple(KeyboardButton(e) for e in dictionary[name])
    )
