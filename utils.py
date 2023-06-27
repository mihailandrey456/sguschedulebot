def parsed_data_to_str(data: dict) -> str:
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