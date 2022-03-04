from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


#Кнопки клавиатуры админа
button_load = KeyboardButton('/Добавить')
button_read = KeyboardButton('/Посмотреть')
button_delete = KeyboardButton('/Удалить')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_load).add(button_read).add(button_delete)
