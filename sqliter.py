import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def add_message(self, a):
        """Добавляем новое сообщение"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `all_message` (`date_message`, `type_message`, `url_message`, `defaulter`, `url_defaulter`, `address`, `published`) VALUES(?,?,?,?,?,?,?)",
                                       (a['date'], a['type_message'], a['url_message'], a['defaulter'], a['url_defaulter'], a['address'], a['published']))

    def allpost_exists(self, url_message):
        """Проверяем, есть ли уже сообщение в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `all_message` WHERE `url_message` = ?', (url_message,)).fetchall()
            return bool(len(result))

    def sql_read(self):
        return self.cursor.execute('SELECT * FROM all_message').fetchall()

    async def sql_add_defaulter(self, data):
        # async with state.proxy() as data:
        self.cursor.execute('INSERT INTO follow VALUES (?, ?, ?, ?)', (f"{data[0]['id_defaulter']}",
                                                                       f"{data[0]['defaulter_url']}",
                                                                       f"{data[0]['name']}",
                                                                       f"{data[0]['all_message']}")) # tuple(data.values())
        self.connection.commit()

    def sql_read_defaulter_url_exists(self, defaulter_url):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `follow` WHERE `defaulter_url` = ?", (defaulter_url,)).fetchall()
            return bool(len(result))

    def sql_read_defaulter_url(self):
        # with self.connection:
        return self.cursor.execute("SELECT `defaulter_url` FROM `follow`").fetchall()

    def sql_read_all_message_defaulter(self, name):
        # with self.connection:
        return self.cursor.execute("SELECT `all_message_defaulter` FROM `follow` WHERE `defaulter_name` = ?", (name,)).fetchall()

    def add_new_message_in_defaulter(self, all_message_defaulter, defaulter_name):
        with self.connection:
            return self.cursor.execute("UPDATE `follow` SET `all_message_defaulter` = ? WHERE `defaulter_name` = ?", (all_message_defaulter, defaulter_name))

    async def sql_delete_command(self, id_defaulter):
        self.cursor.execute('DELETE FROM follow WHERE id_defaulter == ?', (id_defaulter,))
        self.connection.commit()

    async def sql_delete_command_only(self, url_defaulter):
        self.cursor.execute('DELETE FROM follow WHERE defaulter_url == ?', (url_defaulter,))
        self.connection.commit()

    #################################################

    def create_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS key_word(
           key_words TEXT);
        """)
        self.connection.commit()

    def sql_add_key_word(self, data):
        # async with state.proxy() as data:
        # print(data)
        self.cursor.execute('INSERT INTO `key_word` (key_words) VALUES(?)', (data,))
        self.connection.commit()

    def all_table(self):
        return self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    def all_key_words(self):
        return self.cursor.execute('SELECT * FROM key_word').fetchall()

    def all_key_words_exists(self, key_word):
        """Проверяем, есть ли уже ключевое слова в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `key_word` WHERE `key_words` = ?', (key_word,)).fetchall()
            return bool(len(result))

    def sql_delete_key_word(self, key_word):
        self.cursor.execute('DELETE FROM `key_word` WHERE `key_words` == ?', (key_word,))
        self.connection.commit()