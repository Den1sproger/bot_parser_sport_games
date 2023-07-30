from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from ..bot_config import dp, ADMIN
from ..keyboards import main_kb


WELCOME = """
Добрый день
❗️❗️❗️Вы администратор системы❗️❗️❗️
👨🏻‍⚕️👨🏻‍⚕️👨🏻‍⚕️
"""

HELP_TEXT = """
/start - запустить бота
/help - помощь
/fill_table - заполнить таблицу
/clear_table - очистить таблицу
/approve_games - утвердить матчи
/launch - запустить мониторинг
/break - остановить мониторинг
/stop - прервать диалог
/add_rating - Заполнить текущий рейтинг
"""


@dp.message_handler(Command('start'), user_id=ADMIN)
async def start(message: types.Message) -> None:
    await message.answer(WELCOME, reply_markup=main_kb)


@dp.message_handler(Text(equals='🆘Помощь'), user_id=ADMIN)
@dp.message_handler(Command('help'), user_id=ADMIN)
async def help(message: types.Message) -> None:
    await message.answer(HELP_TEXT)