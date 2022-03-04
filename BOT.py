import asyncio
import time
from create_bot import dp, bot, dp_fol, bot_fol,dir_path
from aiogram import executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from parser_web import PARSER
from sqliter import SQLighter
from multiprocessing import Process
import os
import config

parser = PARSER()

# Инициализирууем соединение с БД
db = SQLighter(os.path.join(dir_path, 'databaseMonitor.db'))

if 'users.txt' not in os.listdir(dir_path):
        with open(os.path.join(dir_path, 'users.txt'), 'a') as f:
            pass

# Идексация того, что бот начал работу
async def on_startup(_):
    print('Бот вышел в сеть')

# Команда запуска бота
@dp.message_handler(commands=['start'])
async def START(message: types.Message):
    # Сбор всех id пользователей, которые активировали бота
    with open(os.path.join(dir_path, 'users.txt'), 'r') as f:
        users = ''.join(f.readlines()).strip().split('\n')
    # Проверка, если пользователя нет в списке активировавших, то записываем его туда
    if not (str(message.from_user.id) in users):
        with open(os.path.join(dir_path, 'users.txt'), 'a') as f:
            f.write(f'{message.from_user.id}\n')
    await message.answer('Здравствуйте!\n Данный бот производит мониторинг всех сообщений сайта old.bankrot.fedresurs.ru\n'
                         'Если на сайте появятся новые сообщения,то оно придет сюда\nПод каждым сообщением имеется кнопка "Следить", нажав ее, вы начнете отслежиивать все сообщения должника\n'
                         '@fed_alarmbot - Бот,в которого будут приходить сообщения по отслеживаемым должникам'
                         'Так же имеется возможность поиска должника по ИНН,для этого введите команду /search\n'
                         'Если забудете команды введите /help или перезапустите бота')

@dp.message_handler(commands=['help'])
async def HELP(message: types.Message):
    await message.answer("/search - Команда поиска по ИНН\n"
                         "Чтобы начать следить нажмите кнопку 'Следить' под интересующим вас должником\n\n"
                         "/keyword - Команда для добавления, просмотра и удаления ключевых слов"
                         "@fed_alarmbot - Бот,в которого будут приходить сообщения по отслеживаемым должникам")


# @dp.message_handler()
async def PARSER_WHILE():
    ind = 1
    while True:
        #print('начался монитор')

        bankrotcookie = parser.bankrotcookie()
        #print(bankrotcookie)

        try:
            # await parser.selenium_cookie()
            # time.sleep(3)

            with open(os.path.join(dir_path, 'users.txt'), 'r') as f:
                users = ''.join(f.readlines()).strip().split('\n')

            data = []
            for setin in config.COOKIE[0:3]:
                for reg, mes in setin.items():
                    # print(config.HEAD(mes, reg))

                    soup = parser.get_html(config.URL, config.HEAD(mes, reg, bankrotcookie))
                    # print(config.URL)
                    # print(config.HEAD(mes, reg))
                    # print(soup)
                    data.append(parser.parse_table_all(soup))
                # print()

            for i in data:
                for a in i:
                    if (not db.allpost_exists(a['url_message'])) and ('аннулировано' not in a['type_message']) and (not db.sql_read_defaulter_url_exists(a['url_defaulter'])):
                        # print(a['url_defaulter'])
                        db.add_message(a)
                        # print(a)
                        # print(a['url_message'])
                        soup_LOT = parser.get_html(a['url_message'], config.HEADERS_def(bankrotcookie))
                        LOT = parser.parser_lot(soup_LOT)
                        # if LOT == 'Объявление о проведении торгов (аннулировано, заблокировано)':
                        #     MS_LOT = 'Объявление о проведении торгов (аннулировано, заблокировано)'
                        # elif LOT == 'Отчет оценщика об оценке имущества должника (аннулировано, заблокировано)':
                        #     MS_LOT = 'Отчет оценщика об оценке имущества должника (аннулировано, заблокировано)'
                        # else:
                        MS_LOT = parser.create_MS_LOT(LOT)
                        # print(MS_LOT)

                        ALL_KEY_WORDS = parser.list_key_words()
                        ind_stop_key = 0
                        for key_word in ALL_KEY_WORDS:
                            if key_word in MS_LOT.lower():
                                ind_stop_key += 1

                        if ind_stop_key == 0:
                            for user in users:
                                try:
                                    # print(f"aaaaaa {a['url_defaulter']}")
                                    id = a['url_defaulter'].split('/')[-1]

                                    await bot.send_message(chat_id=user,
                                                           text=f"{a['date']}\n\n"
                                                                f"Тип сообщения - {a['type_message']}\n"
                                                                f"Ссылка на сообщение - {a['url_message']}\n"
                                                                f"Должник - {a['defaulter']}\n"
                                                                f"Ссылка на должника - {a['url_defaulter']}\n"
                                                                f"Адрес - {a['address']}\n"
                                                                f"Кем опубликовано - {a['published']}\n\n"
                                                                f"{MS_LOT}",
                                                           parse_mode='html',
                                                                # f"{MS_KAD_NUM}",
                                                           # reply_markup=InlineKeyboardMarkup().add(
                                                           #     InlineKeyboardButton(f'Удалить',
                                                           #                          callback_data=f'del {ret[1]}')))
                                                           reply_markup=InlineKeyboardMarkup().add(
                                                               InlineKeyboardButton(f"^^^ Следить ^^^",
                                                                                    callback_data=f"fol {id}"))) # {a['defaulter']}
                                except:
                                    pass

            # print('sleep')
            await asyncio.sleep(600)

        except:
            print('ERROR')
            if ind%2 == 0:
                parser.selenium_cookie()
            # for user in users:
            #     try:
            #         await bot.send_message(user, 'ERROR')
            #     except:
            #         pass
            ind += 1
            await asyncio.sleep(45)
        #print('закончился монитор')

