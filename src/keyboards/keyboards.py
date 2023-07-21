from typing import List, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_menu_button = [
    [InlineKeyboardButton(text="Создать новую группу", callback_data="create_new_group"),
     InlineKeyboardButton(text="Удалить группу паролей", callback_data="delete_group_passwords"),
     InlineKeyboardButton(text="Обновить информацию о группе", callback_data="update_group")],
    [InlineKeyboardButton(text="Создать новый пароль", callback_data="create_new_password"),
     InlineKeyboardButton(text="Удалить пароль", callback_data="delete_pass_button"),
     InlineKeyboardButton(text="Обновить пароль", callback_data="update_pass_button")],
    [InlineKeyboardButton(text="Показать пароли из группы", callback_data="get_passwords_by_group"),
     InlineKeyboardButton(text="Найти пароль", callback_data="search_password")]
]
main_menu = InlineKeyboardMarkup(inline_keyboard=main_menu_button)


def create_dynamic_keyboard(data_buttons: List[Tuple[str, str]], count_rows: int = 2) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for text, callback_data in data_buttons:
        builder.button(text=text, callback_data=callback_data)
    builder.adjust(count_rows)
    return builder
