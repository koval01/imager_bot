from static.menu import donate_inline_button, dictionary as menu_dict
from static.config import MANAGER_ID
from random import uniform as float_rand

dictionary = {
    "start_message":
        "Привет. Воспользовавшись меню ниже, ты можешь получить "
        "желаемый тип контента. Также можешь добавить свой.",
    "unknown_answer": "Я не знаю что тебе ответить на это.",
    "select_mode": "Выбери тип контента.",
    "error_select": "Не удалось выбрать тип контента.",
    "error_action": "Неверное действие.",
    "view_content": "Используй кнопку %s, чтобы листать или %s чтобы выйти." % (
        menu_dict["next_content"][1], menu_dict["next_content"][0]
    ),
    "canceled_action": "Хорошо, пошли в главное меню.",
    "no_content": "Нет никакого контента в этой категории, извини. Возможно ты уже всё просмотрел.",
    "internal_error": "Ошибка...\nКласс: <code>%s</code>",
    "banned_user": "Забанен! Иди на хуй",
    "full_ban":
        "К сожалению для тебя этот бот недоступен.\nВозможно, тебе ограничил доступ технический "
        "администратор, обратись к %s, если считаешь это ошибкой." % MANAGER_ID,
    "group_answer": "Извини, этот бот не обслуживает группы.",
    "throttling_message": "Слишком много запросов.",
    "throttling_use_again": "Блокировка снята.",
    "take_content":
        "Отправь мне контент который ты хочешь добавить. Можно "
        "одновременно отправлять разные типы (бот поддерживат фото/видео/голосовые), но на модерации "
        "может быть не более 100 элементов. Если вы загружаете контент, который не соответствует "
        "тематике, то получите бан.",
    "invalid_content_type": "Контент этого типа не поддерживается.",
    "content_success": "Принято 👌",
    "content_load_not_allowed": "Не удалось получить разрешение на загрузку.",
    "database_error_content": "Не удалось добавить запись в базу данных.",
    "big_size_file": "Максимальный вес файла - 20 мегабайт.",
    "content_is_file": "Загрузка файла не поддерживается.",
    "test_log_reply": "Отправляем тестовый лог",
    "init_news_send": "Начинаем рассылку сообщения.",
    "finish_news_send": "Рассылка завершена. Пользователей получило сообщение - %d",
    "rand_or_last": "Как выдавать контент?",
    "rand_or_last_error_select": "Ошибка. Неверный вариант выдачи контента.",
    "news_send_error": "Не удалось разослать сообщение, возможно оно слишком длинное.",
    "news_template": "%s\n\nОтправил: %s",
    "top_list_template": "%d. %s - %d медиа",
    "top_list_comment": "Учитывается контент прошедший модерацию и сейчас отображается в выдаче.",
    "donate_template":
        "Ты можешь поддержать бота финансово, чтобы он мог дальше работать и обновлятся. "
       "Люди которые задонатили больше <code>100</code> гривен - "
       "<b>будут упомянуты в новостях бота</b>. "
       "<i>Ниже кнопка для перехода на страницу доната</i>.",
    "dislike_sent": "Дизлайк отправлен, пошли дальше.",
    "dislike_sent_error": "Ошибка, не удалось поставить дизлайк. Обратитесь к администратору.",
    "already_disliked": "Можно поставить только один дизлайк.",
    "error_action": "Не удалось выполнить действие.",
    "news_command_pattern": "/news текст",
    "timings_template":
        "{%d} <i>%s</i>: " \
        "<code>%.4f</code>/<code>%.4f</code>/<code>%.4f</code>/" \
        "<code>%.4f</code>/<code>%.4f</code>",
    "sys_data_template": "CPU: %d%%; MEM: %s/%s (%d%%)",
    "timings_title_template":
        "{len} <i>function</i>: "
        "<code>min</code>/<code>avg</code>/<code>max</code>/"
        "<code>50%</code>/<code>95%</code>",
    "build_current": "Сейчас активна сборка",
    "build_updated": "Собрана новая версия",
    "build_data_template": "%s\n"
                           "\nID: <code>%s</code>"
                           "\nВремя инициализации: <i>%s</i>"
                           "\nВремя публикации: <i>%s</i>"
                           "\nОписание: (%s)"
                           "\nЖурнал сборки: <b><a href=\"%s\">Посмотреть</a></b>"
}

async def donate_answer(random: bool = False) -> (dict, bool):
    return (dict(
            text=dictionary["donate_template"],
            reply_markup=donate_inline_button), True) \
        if not random or float_rand(0, 1) >= 0.97 \
        else (None, False)
