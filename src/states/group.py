from aiogram.fsm.state import State, StatesGroup


class CreateGroup(StatesGroup):
    name = State()
    description = State()


class UpdateGroup(StatesGroup):
    old_name = State()
    name = State()
    description = State()
