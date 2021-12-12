from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import os
import settings
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

bot = Bot(token=settings.TOKEN)
dp = Dispatcher(bot, storage=storage)

bot_fol = Bot(token=settings.TOKEN_2)
dp_fol = Dispatcher(bot_fol, storage=storage)

# Получаем полный путь к дирректории
dir_path = os.path.dirname(os.path.abspath(__file__))