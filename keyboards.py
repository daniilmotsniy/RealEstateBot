from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class ButtonText:
    country_georgia = 'საქართველო🇬🇪'
    country_ukraine = 'Украина🇺🇦'
    lang_georgian = 'ქართული ენა🇬🇪'
    lang_russian = 'Русский язык🇷🇺'
    change_cohort = "Изменить параметры поиска"
    change_country = "Изменить страну🇬🇪🇺🇦"
    add_object = "Добавить объект"
    jobs = "Вакансии"


class Keyboards:
    country_selection = ReplyKeyboardMarkup([[
            KeyboardButton(ButtonText.country_georgia),
            KeyboardButton(ButtonText.country_ukraine),
        ]], resize_keyboard=True, row_width=2)
    ge_lang_selection = ReplyKeyboardMarkup([[
            KeyboardButton(ButtonText.lang_georgian),
            KeyboardButton(ButtonText.lang_russian),
        ]], resize_keyboard=True, row_width=2)
    start = ReplyKeyboardMarkup([[
            KeyboardButton(ButtonText.change_cohort),
            KeyboardButton(ButtonText.change_country),
        ], [
            KeyboardButton(ButtonText.add_object),
            KeyboardButton(ButtonText.jobs),
        ]], resize_keyboard=True, row_width=2)
