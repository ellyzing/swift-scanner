import logging
import urllib
import tempfile
import os

import scan_v4 

from aiogram import Bot, Dispatcher, executor, types
# from telebot import types
import random

API_TOKEN = '1374384574:AAGMOmjrGPypAjbXD17kNXpmwOH2hY2O-P0'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands="start")
async def start_menu(message):
    message_text = 'Здравствуйте!\n\n' \
                    + 'Для начала сканирования загрузите файл с ip-адресами.\n\n' \
                    + 'Передайте мне ваш txt-файлик с ip-адресами, формат:\n' \
                    +  '195.201.115.2\n' \
                    +  '10.10.5-7.100-150\n' \
                    +  '192.168.0.0/24\n' \
                    +  '172.16.0.5/32\n\n' \
                    +  'По окончании сканирования вы получите уведомление и специально подготовленный файл log.txt\n\n' \
                    +  'Наберите /help - для отображения списка доступных команд.'

    await bot.send_message(message.chat.id, message_text)

@dp.message_handler(commands="info")
async def info_menu(message):
    message_text = 'Информация:\n\n' \
                    + 'Система предназначена для автоматизации сканирования заданного перечня ip-адресов на предмет открытых портов баз данных. При нахождении таких БД производится попытка подключения к ним по заданным словарям логинов и паролей. При успешном подключении происходит запрос перечня имеющихся БД на сканируемой системе. Полученная информация записывается в log-файл в формате txt.\n\n' \
                    + 'Возможно помимо единичных адресов указывать диапазоны адресов, в разных форматах (например: 192.168.0.0/24, 10.10.5-7.100-150, 172.16.0.5/32 и т.д.)\n\n' \
                    + 'Передайте мне ваш txt-файлик с ip-адресами, формат:\n' \
                    +  '195.201.115.2\n' \
                    +  '10.10.5-7.100-150\n' \
                    +  '192.168.0.0/24\n' \
                    +  '172.16.0.5/32\n\n' \
                    + 'Наберите /help - для отображения списка доступных команд.' 
    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(commands="help")
async def print_menu(message):
    message_text = 'Вот, что умеет этот бот:\n' \
                    + '/info - информация о боте\n' \
                    + '/help - отображает список доступных команд\n' \
                    + '/lol - присылает сводную информацию из выбранных источников'
    await bot.send_message(message.chat.id, message_text)

@dp.message_handler(commands="lol")
async def lol(message):
    keyboard = types.InlineKeyboardMarkup() 
    key_oven = types.InlineKeyboardButton(text='Овен', callback_data='zodiac') 
    keyboard.add(key_oven)
    key_lev = types.InlineKeyboardButton(text='Лев', callback_data='zodiac') 
    keyboard.add(key_lev)
    await bot.send_message(message.from_user.id, text='Выбери свой знак зодиака', reply_markup=keyboard)

# @dp.callback_query_handler(func=lambda call: True)
# async def ans(call):
#     if call.data == "zodiac":
#         msg = '123'
#         await bot.send_message(call.message.chat.id, msg)

@dp.message_handler()
async def answer(message: types.Message):
    #НАПИСАТЬ ОТВЕТЫ НА РАНДОМНЫЙ ТЕКСТ
    await message.answer('Я тебя не понимаю. Напиши /help.')


@dp.message_handler(content_types=['document'])
async def scan_message(msg: types.Message):
    #GET FILE
    document_id = msg.document.file_id
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    name = msg.document.file_name
    tf = os.path.join(tempfile.gettempdir(), 'ip_'+os.urandom(8).hex())
    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{API_TOKEN}/{fi}',tf)
    # fff = open(tf,"r")
    with open(tf, 'r') as fff:
        await bot.send_message(msg.from_user.id, 'Checking input file...')
        #ДОБАВИТЬ ПРОВЕРКИ
        await bot.send_message(msg.from_user.id, 'Processing...')
        #ОТПРАВИТЬ ФАЙЛ СКАНЕРУ
        await bot.send_message(msg.from_user.id, 'Scanning started!')
        scan_v4.Main(fff)
    #ПОЛУЧАТЬ ОТВЕТЫ ОТ СКАНЕРА И ВЫВОДИТЬ ПОЛЬЗОВАТЕЛЮ
    await bot.send_message(msg.from_user.id, 'Please wait, scanning in progress...')
    #ПОЛУЧИТЬ РЕЗУЛЬТАТ ОТ СКАНЕРА И ЗАПИСАТЬ ВО ВРЕМЕННЫЙ ФАЙЛ
    await bot.send_message(msg.from_user.id, 'Result:')
    res = open("log.txt", 'r')
    await bot.send_document(msg.from_user.id, res)
    await bot.send_message(msg.from_user.id, 'Scanning completed!')

    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
