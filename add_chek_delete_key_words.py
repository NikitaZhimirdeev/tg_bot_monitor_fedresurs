from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
import kb_key_words
from sqliter import SQLighter
import os
import re
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class FSMADMIN_ADD(StatesGroup):
    add = State()

class FSMADMIN_DEL(StatesGroup):
    delete = State()

# @dp.message_handler(commands='keyword', state=None)
async def admin(message: types.Message):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    db = SQLighter(os.path.join(dir_path, 'databaseMonitor.db'))

    # Проверка существования таблицы
    all_table = db.all_table()
    ALL_TABLE = []
    for table in all_table:
        ALL_TABLE.append(re.sub("[^A-Za-z_]", "", str(table)))
    # Создание таблицы если ее нет
    if not ('key_word' in ALL_TABLE):
        db.create_table()

    await bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=kb_key_words.button_case_admin)

# @dp.message_handler(commands='Добавить', state=None)
async def cm_start(message: types.Message):
    await FSMADMIN_ADD.add.set()
    await message.reply('введите ключевые слова через запятую\nНапример: Генеральный план, ГП, Сервитут\nДля отмены добавления введите "отмена"')

# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')

# @dp.message_handler(state=FSMADMIN_ADD.add)
async def add(message: types.Message, state: FSMContext):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    db = SQLighter(os.path.join(dir_path, 'databaseMonitor.db'))
    # Проверка и запись ключевых слов
    for key_word in message.text.split(','):
        if (not db.all_key_words_exists(key_word.strip().lower())) and (key_word.strip() != ''):
            # print(key_word.strip())
            db.sql_add_key_word(key_word.strip().lower())

    await state.finish()
    await message.reply('Ключевые слова добавлены')

# @dp.message_handler(commands='Посмотреть')
async def read_key_word(message: types.Message):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    db = SQLighter(os.path.join(dir_path, 'databaseMonitor.db'))
    if len(db.all_key_words()) == 0:
        await message.reply('Нет ключевых слов')
    else:
        all_key_words = db.all_key_words()
        ALL_KEY_WORDS = []
        for key_word in all_key_words:
            ALL_KEY_WORDS.append(re.sub("[^A-Za-zА-Яа-я ]", "", str(key_word)))
        MS = ''
        for word in ALL_KEY_WORDS:
            MS += f'{word}\n'
        if MS.strip() == '':
            await message.reply('Нет ключевых слов')
        else:
            await message.reply(MS)


@dp.message_handler(commands='Удалить', state=None)
async def start_delete_key_word(message: types.Message):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    db = SQLighter(os.path.join(dir_path, 'databaseMonitor.db'))
    if len(db.all_key_words()) == 0:
        await message.reply('Нет ключевых слов')
    else:
        all_key_words = db.all_key_words()
        ALL_KEY_WORDS = []
        for key_word in all_key_words:
            ALL_KEY_WORDS.append(re.sub("[^A-Za-zА-Яа-я ]", "", str(key_word)))
        MS = ''
        for word in ALL_KEY_WORDS:
            MS += f'{word}\n'
        if MS.strip() == '':
            await message.reply('Нет ключевых слов')
        else:
            await FSMADMIN_DEL.delete.set()
            await message.reply(
                f'{MS}\n Напишите ключевые слова которые необходимо удалить через запятую\n'
                f'Например: Долги, Права требования, квартиры'
                f'\nДля отмены удаления введите "отмена"')


@dp.message_handler(state=FSMADMIN_DEL.delete)
async def delete(message: types.Message, state: FSMContext):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    db = SQLighter(os.path.join(dir_path, 'databaseMonitor.db'))
    error = []

    all_key_words = message.text.split(',')
    for key_word in all_key_words:
        if db.all_key_words_exists(key_word.strip().lower()):
            # print(f"{key_word} {db.all_key_words_exists(key_word.strip().lower())}")
            db.sql_delete_key_word(key_word.strip().lower())
        else:
            error.append(key_word.strip().lower())

    all_key_words = db.all_key_words()
    ALL_KEY_WORDS = []
    for key_word in all_key_words:
        ALL_KEY_WORDS.append(re.sub("[^A-Za-zА-Яа-я ]", "", str(key_word)))

    MS = ''
    for word in ALL_KEY_WORDS:
        MS += f'{word}\n'
    await message.answer(f'Текущий список ключевых слов:\n{MS}')

    if len(error) != 0:
        MS_er = ''
        for er in error:
            MS_er += f'{er}\n'
        await message.answer(f'Данные слова не получилось удалить: {MS_er}')
    await state.finish()

def register_handlers_key_words(dp: Dispatcher):
    dp.register_message_handler(admin, commands=['keyword'])
    # dp.register_message_handler(cm_start, commands='Добавить', state=None)
    dp.register_message_handler(cm_start, commands='Добавить', state=None)
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(add, state=FSMADMIN_ADD.add )
    dp.register_message_handler(read_key_word, commands='Посмотреть')