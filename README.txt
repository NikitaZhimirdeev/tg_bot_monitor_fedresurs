Имя бота - 
токен - 

Имя бота - 
токен - 

!!!Принцип работы бота!!!
Во время первого запуска бот запоминает ID пользователя, который его запустил.
Мониторинг сайта начинает с момента запуска бота(не смотря, что запускаете один файл, оба бота запускаются вместе).

fed_monitor отправляет запросы с куки на сайт с сообщениями, собирает все сообщения, сравнивает с теми, что имеются в БД и
если сообщения нет в БД, то отправляет его в fed_monitor всем у кого он активирован и запишет в БД. Под каждым сообщением имеется кнопка "Следить",
нажав на нее, бот внесет долдника в БД иначнет за ним следить. Так же имеется функция поиска должника по ИНН, чтобы начать поиск по ИНН
необходимо вызвать команду /search и следовать подсказкам бота (ВАЖНО!!! при выборе физ или юрлица, необходимо правильно выбрать,
т.к. ссылки на запросы отличаются), если в конце нажмете кнопку "Следить", то бот занесет должника в БД иначнет его мониторинг.

fed_alarm отправляет запросы с куки на страницу каждого должника из БД, собирает все сообщения, сравнивает с теми, что имеются в БД и
если сообщения нет в БД, то отправляет его в fed_alarm всем у кого он активирован и запишет в БД. Под каждым сообщением имеется кнопка "Удалить <имяДолжника>",
нажав на нее, бот удалить должника из бд и перестанет за ним следить. Так же имеется функция удалить по ссылке на страницу должника, чтобы 
удалить Должника из БД необходимо вызвать команду /delete и следовать подсказкам бота (при отправке ссылки желательно ссылку отправлть без
приписки в конце "&attempt=1", чтобы ссылка выглядила "https://old.bankrot.fedresurs.ru/PrivatePersonCard.aspx?ID=3CF64F4CF97B080A9C94D0F83120462E").

Для того, чтобы отключить бота для пользователя, необходимо просто остановить бота в аккаунте пользователя, чтобы
полностью отключить мониторинг необходимо отключить бота программно.

!!!Как устроен бот!!!
Бот написан на Python 3.9, для корректной работы необходимо установить любую версию Python3.9 или Python 3.9+.
Чтобы убедиться что у вас установлена необходимая версия Python ведите в консоли для win 'python' для linux 'python3'
и увидите вашу версию, если версия не указана, то у вас не установлен python, если же она ниже 3.9, то советую
обновить до более высокой. Чтобы запустить бота под win, перейдите в папку с ботом, установите необходимые библиотеки
при помощи команды "pip install <название библиотеки>" и запустите команду "python BOT.py".
Чтобы запустить бота под linux, перейдите в папку с ботом, установите необходимые библиотеки при помощи команды
"pip3 install -U <название библиотеки>" и запустите команду "python3 BOT.py". Если у вас вышло надпись "Бот вышел в сеть",
значит бот работает.

Бот протестирован под linux и windows
При первом запуске убедитесь, что у вас установелен Firefox, т.к. для поиска токена пользователя бот использует selenium.
На Windows просто зайдите на оф сайт, скачайте и установите firefox.
На Linux откройте командную и введите следующие команды "sudo apt-get update", "sudo apt-get install firefox".
 
Запуск бота производится из файла BOT.py
При первом запуске возможна задержка, подоэдите минут 10, если бот так и не заработает, то пишите, контакты указаны в конце документа.

Чтобы изменить частоту проверок бота, откройте файл BOT.py текстовым редактором, желательно обычном блокнотом,
в строке 67 имеется запись "await asyncio.sleep(86400) # Время сна, если необходимо изменить частоту проверки, то необходимо изменить число, время в секундах"
необходимо установить необходимое число, вместо "(86400)", это число означает сколько секунд парсер будет спать перед  тем как
заново проверять записи.

Бот написан при помощи следующих библиотек:
aiogram
asyncio
selenium
requests
bs4
lxml

Бот состоит из 6-и модулей и 3 файлов:
craate_bot.py - Модуль инициализации бота;

BOT.py - основной модуль работы бота, через данный модуль происходит запуск бота. В нем прописаны стартовые команды,
	запуск парсера и объявление кнопок панели админа;

config.py - коструктор Cookie, в данном модуле храняться шаблолны для корректного запроса;

SEARCH.py - модуль машины состояний, по добавлению иудалению должников + инлайн кнопки;

parser_web.py - модуль парсинг, в данном модуле прописаны все функции париснга документов и должников;

settings.py - В данном модуле хранится токены для обоих ботов;

sqliter.py - модуль в котором прописаны все команды для взаимодействия с БД;

bankrotcookie.txt - файл хранения токена для доступа к сайту(С ДАННЫМ ФАЙЛОМ НЕ ВЗАИМОДЕЙСТВОВАТЬ, ВСЕ ДЕЙСТВИЯ ПРОИСХОДЯТ АВТОМАТИЧЕСКИ);

databaseMonitor.db - локальный файл БД (SQLite3);

geckodriver - драйвер firefox для работы с selenium.

users.txt - файл хранения ID всех пользователей, которые запускали бота.

КОТАНКТЫ:
почта - nikitazhimirdeev@gmail.com
телеграмм - @ZhN719