@dp_fol.message_handler(commands=['start'])
async def START_fol(message: types.Message):
    # Сбор всех id пользователей, которые активировали бота
    with open(os.path.join(dir_path, 'users.txt'), 'r') as f:
        users = ''.join(f.readlines()).strip().split('\n')
    # Проверка, если пользователя нет в списке активировавших, то записываем его туда
    if not (str(message.from_user.id) in users):
        with open(os.path.join(dir_path, 'users.txt'), 'a') as f:
            f.write(f'{message.from_user.id}\n')
    await message.answer('Здравствуйте!\n Данный бот производит мониторинг всех сообщений должников за которымивы следите\n'
                         'Если у долника появятся новые сообщения,то они придут сюда\n'
                         'Под каждым сообщением имеется кнопка "Удалить <имя должника>", нажав ее, перестаните следить за должником\n'
                         '@fed_monitorbot - Бот,в которого приходят всеновые сообщения и где вы сможете выбрать за кем следить'
                         'Так же имеется возможность удалить должника по ссылке на его профиль на сайте, для этого введите команду /delete\n'
                         'Команда для просмотра всех должников /debtors, при помощи данной команды вы можете просмотреть всех отслеживаемых'
                         'должников и просмотреть лоты каждого\n'
                         'Если забудете команды введите /help или перезапустите бота')

@dp_fol.message_handler(commands=['help'])
async def HELP_fol(message: types.Message):
    await message.answer("/delete - удалить должника по ссылке на его профиль на сайте\n"
                         "/debtors - Команда для просмотра всех должников, при помощи данной команды вы можете просмотреть всех отслеживаемых должников и просмотреть лоты каждого\n"
                         "@fed_monitorbot - Бот,в которого приходят всеновые сообщения и где вы сможете выбрать за кем следить")

