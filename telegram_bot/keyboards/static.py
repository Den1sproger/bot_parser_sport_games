from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton('📋Заполнить таблицу'), KeyboardButton('🧹Очистить таблицу')],
        [KeyboardButton('🏀🏐Утвердить матчи'), KeyboardButton('🚀🚀Запустить мониторинг')],
        [KeyboardButton('❌Закончить мониторинг'), KeyboardButton('🏁Закончить турнир')],
        [KeyboardButton('🆘Помощь'), KeyboardButton('📝Добавить текущий рейтинг')]
    ]
)