import logging

from aiogram import executor
from telegram_bot import dp, set_default_commands
from telegram_bot.handlers.monitoring import *
from telegram_bot.handlers.inline_buttons import *
from telegram_bot.handlers.start import *
from telegram_bot.handlers.main_panel import *


# LOG_FILENAME = "/home/tournament_management/py_log.log"
# logging.basicConfig(level=logging.INFO, filename=LOG_FILENAME, filemode="w")


async def on_startup(_):
    await set_default_commands(dp)


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)