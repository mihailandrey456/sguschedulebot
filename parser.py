import requests
from bs4 import BeautifulSoup

from defs import CellType

def parse(group_id: str) -> (bool, dict):
	""" Парсит сайт кампуса СГУ им. Питирима Сорокина в целях получения расписания.
	Вызывается исключение, если верстка сайта поменялась, так как логика парсера жестко связана с размещением html-элементов.

	Возвращаемые значения: (bool, dict)
	1-ое значение -- прошел ли парсинг успешно
	2-ое значение -- данные ответа

	Структура 2-го значения (пример):
	{
		"Понедельник": {
			"date": "26.06.2023",
			1: {
				"start_time": "08:30",
				"lesson_info": "Уравнения математической физики (экз.) Сушков В.В., 431/1"
			},
			2: {
				"start_time": "10:10",
				"lesson_info": ""
			},
			...
			7: { ... }
		}, 
		...
		"Суббота": { ... }
	}
	"""
	url = "https://campus.syktsu.ru/schedule/group/"
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}
	data = {
		"num_group": group_id,
		"searchdata": ""
	}

	page = requests.post(url, data=data, headers=headers)
	page.encoding = "utf-8"

	ret = None
	match page.status_code / 100:
		case [1, 3]:
			ret = (False, {"status_text": "Упс! Неопознанная ошибка"})
		case 4:
			ret = (False, {"status_text": "Упс! Ошибка на Вашей стороне"})
		case 5:
			ret = (False, {"status_text": "Упс! Ошибка на стороне сервера"})

	if ret != None:
		return ret

	exception_text = "Упс! Парсер сломался или неверно указана учебная группа"

	soup = BeautifulSoup(page.text, "lxml")
	schedule_table = soup.find("table", class_="schedule")
	try:
		tbody = schedule_table.find("tbody")
		cells = tbody.find_all("td")
	except Exception:
		raise Exception(exception_text)

	cell_type = CellType.DAYOFWEEK # int, 0
	response = {}
	current_dayofweek, current_lesson_num = ("", 0)
	for cell in cells:
		if cell.has_attr("class") \
			and len(cell["class"]) > 0 \
			and cell["class"][0] == "dayofweek":

			tmp = cell.text
			dayofweek = tmp[ : tmp.find("(")]
			date = tmp[tmp.find("(")+1 : len(tmp)-1]
			if response.get(dayofweek) != None:
				raise Exception(exception_text)

			response[dayofweek] = {"date": date}

			current_dayofweek = dayofweek
			cell_type = CellType.LESSONNUM
			continue

		match cell_type % CellType.MAX:
			case CellType.LESSONNUM:
				if response.get(current_dayofweek) == None:
					raise Exception(exception_text)

				lesson_num = int(cell.text)
				response[current_dayofweek][lesson_num] = {}
				current_lesson_num = lesson_num
			case CellType.STARTIME:
				if response.get(current_dayofweek) == None \
					and response[current_dayofweek].get(current_lesson_num) == None:

					raise Exception(exception_text)

				start_time = cell.text
				response[current_dayofweek][current_lesson_num]["start_time"] = start_time
			case CellType.LESSONINFO:
				if response.get(current_dayofweek) == None \
					and response[current_dayofweek].get(current_lesson_num) == None:

					raise Exception(exception_text)

				lesson_info = cell.text
				lesson_info = lesson_info.replace("\n", " ")
				lesson_info = lesson_info.replace("\t", "")
				response[current_dayofweek][current_lesson_num]["lesson_info"] = lesson_info
				
				cell_type = CellType.DAYOFWEEK
			case _:
				raise Exception(exception_text)

		cell_type += 1

	return (True, response)