import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from redis.asyncio import Redis

import parser
import utils
from keyboard import keyboard
from _config import API_TOKEN
from _config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
from defs import States, Messages, RedisKeys

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

redis_instance = Redis(
	host=REDIS_HOST,
	port=REDIS_PORT,
	db=REDIS_DB,
	password=REDIS_PASSWORD,
	decode_responses=True
)

storage = RedisStorage2(
	host=REDIS_HOST,
	port=REDIS_PORT,
	db=REDIS_DB,
	password=REDIS_PASSWORD
)
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(state=States.all() + [None], commands=["start"])
async def send_welcome(message: types.Message):
	await message.reply(Messages["start"], reply_markup=keyboard)

@dp.message_handler(state=States.all() + [None], commands=["help"])
async def send_help(message: types.Message):
	await message.reply(Messages["help"], reply_markup=keyboard)

@dp.message_handler(state="*", commands=["setgroup"])
async def process_setgroup_command(message: types.Message):
	group_id = message.get_args().lower()
	state = dp.current_state(user=message.from_id)

	if not group_id:
		state_data = await state.get_data()
		await state.reset_state()

		if state_data.get(RedisKeys.GROUP_ID) == None:
			await message.reply(Messages["set_group_invalid1"])
		else:
			await message.reply(Messages["unset_group"])
		
		return

	# Проверить, что такая учебная группа существует
	if False:
		return

	data = { RedisKeys.GROUP_ID: group_id }
	await state.update_data(**data)
	await state.set_state(States.HAS_GROUP_STATE)
	await message.reply(Messages["set_group_success"])

@dp.message_handler(commands="week", state=States.HAS_GROUP_STATE)
async def send_sheduled_week(message: types.Message):
	state = dp.current_state(user=message.from_id)

	try:
		state_data = await state.get_data()
		group_id = state_data[RedisKeys.GROUP_ID]
		ok, data = await parser.parse_schedule(group_id, redis_instance)
	except Exception as e:
		await message.answer(e.args)
		# await message.answer(Messages["exception"])
		return

	if ok:
		await message.answer(utils.parsed_data_to_str(data))
	else:
		await message.answer(data["status_text"])


@dp.message_handler(state=States.HAS_GROUP_STATE)
async def echo1(message: types.Message):
	if message.text == "НЕДЕЛЯ":
		await send_sheduled_week(message)
	else:
		await message.answer(message.text)

@dp.message_handler()
async def echo2(message: types.Message):
	await message.answer(message.text)

async def shutdown(dispatcher: Dispatcher):
	await dispatcher.storage.close()

if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=False, on_shutdown=shutdown)