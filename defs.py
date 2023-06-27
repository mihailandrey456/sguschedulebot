from enum import IntEnum, Enum
from aiogram.utils.helper import Helper, HelperMode, Item

class CellType(IntEnum):
    DAYOFWEEK = 0,
    LESSONNUM = 1,
    STARTIME = 2,
    LESSONINFO = 3,
    MAX = 4

class States(Helper):
    mode = HelperMode.snake_case

    HAS_GROUP_STATE = Item()



_start_text = "велком, c помощью меня можешь получать расписание" \
            " на текущею неделю. Для начала укажи свою группу (/help)" \

_help_text = "/setgroup group_id - выбрать учебную группу\n" \
            "/setgroup - сбросить установленную группу\n" \
            "/week - получить расписание на текущею неделю"

_set_group_success_text = "Учебная группа установлена"
_set_group_invalid_text1 = "Надо указать группу!!"

_unset_group_text = "Учебная группа сброшена"

Messages = {
    "start": _start_text,
    "help": _help_text,
    "set_group_success": _set_group_success_text,
    "set_group_invalid1": _set_group_invalid_text1,
    "unset_group":_unset_group_text
}


class RedisKeys(str, Enum):
    GROUP_ID = "group_id"