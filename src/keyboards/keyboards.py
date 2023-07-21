from typing import List, Tuple

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_menu_button = [
    [KeyboardButton(text="Создать новую группу"), KeyboardButton(text="Удалить группу паролей"),
     KeyboardButton(text="Обновить информацию о группе")],
    [KeyboardButton(text="Создать новый пароль"), KeyboardButton(text="Удалить пароль"),
     KeyboardButton(text="Обновить пароль")],
    [KeyboardButton(text="Показать пароли из группы"), KeyboardButton(text="Найти пароль")]
]

main_menu = ReplyKeyboardMarkup(keyboard=main_menu_button, resize_keyboard=True,
                                input_field_placeholder="Выберите действие")


def create_dynamic_keyboard(data_buttons: List[Tuple[str, str]], count_rows: int = 2) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for text, callback_data in data_buttons:
        builder.button(text=text, callback_data=callback_data)
    builder.adjust(count_rows)
    return builder