async def MONITOR_WHILE():
    indx = 1
    while True:
        #print('Идет проверка follow')

        bankrotcookie = parser.bankrotcookie()
        #print(bankrotcookie)

        try:
            # await parser.selenium_cookie()
            # time.sleep(3)

            with open(os.path.join(dir_path, 'users.txt'), 'r') as f:
                users = ''.join(f.readlines()).strip().split('\n')

            defaulters_urls = db.sql_read_defaulter_url()
            for defaulter_url in defaulters_urls:
                new = ''
                id_defaulter = defaulter_url[0].split('=')[1]
                soup = parser.get_html(defaulter_url[0], config.HEADERS_def(bankrotcookie))
                data_defaulter = parser.parser_table_defaulter(soup, defaulter_url[0])

                name = data_defaulter[0]['name']
                all_message_new = data_defaulter[0]['all_message'].split(';')
                del all_message_new[-1]

                all_message_old = db.sql_read_all_message_defaulter(name)[0][0]
                all_message_old_split = all_message_old.split(';')
                del all_message_old_split[-1]
                for message_new in all_message_new:
                    if message_new in all_message_old_split:
                        # print('yes')
                        pass
                    else:
                        new += f'{message_new};'

                        soup_LOT = parser.get_html(message_new, config.HEADERS_def(bankrotcookie))
                        LOT = parser.parser_lot(soup_LOT)
                        # print(LOT)
                        if LOT == 'Аннулировано':
                            MS_LOT = 'Аннулировано'
                        else:
                            MS_LOT = parser.create_MS_LOT(LOT)


                        for user in users:
                            try:
                                await bot_fol.send_message(chat_id=user, text=f"🟢🟢🟢НОВОЕ СООБЩЕНИЕ🟢🟢🟢\n\n"
                                                                            f"{name}\n\n"
                                                                            f"{message_new}\n\n"
                                                                            f"{MS_LOT}",
                                                                            parse_mode='html',
                                                                            reply_markup = InlineKeyboardMarkup().add(
                                                                                InlineKeyboardButton(f"^^^ Удалить {name} ^^^",
                                                                                                 callback_data=f"delete {id_defaulter}")))
                            except:
                                pass

                if new != '':
                    # print(all_message_old)
                    message_ready = all_message_old + new
                    db.add_new_message_in_defaulter(message_ready, name)

            # print('sleep')
            await asyncio.sleep(900)
        except:
            print('ERROR')
            if indx%2 == 0:
                parser.selenium_cookie()
            # for user in users:
            #     try:
            #         await bot.send_message(user, 'ERROR')
            #     except:
            #         pass
            indx += 1
            await asyncio.sleep(450)
        # print('закончилась проверка follow')

@dp_fol.callback_query_handler(lambda x: x.data and x.data.startswith('delete '))
async def follow_run(callback_query: types.CallbackQuery):
    id_defaulter = callback_query.data.replace('delete ', '')
    await db.sql_delete_command(id_defaulter)
    await callback_query.answer('Вы престали отслеживать')

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('fol '))
async def follow_run(callback_query: types.CallbackQuery):
    # url_defaulter = f"https://old.bankrot.fedresurs.ru{tds[2].find('a').get('href')}"
    url_defaulter = f"https://old.bankrot.fedresurs.ru/{callback_query.data.replace('fol ', '')}"

    bankrotcookie = parser.bankrotcookie()
    #print(bankrotcookie)

    soup = parser.get_html(url_defaulter, config.HEADERS_def(bankrotcookie))
    data_defaulter = parser.parser_table_defaulter(soup, url_defaulter)

    if 'На сайте ошибка, перейдите по ссылке' in data_defaulter:
        await callback_query.answer(f'{data_defaulter}', show_alert=True)
    else:
        data_defaulter[0]['id_defaulter'] = callback_query.data.replace('fol ', '').split('=')[-1]
        data_defaulter[0]['defaulter_url'] = url_defaulter
        # print(data_defaulter)

        try:
            # try:
                await db.sql_add_defaulter(data_defaulter)
                await callback_query.answer(text=f'Вы начали следить за "{data_defaulter[0]["name"]}"', show_alert=True)
            # except:
            #     pass
        except:
            try:
                await callback_query.answer(f'Вы уже отслеживаете "{data_defaulter[0]["name"]}"', show_alert=True)
            except:
                pass

import SEARCH
SEARCH.register_handlers_admin(dp)

import add_chek_delete_key_words
add_chek_delete_key_words.register_handlers_key_words(dp)

# Запуска бота
# loop = asyncio.get_event_loop()
# loop.create_task(PARSER_WHILE())

# Запуска бота
# executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

# @dp.message_handler()
def Bot1():

    # await message.answer(message.text)
    loop = asyncio.get_event_loop()
    loop.create_task(PARSER_WHILE())
  #   loop = asyncio.get_event_loop()
  #   loop.create_task(PARSER_WHILE())
    executor.start_polling(dp, skip_updates=True)

# @dp_fol.message_handler()
def Bot2():
    # await message.answer(message.text)
    loop = asyncio.get_event_loop()
    loop.create_task(MONITOR_WHILE())
    executor.start_polling(dp_fol, skip_updates=True)

def GO():
    p1 = Process(target=Bot1)
    p2 = Process(target=Bot2)
    p1.start()
    p2.start()
    time.sleep(85800)
    p1.kill()
    p2.kill()

if __name__ == '__main__':
    # parser.selenium_cookie()

    p1 = Process(target=Bot1)
    p2 = Process(target=Bot2)
    p1.start()
    p2.start()

    # print('sleep ALL')
    time.sleep(85800)
    # print('moning')
    # p1.join()
    # p2.join()
    p1.kill()
    p2.kill()

