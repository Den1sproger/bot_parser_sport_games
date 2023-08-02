import os
import urllib3
import time
import logging

import requests

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
            BotCommand('add_rating', 'Заполнить текущий рейтинг')
        ]
    )


def send_msg(msg_text: str,
             chat_id: str | int,
             token: str = USER_TOKEN,
             retry: int = 5) -> None:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        requests.post(
            url=url,
            timeout=5,
            verify=False,
            data={
                'chat_id':  int(chat_id),
                'text': msg_text,
            }
        )
    except Exception as _ex:
        if retry:
            logging.info(f"retry={retry} send_msg => {_ex}")
            retry -= 1
            time.sleep(5)
            send_msg(msg_text, chat_id, token, retry)
        else:
            logging.info(f'Cannot send message to chat_id = {chat_id}')