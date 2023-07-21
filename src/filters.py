from typing import Dict, Any, Awaitable, Callable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from utils import check_telegram_profile_message


class CheckBlockUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        _, error = await check_telegram_profile_message(message=event)
        if error:
            await event.answer(error, show_alert=True)
            return
        else:
            return await handler(event, data)
