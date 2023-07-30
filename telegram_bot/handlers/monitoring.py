import threading
import asyncio

import schedule

from aiogram import types
from aiogram.utils.exceptions import ChatNotFound, CantInitiateConversation
from aiogram.dispatcher.filters import Command, Text
from ..bot_config import dp, ADMIN, users_bot
from data_processing import Monitoring, Comparison
from ..keyboards import (get_select_tourn_type_ikb,
                         start_mail_ikb)
from database import (Database,
                      get_prompt_view_nick_by_id,
                      get_prompt_view_rating,
                      get_prompt_view_chat_id_by_tourn,
                      get_prompt_view_games_id)



current_selected_types = []
thread_monitoring: threading.Thread
thread_active = False


async def monitoring(*tourn_types) -> None:
    m = Monitoring(*tourn_types)
    result = m.check_status()

    db = Database()
    if result:
        for item in result:     # for every tournament type in completed types

            comparison = Comparison()
            for ws in comparison.wss:           # for every worksheet in the worksheets in the spreadshhet

                tourn_name = ws.title           # tournament name
                if item in tourn_name.upper():

                    users = db.get_data_list(get_prompt_view_chat_id_by_tourn(tourn_name))
                    for user in users:

                        # creating leaderboard
                        user_chat_id = user['chat_id']
                        nickname = db.get_data_list(
                            get_prompt_view_nick_by_id(user_chat_id)
                        )[0]['nickname']

                        msg_text = f'🏆Таблица лидеров {tourn_name}:\n'

                        rating = db.get_data_list(get_prompt_view_rating(tourn_name))
                        own_number = 0
                        own_score = 0
                        count = 0
                        for participant in rating:

                            count += 1
                            if count <= 10:
                                msg_text += f'{count}. {participant["nickname"]}: {participant["scores"]}\n'
                            if participant["nickname"] == nickname:
                                own_number = count
                                own_score = participant["scores"]
                                if count >= 10: break

                        # user's position
                        msg_text += f'\nВаша позиция в списке: {own_number} из {len(rating)}' \
                                    f'\n{own_number}{nickname}: {own_score}'
                        
                        try:
                            await users_bot.send_message(
                                chat_id=user_chat_id, text=msg_text
                            )
                        except (ChatNotFound, CantInitiateConversation):
                            pass
        
        # time.sleep(10)

def mon_coroutine_wrapper(*tourn_types):
    asyncio.run(monitoring(*tourn_types))


def run_monitoring(types: list[str]) -> None:
    schedule.every(20).minutes.do(mon_coroutine_wrapper, *types)
    while thread_active:
        schedule.run_pending()
        

@dp.message_handler(Text(equals='🚀🚀Запустить мониторинг'), user_id=ADMIN)
@dp.message_handler(Command('launch'), user_id=ADMIN)
async def launch_monitoring(message: types.Message) -> None:
    if thread_active:
        await message.answer('Мониторинг уже запущен')
        return
    
    await message.answer(
        text='Выберите типы турниров',
        reply_markup=get_select_tourn_type_ikb()
    )


@dp.message_handler(Text(equals='❌Закончить мониторинг'), user_id=ADMIN)
@dp.message_handler(Command('break'), user_id=ADMIN)
async def break_monitoring(message: types.Message) -> None:
    global thread_monitoring, thread_active

    if not thread_active:
        await message.answer('Мониторинг не запущен')
    else:
        thread_active = False
        thread_monitoring.join()
        await message.answer('✅Мониторинг остановлен')


@dp.callback_query_handler(lambda callback: callback.data.startswith('select_type_'))
async def select_type(callback: types.CallbackQuery) -> None:
    tourn_type = callback.data.replace('select_type_', '').upper()

    global current_selected_types
    current_selected_types.append(tourn_type)

    await callback.message.edit_reply_markup(
        reply_markup=get_select_tourn_type_ikb(current_selected_types)
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith('unselect_type_'))
async def unselect_type(callback: types.CallbackQuery) -> None:
    tourn_type = callback.data.replace('unselect_type_', '').upper()

    global current_selected_types
    current_selected_types.remove(tourn_type)

    await callback.message.edit_reply_markup(
        reply_markup=get_select_tourn_type_ikb(current_selected_types)
    )


@dp.callback_query_handler(lambda callback: callback.data == 'remember_choice')
async def unselect_type(callback: types.CallbackQuery) -> None:
    global thread_monitoring, thread_active, current_selected_types
    if not current_selected_types:
        await callback.answer('Вы не выбрали ни одного турнира')
        return
    
    db = Database()

    for type_ in current_selected_types:
        games = db.get_data_list(get_prompt_view_games_id(type_))
        if not games:
            await callback.message.answer(f'❌❌У вас нет игр в базе данных {type_}')
            return
    
    thread_monitoring = threading.Thread(target=run_monitoring,
                                         daemon=True,
                                         args=(current_selected_types,))
    thread_active = True
    thread_monitoring.start()

    current_selected_types.clear()
    await callback.message.answer("✅Мониторинг запущен", reply_markup=start_mail_ikb)