from static.menu import dictionary as menu_dict

dictionary = {
    "start_message": "Привет. Воспользовавшись меню ниже, ты можешь получить "
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
    "internal_error": "Ошибка...\n\nДетали: <code>%s</code>",
    "banned_user": "Забанен! Иди на хуй",
    "group_answer": "Извини, этот бот не обслуживает группы.",
    "throttling_message": "Слишком много запросов.",
    "throttling_use_again": "Блокировка снята.",
    "take_content": "Отправь мне контент который ты хочешь добавить. Можно "
                    "одновременно отправлять разные типы (бот поддерживат фото/видео/голосовые), но на модерации "
                    "может быть не более 100 элементов. Если вы загружаете контент, который не соответствует "
                    "тематике, то получите бан.",
    "invalid_content_type": "Контент этого типа не поддерживается.",
    "content_success": "Принято 👌",
    "content_load_not_allowed": "Не удалось получить разрешение на загрузку.",
    "database_error_content": "Не удалось добавить запись в базу данных."
}
