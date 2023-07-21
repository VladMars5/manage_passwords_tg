import asyncio

from aiogram import Bot, Dispatcher
import logging

from config import TOKEN_BOT
from handlers.group import router as router_group
from handlers.main_command import router as router_main
from handlers.other import router as router_other
from handlers.password import router as router_password


async def main():
    dp = Dispatcher()
    dp.include_router(router_main)
    dp.include_router(router_group)
    dp.include_router(router_password)
    dp.include_router(router_other)
    bot = Bot(TOKEN_BOT)
    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
