import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

TOKEN = os.getenv('TOURNAMENT_ADMIN_TOKEN')
USER_TOKEN = os.getenv('TOURNAMENT_TOKEN')
ADMIN = int(os.getenv('ADMIN'))
bot = Bot(TOKEN)
users_bot = Bot(USER_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


async def set_default_commands(dp: Dispatcher) -> None:
    await dp.bot.set_my_commands(
        [
            BotCommand('start', 'Запустить бота'),
            BotCommand('help', 'Помощь'),
            BotCommand('fill_table', 'Заполнить таблицу'),
            BotCommand('clear_table', 'Очистить таблицу'),
            BotCommand('approve_games', 'Утвердить матчи'),
            BotCommand('launch', 'Запустить мониторинг'),
            BotCommand('break', 'Остановить мониторинг'),
            BotCommand('finish', 'Закончить турнир'),
            BotCommand('add_rating', 'Заполнить текущий рейтинг'),
            BotCommand('reset_overall_rating', 'Обнулить общий рейтинг')
        ]
    )