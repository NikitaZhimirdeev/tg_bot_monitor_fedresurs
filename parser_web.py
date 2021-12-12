import requests
from bs4 import BeautifulSoup as BS4
from selenium import webdriver
from create_bot import dir_path
from aiogram.utils.markdown import hlink
import os

class PARSER():
    def get_html(self, URL, HEADERS):
        r = requests.get(URL, headers=HEADERS)
        soup = BS4(r.text, 'lxml')

        return soup

    def parse_table_all(self, soup):
        DATA = []
        # print(soup)
        try:
            table = soup.find('table', class_='bank').find_all('tr')
            del table[0], table[-2], table[-1]
        except:
            table = soup.find('table', class_='bank').find_all('tr')
            del table[0], table[-2], table[-1]

        for tr in table:
            tds = tr.find_all('td')
            date = tds[0].text.strip()
            type_message = tds[1].text.strip()
            url_message = f"https://old.bankrot.fedresurs.ru{tds[1].find('a').get('href')}"
            defaulter = tds[2].text.strip()
            url_defaulter = f"https://old.bankrot.fedresurs.ru{tds[2].find('a').get('href')}"
            address = tds[3].text.strip()
            published = tds[4].text.strip()
            DATA.append({
                'date': date,
                'type_message': type_message,
                'url_message': url_message,
                'defaulter': defaulter,
                'url_defaulter': url_defaulter,
                'address': address,
                'published': published
            })
            # print(f'{date} - {type_message} - {url_message} - {defaulter} - {url_defaulter}')
        return DATA

    def parser_table_defaulter(self, soup, url_defaulter):
        DATA = []
        # try:
        # print(url_defaulter)
        # print(soup)
        table = soup.find('table', class_='bank').find_all('tr')
        pages = soup.find('table', class_='bank').find('tr', class_='pager')
        try:
            name = soup.find('table', class_='au').find('tr', id='ctl00_cphBody_trFullName').find('span').text.strip()
        except:
            name = f"{soup.find('table', class_='au').find('span', id='ctl00_cphBody_lblLastName').text.strip()} " \
                   f"{soup.find('table', class_='au').find('span', id='ctl00_cphBody_lblFirstName').text.strip()} " \
                   f"{soup.find('table', class_='au').find('span', id='ctl00_cphBody_lblMiddleName').text.strip()} "

        if pages != None:
            # print('1')
            del table[0], table[-2], table[-1]
        else:
            # print('2')
            del table[0]

        all_message = ''
        for tr in table:
            tds = tr.find_all('td')
            type_message = tds[1].text.strip()
            url_message = f"https://old.bankrot.fedresurs.ru{tds[1].find('a').get('href')}"

            all_message += f'{url_message};'

        DATA.append({
            'name': name,
            'all_message': all_message
        })
        # except AttributeError:
        #     DATA = f'На сайте ошибка, перейдите по ссылке {url_defaulter}'
        return DATA

    def parser_lot(self, soup):
        LOT = [{}]
        try:
            table = soup.find('table', class_='lotInfo').find_all('tr')
        except:
            try:
                table = soup.find_all('table', class_='personInfo')[-1].find_all('tr')
            except:
                if 'аннулирован' in soup.text.strip().lower():
                    print('yes')
                    return 'Аннулировано'
                else:
                    h1 = soup.find('h1').text.strip()
                    return h1

        head = table[0].find_all('th')
        lot = table[1].find_all('td')
        del head[0], lot[0]
        len_table = len(head)

        for i in range(len_table):
            LOT[0][head[i].text.strip()] = lot[i].text.strip()

        # LOT.append()
        return LOT

    def create_MS_LOT(self, LOT):
        if len(LOT) == 1:
            MS = 'ИНФОРМАЦИЯ О ЛОТЕ:\n'
            for key, val in LOT[0].items():
                if key == 'Описание':
                    MS += f"{key} - {self.create_ms_kad_num(val)}\n"
                else:
                    MS += f"{key} - {val}\n"
            return MS
        else:
            MS = f'ИНФОРМАЦИЯ О ЛОТЕ:\n{LOT}'
            return MS

    def selenium_cookie(self):
        URL = 'https://old.bankrot.fedresurs.ru'

        oprion = webdriver.FirefoxOptions()
        oprion.set_preference('dom.webdriver.enabled', False)
        useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        oprion.set_preference('general.useragent.override', useragent)
        oprion.set_preference('dom.webnotifications.enabled', False)
        oprion.set_preference('media.volume_scale', '0.0')
        oprion.headless = True

        browser = webdriver.Firefox(options=oprion, executable_path=os.path.join(dir_path, 'geckodriver'))
        browser.get(URL)
        bankrotcookie = browser.get_cookies()[0]['value']

        with open(os.path.join(dir_path, 'bankrotcookie.txt'), 'w') as f:
            f.write(bankrotcookie)

        browser.close()
        browser.quit()

    def bankrotcookie(self):
        with open(os.path.join(dir_path, 'bankrotcookie.txt'), 'r') as f:
            bankrotcookie = f.read()
        return bankrotcookie

    def create_ms_kad_num(self, description):
        des_list = description.split(' ')
        MES = ''
        if len(des_list) != 0:
            for word in des_list:
                if len(word.split(':')) > 2:
                    chars_href = word.replace(';', '').replace(',', '').replace('№', '').split(':')
                    text_href = ''
                    for char in chars_href:
                        text_href += f'{char} %3A'
                    text_href = text_href.strip('%3A').replace(' ', '')
                    text_href += '&opened='

                    opened = ''
                    for char in chars_href:
                        n = char.lstrip('0')
                        if len(n) == 0:
                            n = '0'
                        opened += f'{n} %3A'
                    opened = opened.strip('%3A').replace(' ', '')
                    # print(opened)

                    # text_href = f"https://pkk.rosreestr.ru/#/search/@5w3tqxnjb?text={text_href}{opened}"
                    text_href = hlink(word, f"https://pkk.rosreestr.ru/#/search/@5w3tqxnjb?text={text_href}{opened}")

                    MES += f'{text_href} '

                else:
                    MES += f'{word} ' #.replace(".", "").replace("-", "").replace("(", "").replace(")", "")}
            return MES
        else:
            return MES

    # def create_ms_kad_num(self, LOT):
    #     description = LOT[0]['Описание']
    #     des_list = description.split(' ')
    #     MS_KAD_NUM = ''
    #     if len(des_list) != 0:
    #         MS_KAD_NUM = '\nКадастровые номера и ссылки:\n'
    #         for word in des_list:
    #             if len(word.split(':')) > 2:
    #                 print(word)
    #                 # 'https://pkk.rosreestr.ru/#/search/@5w3tqxnjb?text=50%3A18%3A0090313%3A77&opened=50%3A18%3A90313%3A77'
    #                 chars_href = word.replace('№', '').split(':')
    #                 text_href = ''
    #                 for char in chars_href:
    #                     text_href += f'{char}%3A'
    #                 text_href = text_href.strip('%3A')
    #                 text_href += '&opened='
    #
    #                 opened = ''
    #                 for char in chars_href:
    #                     n = char.lstrip('0')
    #                     if len(n) == 0:
    #                         n = '0'
    #                     opened += f'{n}%3A'
    #                 opened = opened.strip('%3A')
    #                 # print(opened)
    #
    #                 text_href = f"https://pkk.rosreestr.ru/#/search/@5w3tqxnjb?text={text_href}{opened}"
    #
    #                 print(text_href)
    #                 MS_KAD_NUM += f'{word} - {text_href}\n'
    #                 print()
    #
    #         if len(MS_KAD_NUM.strip('\nКадастровые номера и ссылки:\n')) == 0:
    #             MS_KAD_NUM = ''
    #
    #     return MS_KAD_NUM


