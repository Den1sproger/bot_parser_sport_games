import logging

from aiogram import types
from aiogram.utils.exceptions import ChatNotFound, CantInitiateConversation
from data_processing import Rating, Games, Collection, Comparison
from ..bot_config import dp, users_bot
from ..keyboards import (finish_mail_ikb,
                         get_tourn_type_ikb,
                         get_ikb_gs_url)
from googlesheets import GAMES_SPREADSHEET_URL, RATING_SPREADSHEET_URL
from database import (Database,
                      PROMPT_VIEW_USERS,
                      get_prompt_delete_answers,
                      get_prompt_delete_rating,
                      get_prompt_delete_games,
                      get_prompt_view_username_by_id,
                      get_prompt_delete_games,
                      get_prompt_delete_rating,
                      get_prompt_register_participant,
                      get_prompt_delete_users_tournaments)



async def send_notification(callback: types.CallbackQuery,
                            msg_text: str) -> None:
    db = Database()
    users = db.get_data_list(PROMPT_VIEW_USERS)
    chat_ids = [int(i['chat_id']) for i in users]

    for chat_id in chat_ids:
        try:
            await users_bot.send_message(chat_id=chat_id, text=msg_text)
        except (ChatNotFound, CantInitiateConversation):
            username = db.get_data_list(
                get_prompt_view_username_by_id(str(chat_id))
            )[0]['username']
            await callback.message.answer(
                f'@{username} не создал чат с ботом'
            )

    await callback.answer('✅Уведомления отправлены пользователям')
    await callback.message.answer('✅Уведомления отправлены пользователям')


@dp.callback_query_handler(lambda callback: callback.data == 'send_start_notification')
async def send_start_notification(callback: types.CallbackQuery) -> None:
    await send_notification(
        callback, 
        msg_text='❗️❗️❗️Доступно голосование в некоторых турнирах'
    )


@dp.callback_query_handler(lambda callback: callback.data == 'confirm_finish')
async def confirm_finish(callback: types.CallbackQuery) -> None:
    await callback.message.answer(
        text='Выберите тип турнира',
        reply_markup=get_tourn_type_ikb(action='finish')
    )


@dp.callback_query_handler(lambda callback: callback.data == 'not_confirm')
async def delete_confirm_msg(callback: types.CallbackQuery) -> None:
    await callback.message.delete()


@dp.callback_query_handler(lambda callback: callback.data.endswith('_type_finish'))
async def select_type_finish(callback: types.CallbackQuery) -> None:
    try:
        tourn_type = callback.data.replace('_type_finish', '').upper()
        db = Database()
        db.action(
            get_prompt_delete_rating(tourn_type),
            get_prompt_delete_answers(tourn_type),
            get_prompt_delete_users_tournaments(tourn_type),
            get_prompt_delete_games(tourn_type)
        )
        gs = Games(tourn_type=tourn_type)
        gs.clear_table()
    except Exception as _ex:
        logging.error(_ex)
        await callback.answer("❌❌Ошибка❌❌")
        await callback.message.answer("❌❌Ошибка❌❌")
    else:
        await callback.message.answer(f'✅Турниры {tourn_type} завершены')


@dp.callback_query_handler(lambda callback: callback.data.endswith('_type_fill'))
async def select_type_fill(callback: types.CallbackQuery) -> None:
    try:
        # parsing sport games and recorde to json
        tourn_type = callback.data.replace('_type_fill', '').upper()

        parser = Collection(get_full_data=True, tourn_type=tourn_type)
        admin_data = parser.log_in()
        parser.get_games(id=admin_data['id'], hash=admin_data['hash'])
        parser.get_begin_time()
        parser.get_game_url()
        parser.get_team_coeffs()
        parser.recorde_to_json()
        parser.session.close()

        # writing data to the googlesheet
        gs = Games(games_data=parser.full_data, tourn_type=tourn_type)
        gs.write_data()
    except Exception as _ex:
        logging.error(_ex)
        await callback.answer("❌❌Ошибка❌❌")
        await callback.message.answer("❌❌Ошибка❌❌")
    else:
        await callback.message.answer(
            text="Таблица заполнена✅",
            reply_markup=get_ikb_gs_url(
                button_text=gs.SHEET_NAME,
                url=GAMES_SPREADSHEET_URL
            )
        )


@dp.callback_query_handler(lambda callback: callback.data.endswith('_type_clear'))
async def select_type_clear(callback: types.CallbackQuery) -> None:
    try:
        tourn_type = callback.data.replace('_type_clear', '').upper()
        gs = Games(tourn_type=tourn_type)
        gs.clear_table()
        db = Database()
        db.action(get_prompt_delete_games(tourn_type))
    except FileNotFoundError:
        pass
    except Exception as _ex:
        logging.error(_ex)
        await callback.answer("❌❌Ошибка❌❌")
        await callback.message.answer("❌❌Ошибка❌❌")
        return
    
    await callback.message.answer(
        text="Таблица очищена✅",
        reply_markup=get_ikb_gs_url(
            button_text=gs.SHEET_NAME,
            url=GAMES_SPREADSHEET_URL
        )
    )


@dp.callback_query_handler(lambda callback: callback.data.endswith('_type_add'))
async def add_rating(callback: types.CallbackQuery) -> None:
    tourn_type = callback.data.replace('_type_add', '').upper()

    # get the tournament's users of the tournament type
    comparsion = Comparison()
    users_tournaments = comparsion.get_tournaments(tourn_type)
    
    # write data to the table with name "current rating"
    rating = Rating(tourn_type)
    rating.add_rating(users_tournaments)

    # write data to the database to the table with name "participants"
    db = Database()
    queries = [get_prompt_delete_rating(tourn_type)]
    for item in users_tournaments:
        queries.append(
            get_prompt_register_participant(
                nickname=item[0],
                tournament=item[-1]
            )
        )
    db.action(*queries)

    await callback.answer('✅Текущий рейтинг создан')
    await callback.message.answer(
        text='✅Текущий рейтинг создан',
        reply_markup=get_ikb_gs_url(
            button_text=Rating.SHEET_NAME,
            url=RATING_SPREADSHEET_URL
        )
    )


@dp.callback_query_handler(lambda callback: callback.data.endswith('_type_approve'))
async def add_rating(callback: types.CallbackQuery) -> None:
    try:
        tourn_type = callback.data.replace('_type_approve', '').upper()
        gs = Games(tourn_type)
        gs.approve_tournament_games()
        parser = Collection(tourn_type)
        parser.write_to_database()
    except Exception as _ex:
        logging.error(_ex)
        await callback.answer("❌❌Ошибка❌❌")
        await callback.message.answer("❌❌Ошибка❌❌")
    else:
        await callback.message.answer(
            "Данные утверждены✅\nДля корректной работы ничего не меняйте в таблице"
        )