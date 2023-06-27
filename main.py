import logging

from aiogram import Bot, Dispatcher, executor, types

import parser
from keyboard import keyboard
from config import API_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def __data_to_str(data: dict) -> str:
	res = ""

	for dayofweek in data:
		main_fmt = "{}\n\n{}\n\n\n"
		date = data[dayofweek]["date"]
		head = f"{dayofweek} ({date})"

		body = ""
		for lesson_num in range(1, 8):
			start_time = data[dayofweek][lesson_num]["start_time"]
			lesson_title = data[dayofweek][lesson_num]["lesson_info"]

			if lesson_title == "":
				continue
			body += f"{lesson_num}-я пара, с {start_time}\n{lesson_title}\n"

		if (body == ""):
			body = "Занятий нет"

		res += main_fmt.format(head, body)

	return res

@dp.message_handler(commands="week")
async def send_sheduled_week(message: types.Message):
	try:
		ok, data = parser.parse()
	except Exception as e:
		await message.answer(e.args[0])
		return

	if ok:
		await message.answer(__data_to_str(data))
	else:
		await message.answer(data["status_text"])

@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
	text = "велком, c помощью меня можешь получать расписание на текущею неделю"
	await message.reply(text, reply_markup=keyboard)

@dp.message_handler()
async def echo(message: types.Message):
	print(message.from_id)
	if message.text == "НЕДЕЛЯ":
		await send_sheduled_week(message)
	else:
		await message.answer("Не панятна")

if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True)