import threading

import schedule

from aiogram import types
from aiogram.utils.exceptions import ChatNotFound, CantInitiateConversation
from aiogram.dispatcher.filters import Command, Text
from ..bot_config import dp, ADMIN, TOKEN, users_bot, USER_TOKEN
from data_processing import Monitoring, Comparison, send_msg
from ..keyboards import get_select_tourn_type_ikb
from database import (Database,
                      get_prompt_view_username_by_id,
                      get_prompt_view_chat_id_by_nick,
                      get_prompt_view_rating,
                      get_prompt_view_nicknames_by_tourn,
                      get_prompt_view_nicknames_by_tourn_type,
                      get_prompt_view_games_id)



current_selected_types = []
current_selt_send = []
thread_monitoring: threading.Thread
thread_active = False



def monitoring():
    global current_selected_types
    result = None
    if current_selected_types:
        m = Monitoring(*current_selected_types)
        result = m.check_status()
        db = Database()
        
    if result:

        for item in result:     # for every tournament type in completed types

            comparison = Comparison()
            for ws in comparison.wss:           # for every worksheet in the worksheets in the spreadshhet

                tourn_name = ws.title           # tournament name
                if item in tourn_name.upper():

                    users = db.get_data_list(get_prompt_view_nicknames_by_tourn(tourn_name))
                    for user in users:

                        # creating leaderboard
                        nickname = user['nickname']
                        user_chat_id = db.get_data_list(
                            get_prompt_view_chat_id_by_nick(nickname)
                        )[0]['chat_id']

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
                                    f'\n{own_number}. {nickname}: {own_score}'
                        
                        send_msg(msg_text=msg_text, chat_id=user_chat_id, token=USER_TOKEN)

            current_selected_types.remove(item)

        send_msg(
            msg_text=f'Турниры {" ".join(result)} завершены🔚🔚🔚\nРейтинги разосланы юзерам',
            chat_id=ADMIN, token=TOKEN
        )


def run_monitoring() -> None:
    schedule.every(10).seconds.do(monitoring)
    while thread_active:
        schedule.run_pending()
        

# button/command in main menu
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
        current_selected_types.clear()
        await message.answer('✅Мониторинг остановлен')


@dp.callback_query_handler(lambda callback: callback.data.startswith('sendselect_type_'))
async def select_type(callback: types.CallbackQuery) -> None:
    tourn_type = callback.data.replace('sendselect_type_', '').upper()

    global current_selt_send
    current_selt_send.append(tourn_type)

    await callback.message.edit_reply_markup(
        reply_markup=get_select_tourn_type_ikb(
            callback='send', selected_types=current_selt_send
        )
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith('sendunselect_type_'))
async def unselect_type(callback: types.CallbackQuery) -> None:
    tourn_type = callback.data.replace('sendunselect_type_', '').upper()

    global current_selt_send
    current_selt_send.remove(tourn_type)

    await callback.message.edit_reply_markup(
        reply_markup=get_select_tourn_type_ikb(
            callback='send', selected_types=current_selt_send
        )
    )


@dp.callback_query_handler(lambda callback: callback.data == 'sendremember_choice')
async def unselect_type(callback: types.CallbackQuery) -> None:
    global current_selt_send
    if not current_selt_send:
        await callback.answer('Вы не выбрали ни одного турнира')
        return
    
    db = Database()

    chat_ids = []
    for i in current_selt_send:
        users = db.get_data_list(get_prompt_view_nicknames_by_tourn_type(i))
        nicknames = [i['nickname'] for i in users]
        for nick in nicknames:
            chat_id = db.get_data_list(
                get_prompt_view_chat_id_by_nick(nick)
            )[0]['chat_id']
            chat_ids.append(chat_id)

    msg_text='❗️Доступно участие в турнире\nВ разделе "Текущие турниры" выберите свой турнир'
    for chat_id in set(chat_ids):
        try:
            await users_bot.send_message(chat_id=chat_id, text=msg_text)
        except (ChatNotFound, CantInitiateConversation):
            username = db.get_data_list(
                get_prompt_view_username_by_id(str(chat_id))
            )[0]['username']
            await callback.message.answer(
                f'@{username} не создал чат с ботом'
            )

    current_selt_send.clear()
    await callback.message.answer('✅Уведомления отправлены пользователям')
    await callback.message.delete()



@dp.callback_query_handler(lambda callback: callback.data.startswith('select_type_'))
async def select_type(callback: types.CallbackQuery) -> None:
    tourn_type = callback.data.replace('select_type_', '').upper()

    global current_selected_types
    current_selected_types.append(tourn_type)

    await callback.message.edit_reply_markup(
        reply_markup=get_select_tourn_type_ikb(selected_types=current_selected_types)
    )


@dp.callback_query_handler(lambda callback: callback.data.startswith('unselect_type_'))
async def unselect_type(callback: types.CallbackQuery) -> None:
    tourn_type = callback.data.replace('unselect_type_', '').upper()

    global current_selected_types
    current_selected_types.remove(tourn_type)

    await callback.message.edit_reply_markup(
        reply_markup=get_select_tourn_type_ikb(selected_types=current_selected_types)
    )


# inline button starting monitoring with selected types
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
                                         daemon=True)
    thread_active = True
    thread_monitoring.start()

    await callback.message.answer(
        text="✅Мониторинг запущен\nВы можете отправить уведомления юзерам",
        reply_markup=get_select_tourn_type_ikb(callback='send')
    )
    await callback.message.delete()

