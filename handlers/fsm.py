from aiogram.dispatcher.filters.state import State, StatesGroup


class ViewContent(StatesGroup):
    select_mode = State()
    view_mode = State()


class TakeContent(StatesGroup):
    wait_content = State()
    load_confirm = State()
