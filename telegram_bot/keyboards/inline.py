from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import TOURNAMENT_TYPES


def get_ikb_gs_url(button_text: str, url: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(button_text, url=url)]
        ]
    )
    return ikb


def get_tourn_type_ikb(action: str) -> InlineKeyboardMarkup:
    actions = ['fill', 'clear', 'add', 'approve', 'finish']
    assert action in actions, 'Unknown action for games sheets'
    
    inline_keyboard = []
    for type_ in TOURNAMENT_TYPES:
        inline_keyboard.append(
            [InlineKeyboardButton(type_, callback_data=f'{type_.lower()}_type_{action}')]
        )

    ikb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return ikb


def get_select_tourn_type_ikb(callback: str = '',
                              selected_types: list[str] = []) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for type_ in TOURNAMENT_TYPES:
        text: str
        callback_data: str
        if type_ in selected_types:
            text = f'➡️{type_}⬅️'
            callback_data=f'{callback}unselect_type_{type_.lower()}'
        else:
            text = type_
            callback_data=f'{callback}select_type_{type_.lower()}'
        inline_keyboard.append(
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
        )
    
    # start monitoring button with selected tournament types
    inline_keyboard.append(
        [
            InlineKeyboardButton(
                text='Запомнить выбор и начать',
                callback_data=f'{callback}remember_choice'
            )
        ]
    )
    ikb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return ikb



confirm_finish_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('Подтвердить завершение', callback_data='confirm_finish')],
        [InlineKeyboardButton('Не завершать', callback_data='not_confirm')]
    ]
)


confirm_reset_rating = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton('Подтвердить обнуление', callback_data='confirm_reset')],
        [InlineKeyboardButton('Не обнулять', callback_data='not_confirm_reset')]
    ]
)