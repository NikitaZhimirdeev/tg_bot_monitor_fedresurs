from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
import requests
from bs4 import BeautifulSoup as BS4
from create_bot import dp, bot, dp_fol, bot_fol, dir_path
import config
from parser_web import PARSER
from sqliter import SQLighter
import os
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

db = SQLighter(os.path.join(dir_path, 'databaseMonitor.db'))
parser = PARSER()

class SEARCH_INN(StatesGroup):
    typeofsearch = State()
    INN = State()
    follow = State()

class DELETE_INN(StatesGroup):
    delete = State()
    find_name = State()
    follow = State()

# @dp.message_handler(commands='search')
async def cm_start(message: types.Message):
    await SEARCH_INN.typeofsearch.set()
    # await message.reply('хотите отслеживать юрлицо или физлицо 1 или 2:\nДля отмены добавления введите "отмена"')
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Выбирите за кем вам необходимо следить\nЕсли не уверены, то проверьте на сайте old.bankrot.fedresurs.ru\n"
                                f"Если вы нажали случайно или предумали следить введите 'отмена'",
                           # reply_markup=InlineKeyboardMarkup().add(
                           #     InlineKeyboardButton(f'Удалить',
                           #                          callback_data=f'del {ret[1]}')))
                           reply_markup=InlineKeyboardMarkup().add(
                               InlineKeyboardButton(f"ЮРЛИЦО", callback_data=f"face 1")).add(
                               InlineKeyboardButton(f"ФИЗЛИЦО", callback_data=f"face 2")
                           ))

# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    # if message.from_user.id == ID:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')

# @dp.message_handler(state=SEARCH_INN.typeofsearch)
# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('fol '))
@dp.callback_query_handler(lambda x: x.data and x.data.startswith('face '))
async def typeofsearch(callback_query: types.CallbackQuery, state: FSMContext):
    # print(callback_query.data.replace('face ', '')
    async with state.proxy() as data:
        data['type_search'] = callback_query.data.replace('face ', '')
    # type_search = message.text.strip()
    await SEARCH_INN.next()
    await bot.send_message(callback_query.from_user.id, 'Введите ИНН должника')
    # await message.reply('введите инн')

# @dp.message_handler(state=SEARCH_INN.typeofsearch)
async def INN(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['INN'] = message.text.strip()
        org = tuple(data.values())[0]
    # type_search = message.text.strip()
    # print('1')
    name = await search_inn(state)
    # print(name)
    # href = name[0]['href_defaulter'].split('=')[-1] + f'@{org}'
    # print(href.split('=')[-1])
    if name != 'Пороизошла ошибка, проверьте ИНН на сайте, либо проверьте bankrotcookie' and name[0]['name'] != '':
        href = name[0]['href_defaulter'].split('=')[-1] + f'@{org}'
        await bot.send_message(message.from_user.id, text=f"{name[0]['name']} - Есди это тот кто вам нужен, то нажмите 'Следить'\n"
                                                          f"иначе введите 'отмена', уточните ИНН и повторите попытку",
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton(f"Следить", callback_data=f"follow {href}"))
                               )
        await SEARCH_INN.next()
    else:
        await bot.send_message(message.from_user.id, text='Пороизошла ошибка, проверьте ИНН на сайте, либо проверьте bankrotcookie')
        await state.finish()
    # print('2')
    # await SEARCH_INN.next()
    # await state.finish()

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('follow '))
async def follow(callback_query: types.CallbackQuery, state: FSMContext):
    data = []

    bankrotcookie = parser.bankrotcookie()
    #print(bankrotcookie)

    id_defaulter = callback_query.data
    # print(id_defaulter.split(' ')[1])
    # print(id_defaulter.split(' ')[1].split('@')[0])

    if id_defaulter.split(' ')[1].split('@')[1] == '1':
        href = 'https://old.bankrot.fedresurs.ru/OrganizationCard.aspx?ID='
    else:
        href = 'https://old.bankrot.fedresurs.ru/PrivatePersonCard.aspx?ID='

    url_defailter = f"{href}{id_defaulter.split(' ')[1].split('@')[0]}"

    soup = PARSER().get_html(url_defailter, config.HEADERS_def(bankrotcookie))
    data_defaulter = PARSER().parser_table_defaulter(soup, url_defailter)

    data.append({
        'id_defaulter': id_defaulter.split(' ')[1].split('@')[0],
        'defaulter_url': url_defailter,
        'name': data_defaulter[0]['name'],
        'all_message': data_defaulter[0]['all_message']
    })
    try:
        # print(data)
        await db.sql_add_defaulter(data)
        await callback_query.answer(text=f'Вы начали следить за "{data_defaulter[0]["name"]}"', show_alert=True)
        await state.finish()
    except:
        await callback_query.answer(f'Вы уже отслеживаете "{data_defaulter[0]["name"]}"', show_alert=True)
        await state.finish()

