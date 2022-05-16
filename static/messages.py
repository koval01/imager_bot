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
    "canceled_action": "Хорошо, пошли в главное меню."
}
