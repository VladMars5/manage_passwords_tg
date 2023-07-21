from aiogram.fsm.state import State, StatesGroup


class CreatePassword(StatesGroup):
    group_id = State()
    service_name = State()
    login = State()
    password = State()


class DeletePassword(StatesGroup):
    group_id = State()
    service_name = State()
    login = State()