async def search_inn(state):
    name = ''
    href_defaulter = ''

    bankrotcookie = parser.bankrotcookie()
    #print(bankrotcookie)

    async with state.proxy() as data:
        # print(tuple(data.values())[0])
        if tuple(data.values())[0] == '1':
            HEADERS = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Cookie': f'debtorsearch=typeofsearch=Organizations&orginn={tuple(data.values())[1]}; bankrotcookie={bankrotcookie}'
                }
        elif tuple(data.values())[0] == '2':
            HEADERS = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Cookie': f'debtorsearch=typeofsearch=Persons&prsinn={tuple(data.values())[1]}; bankrotcookie={bankrotcookie}'
                }

    try:
        r = requests.get('https://old.bankrot.fedresurs.ru/DebtorsSearch.aspx', headers=HEADERS)
        soup = BS4(r.text, 'lxml')

        table = soup.find('table', class_='bank').find_all('tr')
        del table[0]  # , table[-2], table[-1]
        dat = []
        for tr in table:
            tds = tr.find_all('td')
            name = tds[1].text.strip()
            href_defaulter = f"https://old.bankrot.fedresurs.ru{tds[1].find('a').get('href')}"
        dat.append({
            'name': name,
            'href_defaulter': href_defaulter
        })
        return dat
    except:
        return 'Пороизошла ошибка, проверьте ИНН на сайте, либо проверьте bankrotcookie'


@dp_fol.message_handler(commands='delete', state=None)
async def cm_start_delete(message: types.Message):
    await DELETE_INN.delete.set()
    # await message.reply('хотите отслеживать юрлицо или физлицо 1 или 2:\nДля отмены добавления введите "отмена"')
    await bot_fol.send_message(chat_id=message.from_user.id,
                               text=f"Если хотите перестать отслеживать должника, то введите сслку на его профиль\n"
                                    f"Пример ссылки - 'https://old.bankrot.fedresurs.ru/PrivatePersonCard.aspx?ID=66CBC55AC008F15B79847C8B2361A9DC'\n"
                                    f"Если вы нажали случайно или предумали удалять введите 'отмена'")

@dp_fol.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler_fol(message: types.Message, state: FSMContext):
    # if message.from_user.id == ID:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')

@dp_fol.message_handler(state=DELETE_INN.delete)
async def find_name(message: types.Message, state: FSMContext):

    url_defaulter = message.text
    if '&attempt=1' in url_defaulter:
        url_defaulter = url_defaulter.replace('&attempt=1', '')

    await db.sql_delete_command_only(url_defaulter)
    await bot_fol.send_message(chat_id=message.from_user.id,
                               text='Вы перестали отслеживать должника')


    # await bot_fol.send_message(chat_id=message.from_user.id, text=f'{message.text}')
    # await message.reply('хотите отслеживать юрлицо или физлицо 1 или 2:\nДля отмены добавления введите "отмена"')
    # await bot_fol.send_message(chat_id=message.from_user.id,
    #                            text=f"хотите удалить, введите ссылку на страницу")
    # await state.next()
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands='search', state=None)
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_callback_query_handler(typeofsearch, state=SEARCH_INN.typeofsearch)
    dp.register_callback_query_handler(follow, state=SEARCH_INN.follow)
    # dp.register_message_handler(typeofsearch, state=SEARCH_INN.typeofsearch)
    dp.register_message_handler(INN, state=SEARCH_INN.INN)

def register_handlers_admin_2(dp: Dispatcher):
    dp.register_message_handler(cm_start_delete, commands='delete', state=None)
    dp.register_message_handler(cancel_handler_fol, Text(equals='отмена', ignore_case=True), state="*")
    # dp.register_callback_query_handler(typeofsearch, state=SEARCH_INN.typeofsearch)
    # dp.register_callback_query_handler(follow, state=SEARCH_INN.follow)
    # dp.register_message_handler(typeofsearch, state=SEARCH_INN.typeofsearch)
    dp.register_message_handler(find_name, state=SEARCH_INN.INN)

