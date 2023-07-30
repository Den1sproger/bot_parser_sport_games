from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from ..bot_config import dp, ADMIN
from ..keyboards import get_tourn_type_ikb, confirm_finish_ikb



@dp.message_handler(Text(equals='📋Заполнить таблицу'), user_id=ADMIN)
@dp.message_handler(Command('fill_table'), user_id=ADMIN)
async def fill_table(message: types.Message) -> None:
    await message.answer(
        'Выберите тип турнира',
        reply_markup=get_tourn_type_ikb(action='fill')
    )


@dp.message_handler(Text(equals='🧹Очистить таблицу'), user_id=ADMIN)
@dp.message_handler(Command('clear_table'), user_id=ADMIN)
async def clear_table(message: types.Message) -> None:
    await message.answer(
        'Выберите тип турнира',
        reply_markup=get_tourn_type_ikb(action='clear')
    )


@dp.message_handler(Text(equals='🏀🏐Утвердить матчи'), user_id=ADMIN)
@dp.message_handler(Command('approve_games'), user_id=ADMIN)
async def approve_games(message: types.Message) -> None:
    await message.answer(
        'Выберите тип турнира',
        reply_markup=get_tourn_type_ikb(action='approve')
    )
    

@dp.message_handler(Text(equals='🏁Закончить турнир'), user_id=ADMIN)
@dp.message_handler(Command('finish'), user_id=ADMIN)
async def finish(message: types.Message) -> None:
    await message.answer(
        text='Вы точно хотите завершить турниры?\nДанное действие очистит базы этих турниров',
        reply_markup=confirm_finish_ikb
    )


@dp.message_handler(Text(equals='📝Добавить текущий рейтинг'), user_id=ADMIN)
@dp.message_handler(Command('add_rating'), user_id=ADMIN)
async def fill_rating(message: types.Message) -> None:
    await message.answer(
        text='Выберите тип турнира',
        reply_markup=get_tourn_type_ikb(action='add')
    )