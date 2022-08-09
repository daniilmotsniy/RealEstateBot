from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class ButtonText:
    country_georgia = 'საქართველო🇬🇪'
    country_ukraine = 'Украина🇺🇦'
    lang_georgian = 'ქართული ენა🇬🇪'
    lang_russian = 'Русский язык🇷🇺'
    lang_english = 'English🇬🇧'
    change_cohort = {'en': "Select search options ⚙",
                     'ru': "Выбрать параметры поиска ⚙",
                     'ka': "ძიების პარამეტრების შეცვლა ⚙"}
    change_country = {
        'en': "Change country🇬🇪🇺🇦",
        'ru': "Изменить страну🇬🇪🇺🇦",
        'ka': "შეცვალე ქვეყანა🇬🇪🇺🇦"}
    add_object = {'en': "Add object ✅",
                  'ru': "Добавить объект ✅",
                  'ka': "ობიექტის დამატება ✅"}
    jobs = {'en': "Vacancies 👥", 'ru': "Вакансии 👥",
            'ka': "ვაკანსია 👥"}
    send_to_users = {'en': "Send Newsletter 👥", 'ru': "Отправить рассылку 👥",
                     'ka': "ბიულეტერის გაგზავნა 👥"}


def _start(locale: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[
        KeyboardButton(ButtonText.change_cohort[locale]),
        KeyboardButton(ButtonText.change_country[locale]),
    ], [
        KeyboardButton(ButtonText.add_object[locale]),
        KeyboardButton(ButtonText.jobs[locale]),
    ]], resize_keyboard=True, row_width=2)


def _start_admin(locale: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[
        KeyboardButton(ButtonText.send_to_users[locale]),
        KeyboardButton(ButtonText.change_country[locale]),
    ]], resize_keyboard=True)


class Keyboards:
    country_selection = ReplyKeyboardMarkup([[
            KeyboardButton(ButtonText.country_georgia),
            KeyboardButton(ButtonText.country_ukraine),
        ]], resize_keyboard=True, row_width=2)
    ge_lang_selection = ReplyKeyboardMarkup([[
            KeyboardButton(ButtonText.lang_russian),
            KeyboardButton(ButtonText.lang_english),
        ], [
            KeyboardButton(ButtonText.lang_georgian)
    ]], resize_keyboard=True, row_width=2)
    start = {k: _start(k) for k in ['en', 'ru', 'ka']}
    start_admin = {k: _start_admin(k) for k in ['en', 'ru', 'ka']}
