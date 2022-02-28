from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from sqlite3 import connect
import string
import random
from time import sleep
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup

bot = Bot(token='токен телеграмм')
dp = Dispatcher(bot)
con = connect('data/db.db')
cur = con.cursor()

start_keys = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton('Я нашёл борщевик')).add(KeyboardButton('Помощь'))
location_keys = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton('Отправить свою локацию', request_location=True))


@dp.message_handler(commands=['start'])
async def start_mess(message: types.Message):
    data = cur.execute('SELECT * FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()
    if data:
        await bot.send_message(message.from_user.id, "Для помощи нажми кнопку помощь", reply_markup=start_keys)
        return
    cur.execute("INSERT INTO users (id, step, template_references_id) VALUES (?, ?, ?)", (message.from_user.id, 0, ''))
    con.commit()
    await bot.send_message(message.from_user.id, "Привет!\nНекий бот для борьбы с борщивеком, помощь",
                           reply_markup=start_keys)


@dp.message_handler()
async def echo_message(message: types.Message):
    if message.text == 'Я нашёл борщевик':
        count = cur.execute('SELECT MAX(id) FROM template_references').fetchone()[0]
        if not count:
            count = 0
        count += 1
        cur.execute("INSERT INTO template_references (id, place, image_patch, email, is_done) VALUES (" +
                    "?, ?, ?, ?, ?)",
                    (count, '', '', '', False))
        cur.execute(f"UPDATE users SET step=1, template_references_id={count} WHERE id == '{message.from_user.id}'")
        con.commit()
        await bot.send_message(message.from_user.id, 'Отлично, отправьте нам координато борщевика',
                               reply_markup=location_keys)
        sleep(10)
        await bot.send_message(message.from_user.id, 'Видимо вы заблокировали передачу геолокации через телеграмм,',
                               reply_markup=ReplyKeyboardRemove())
        await bot.send_message(message.from_user.id, 'давайте попробуем передать ваше местоположение через наш сайт,',
                               reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(
                                   'Отправить свою локацию',
                                   url=f'https://location.easy-language.site/{message.from_user.id}')))
        return
    elif len(message.text.split('@')) == 2:
        count = cur.execute('SELECT MAX(id) FROM references_').fetchone()[0]
        if not count:
            count = 0
        count += 1
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()
        data = cur.execute('SELECT place, image_patch FROM template_references WHERE id == "' + str(data[2]) +
                           '"').fetchone()
        cur.execute("INSERT INTO references_ (id, place, image_patch, email, is_done) VALUES (" +
                    "?, ?, ?, ?, ?)",
                    (count, data[0], data[1], message.text, False))
        await bot.send_message(message.from_user.id, 'Отлично, спасибо за заявку',
                               reply_markup=start_keys)
        return
    elif message.text == 'Помощь':
        await bot.send_message(message.from_user.id, 'некая помощь',
                               reply_markup=start_keys)
        return
    await bot.send_message(message.from_user.id, 'Не понял команду', reply_markup=start_keys)


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    img = 'data/images/' + ''.join(random.choice(string.ascii_lowercase) for _ in range(12)) + '.png'
    await message.photo[-1].download(img)
    data = cur.execute('SELECT * FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()
    cur.execute(f'UPDATE template_references SET image_patch="' + img + '" WHERE id == "' + str(data[2]) + '"')
    con.commit()
    await bot.send_message(message.from_user.id, 'Спасибо, а теперь ваш email для связи')


@dp.message_handler(content_types=['location'])
async def location_mess(message: types.Message):
    data = cur.execute('SELECT * FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()
    cur.execute(f'UPDATE template_references SET place="' + str(message.location.latitude) + ";" +
                str(message.location.longitude) + '" WHERE id == "' + str(data[2]) + '"')
    con.commit()
    await bot.send_message(message.from_user.id, 'А теперь фото борщевика',
                           reply_markup=ReplyKeyboardRemove())


if __name__ == '__main__':
    executor.start_polling(dp)
