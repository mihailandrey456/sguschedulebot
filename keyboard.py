from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb = [
	[KeyboardButton("НЕДЕЛЯ")]
]

keyboard = ReplyKeyboardMarkup(
	keyboard=kb,
	resize_keyboard=True
)