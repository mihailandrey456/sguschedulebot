import asyncio
import json

import parser
from defs import RedisKeys

def parsed_data_to_str(data: dict) -> str:
	res = ""

	for dayofweek in data:
		main_fmt = "{}\n\n{}\n\n\n"
		date = data[dayofweek]["date"]
		head = f"{dayofweek} ({date})"

		body = ""
		for lesson_num in range(1, 8):
			lesson_num = str(lesson_num)
			start_time = data[dayofweek][lesson_num]["start_time"]
			lesson_title = data[dayofweek][lesson_num]["lesson_info"]

			if lesson_title == "":
				continue
			body += f"{lesson_num}-я пара, с {start_time}\n{lesson_title}\n"

		if (body == ""):
			body = "Занятий нет"

		res += main_fmt.format(head, body)

	return res

async def check_cache(group_id: str, redis) -> dict:
	cache = None

	parse_last_update_time_task = asyncio.create_task(
		parser.parse_last_update_time(group_id)
	)
	json_data = await redis.hget(RedisKeys.CACHE_HASH_NAME, group_id)
	if json_data != None:
		data = json.loads(json_data)
		last_update_time_from_redis = data["last_update_time"]
		last_update_time = await parse_last_update_time_task
		if last_update_time_from_redis >= last_update_time:
			cache = data
	else:
		last_update_time = await parse_last_update_time_task

	if cache == None:
		cache = {
			"last_update_time": last_update_time,
			"schedule": None
		}

	return cache

async def update_cache(group_id: str, new_data: dict, redis):
	await redis.hset(
		name=RedisKeys.CACHE_HASH_NAME,
		key=group_id,
		value=json.dumps(new_data)
	)