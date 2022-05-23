from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class ButtonText:
    change_cohort = "Изменить параметры поиска"
    add_object = "Добавить объект"
    jobs = "Вакансии"


class Keyboards:
    start = ReplyKeyboardMarkup(
        [[
            KeyboardButton(ButtonText.change_cohort)
        ], [
            KeyboardButton(ButtonText.add_object),
            KeyboardButton(ButtonText.jobs),
        ]],
        resize_keyboard=True, row_width=2)
