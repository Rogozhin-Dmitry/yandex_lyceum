from flask import Flask, request, render_template
from sqlite3 import connect
import logging
from logging.handlers import RotatingFileHandler
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from requests import post, get
from threading import Timer
from docxtpl import DocxTemplate, InlineImage
import docx
import re
from PIL import Image
import os
from email_file import send_email

telegram_api_key = 'токен от телеграмма'
yandex_maps_api_key = 'токен от яндекса'
telegram_admin_password = 'пароль в тг'
site_domain = 'домен на котором висит бот'
to_email_address = 'почта на которую высылаем'
email_address = 'логин'
password_address = 'пароль'
# внимание для получения ответов от telegram используется адрес: https://{site_domain}/telegram_bot,
# а для вывода карты https://{site_domain}/{ид пользователя},
# переключение отправки данных от телеграм на новый адрес реализована автомотически

if post(f'https://api.telegram.org/bot{telegram_api_key}/getWebhookInfo').json()['result']['url'] != \
        f'https://{site_domain}/telegram_bot':
    post(f'https://api.telegram.org/bot{telegram_api_key}/setwebhook')
    get(f'https://api.telegram.org/bot{telegram_api_key}/setwebhook?url=https://{site_domain}/telegram_bot')

application = Flask(__name__)
file_handler = RotatingFileHandler('python.log', maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.ERROR)
application.logger.setLevel(logging.ERROR)
application.logger.addHandler(file_handler)

start_keys = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton('Я нашёл борщевик')).add(KeyboardButton('Помощь'))
true_false = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton('Да')).add(KeyboardButton('Нет'))
location_keys = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton('Отправить свою локацию', request_location=True))


def add_hyperlink(paragraph, url, text, color, underline):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )
    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')
    if color is not None:
        c = docx.oxml.shared.OxmlElement('w:color')
        c.set(docx.oxml.shared.qn('w:val'), color)
        rPr.append(c)
    if not underline:
        u = docx.oxml.shared.OxmlElement('w:u')
        u.set(docx.oxml.shared.qn('w:val'), 'none')
        rPr.append(u)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink


def save_file(file_id, file_name):
    res = post(f'https://api.telegram.org/bot{telegram_api_key}/getFile', data={'file_id': file_id})
    file_path = res.json()['result']['file_path']
    with open(file_name, 'wb') as handler:
        handler.write(get(f'https://api.telegram.org/file/bot{telegram_api_key}/{file_path}').content)


def send_file(user_id, file_name, reply_markup):
    if reply_markup:
        post(f'https://api.telegram.org/bot{telegram_api_key}/sendDocument',
             files={'document': open(file_name, 'rb')}, data={'chat_id': user_id, 'reply_markup': reply_markup})
    else:
        post(f'https://api.telegram.org/bot{telegram_api_key}/sendDocument',
             files={'document': open(file_name, 'rb')}, data={'chat_id': user_id})


def send_mess(user_id, text, reply_markup):
    if reply_markup:
        post(f'https://api.telegram.org/bot{telegram_api_key}/sendMessage',
             data={'chat_id': user_id, 'text': text, 'reply_markup': reply_markup})
    else:
        post(f'https://api.telegram.org/bot{telegram_api_key}/sendMessage', data={'chat_id': user_id, 'text': text})


def send_photo(user_id, photo, caption, reply_markup):
    if reply_markup:
        post(f'https://api.telegram.org/bot{telegram_api_key}/sendPhoto',
             data={'chat_id': user_id, 'photo': photo, 'caption': caption, 'reply_markup': reply_markup})
    else:
        post(f'https://api.telegram.org/bot{telegram_api_key}/sendPhoto',
             data={'chat_id': user_id, 'photo': photo, 'caption': caption})


def send_geo_error(user_id):
    con = connect('data/db.db')
    cur = con.cursor()
    mg = cur.execute(f"SELECT must_geo FROM users WHERE id == '{user_id}'").fetchone()[0]
    if not mg:
        return
    cur.execute(f"UPDATE users SET must_geo=0 WHERE id == '{user_id}'")
    con.commit()
    send_mess(user_id, 'Наверное, вы заблокировали возможность получения геопозиции для Телеграм, ' +
              'давайте попробуем передать ваше местоположение через наш сайт.', str(ReplyKeyboardRemove()))

    send_mess(user_id, 'При переходе на сайт просто зафиксируйте местоположение и закройте вкладку.',
              str(InlineKeyboardMarkup(
              ).add(InlineKeyboardButton('Отправить локацию',
                                         url=f'https://location.easy-language.site/{user_id}'))))


def save_docx(param):
    doc = DocxTemplate("data/temp.docx")
    args = {}
    im = Image.open("temp/img.png")
    width, height = im.size
    if height > width:
        scale = 89 / height
        args['height'] = docx.shared.Mm(height * scale)
        args['width'] = docx.shared.Mm(width * scale)
    else:
        scale = 178 / width
        args['height'] = docx.shared.Mm(height * scale)
        args['width'] = docx.shared.Mm(width * scale)
    doc.render({
        'email': param[2],
        'location': f'{param[0].split(";")[0]}, {param[0].split(";")[1]}',
        'image': InlineImage(doc, image_descriptor='temp/img.png', **args),
        'name': param[-2]
    })
    doc.save(f"temp/file {param[-1]}.docx")


@application.route('/<int:user_id>', methods=['GET', 'POST'])
def index(user_id):
    if request.method == 'GET':
        return render_template('main.html', api_key=yandex_maps_api_key)
    con = connect('data/db.db')
    cur = con.cursor()
    data_ = cur.execute('SELECT * FROM users WHERE id == "' + str(user_id) + '"').fetchone()
    if data_[1] == 3:
        send_mess(user_id,
                  'Отлично, мы получили координаты. Для того, чтобы сформировать обращение, нам потребуется ваше ' +
                  'ФИО. Представьтесь, пожалуйста.', str(ReplyKeyboardRemove()))
    data = request.json
    if data['geo_location']:
        cur.execute(f'UPDATE template_references SET place="' + str(data['latitude']) + ";" +
                    str(data["longitude"]) + '" WHERE id == "' + str(data_[2]) + '"')
        cur.execute(f"UPDATE users SET step=5, must_geo=0 WHERE id == '{user_id}'")
        con.commit()
    else:
        cur.execute(f'UPDATE template_references SET place="' + str(data['latitude']) + ";" +
                    str(data["longitude"]) + '" WHERE id == "' + str(data_[2]) + '"')
        cur.execute(f"UPDATE users SET step=5, must_geo=0 WHERE id == '{user_id}'")
        con.commit()
    return {}, 200


@application.route('/all_marks', methods=['GET', 'POST'])
def all_marks():
    con = connect('data/db.db')
    cur = con.cursor()
    data = [[*i[0].split(';'), i[1], i[2], i[3]]
            for i in cur.execute('SELECT place, email, name, image_patch FROM references_ WHERE is_done=0').fetchall()]
    return render_template('all_marks.html', api_key=yandex_maps_api_key, all_marks=data)


@application.route('/telegram_bot', methods=['GET', 'POST'])
def bot():
    if request.method == 'GET':
        return 'all_ok'
    if 'message' not in request.json:
        return {}, 200
    message = request.json['message']
    user_id = message['chat']['id']
    application.logger.error(message)

    con = connect('data/db.db')
    cur = con.cursor()
    if 'photo' in message:
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(user_id) + '"').fetchone()
        if not data or data[1] != 1:
            send_mess(user_id, 'Не понял команды', '')
            return {}, 200
        cur.execute(
            f'UPDATE template_references SET image_patch="' + message['photo'][-1]['file_id'] + '" WHERE id == "' + str(
                data[2]) + '"')
        cur.execute(f"UPDATE users SET step=2 WHERE id == '{user_id}'")
        con.commit()
        send_mess(user_id, 'Спасибо! Теперь давайте определим, где он растет. Вы видите борщевик прямо сейчас?',
                  str(true_false))
        return {}, 200

    if 'location' in message:
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(user_id) + '"').fetchone()
        if not data or data[1] != 3:
            send_mess(user_id, 'Не понял команды', '')
            return {}, 200
        cur.execute(f'UPDATE template_references SET place="' + str(message['location']['latitude']) + ";" +
                    str(message['location']['longitude']) + '" WHERE id == "' + str(data[2]) + '"')
        cur.execute(f"UPDATE users SET step=4, must_geo=0 WHERE id == '{user_id}'")
        con.commit()
        send_mess(user_id, 'Геолокация определена верно?', str(true_false))
        return {}, 200

    if 'text' not in message:
        send_mess(user_id, 'Не понял команды', '')
        return {}, 200

    if message['text'] == '/start':
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(user_id) + '"').fetchone()
        if not data:
            cur.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
            con.commit()
        send_mess(user_id, 'Это бот, куда вы можете отправить фото и геолокацию борщевика в Новой Москве. Данные буд' +
                  'ут переданы в приемную депутата Мосгордумы Валерия Головченко.\nПобедим борщевик вместе!',
                  str(start_keys))

    elif message['text'].startswith('/become_an_admin') and len(message['text'].split()) == 2:
        if message['text'].split()[1] == telegram_admin_password:
            data = cur.execute('SELECT * FROM admin_list WHERE id == "' + str(user_id) + '"').fetchone()
            if data:
                send_mess(user_id, 'Вы уже админ, нельзя ещё раз стать админом', '')
                return {}, 200
            cur.execute("INSERT INTO admin_list (id) VALUES (?)", (user_id,))
            con.commit()
            send_mess(user_id, 'Отлично, теперь вы админ)', '')
        else:
            send_mess(user_id, 'Это не правильный пароль администратора', '')

    elif message['text'] == '/result':
        data = cur.execute('SELECT id FROM admin_list WHERE id == "' + str(user_id) + '"').fetchone()
        if not data:
            send_mess(user_id, 'Вы не админ и не имеете доступ к данной функции', '')
            return {}, 200
        data = cur.execute('SELECT place, image_patch, email, name FROM references_ WHERE is_done=0').fetchall()
        if not data:
            send_mess(user_id, 'Новых заявок нет', '')
        for i in data:
            send_photo(user_id, i[1], f'местоположение/кадастровый номер:\n' +
                       f'https://pkk.rosreestr.ru/#/search/{i[0].split(";")[0]},{i[0].split(";")[1]}/19/@5w3tqxnc7\n' +
                       f'координаты: {i[0].split(";")[0]}, {i[0].split(";")[1]}\n' +
                       f'email: {i[2]}\n' +
                       f'ФИО: {i[-1]}\n', '')

    elif message['text'] == '/result_docx':
        data = cur.execute('SELECT id FROM admin_list WHERE id == "' + str(user_id) + '"').fetchone()
        if not data:
            send_mess(user_id, 'Вы не админ и не имеете доступ к данной функции', '')
            return {}, 200
        data = cur.execute('SELECT place, image_patch, email, name, id FROM references_ WHERE is_done=0').fetchall()
        if not data:
            send_mess(user_id, 'Новых заявок нет', '')
        for i in data:
            save_file(i[1], 'temp/img.png')
            save_docx(i)
            send_file(user_id, f'temp/file {i[-1]}.docx', '')

    elif message['text'] == '/result_docx_done':
        data = cur.execute('SELECT id FROM admin_list WHERE id == "' + str(user_id) + '"').fetchone()
        if not data:
            send_mess(user_id, 'Вы не админ и не имеете доступ к данной функции', '')
            return {}, 200
        data = cur.execute('SELECT place, image_patch, email, name, id FROM references_ WHERE is_done=0').fetchall()
        if not data:
            send_mess(user_id, 'Новых заявок нет', '')
        for i in data:
            save_file(i[1], 'temp/img.png')
            save_docx(i)
            send_file(user_id, f'temp/file {i[-1]}.docx', '')
            cur.execute(f"UPDATE references_ SET is_done=1 WHERE id == '{i[-1]}'")
        con.commit()
        for i in data:
            if os.path.isfile(f'temp/file {i[-1]}.docx'):
                os.remove(f'temp/file {i[-1]}.docx')

    elif message['text'] == '/done' and 'reply_to_message' in message and \
            'photo' in message['reply_to_message']:
        data = cur.execute('SELECT id FROM admin_list WHERE id == "' + str(user_id) + '"').fetchone()
        if not data:
            send_mess(user_id, 'Вы не админ и не имеете доступ к данной функции', '')
            return {}, 200
        st = ';'.join(message['reply_to_message']['caption'].split('\n')[1].split('/')[5].split(','))
        cur.execute(f"UPDATE references_ SET is_done=1 WHERE place == '{st}'")
        i = cur.execute(f"SELECT id FROM references_ WHERE place == '{st}'")[0]

        con.commit()
        send_mess(user_id, 'Отлично, хорошо что вы выполнили заявку', '')
        if os.path.isfile(f'temp/file {i}.docx'):
            os.remove(f'temp/file {i}.docx')

    elif message['text'] == 'Помощь':
        send_mess(user_id,
                  'Это бот, куда вы можете отправить фото и геолокацию борщевика в Новой Москве. Данные будут' +
                  'переданы в приемную депутата Мосгордумы Валерия Головченко.\n\nЧто попросит бот? Отправить фото ' +
                  'борщевика. Сделайте фотографию и прикрепите к сообщению.\n\nУказать местоположение борщевика. Если' +
                  ' вы видите борщевик прямо сейчас, нажмите «Да» и отправьте свою локацию. \n\nЕсли функция ' +
                  'определения геопозиционирования включена на вашем устройстве, ее можно будет отправить боту в ' +
                  'сообщении. Если функция отключена или вы находитесь не рядом с точкой, где увидели борщевик, ' +
                  'укажите локацию с помощью нашего сайта. Просто выберете точку с местоположением и закройте ' +
                  'браузер.\n\nУкажите свои контактные данные Отправьте ФИО (в формате «Фамилия Имя Отчество» пол' +
                  'ностью) и адрес электронной  почты (в формате «test@test.ru»).\n\nСпасибо! Если у вас остались ' +
                  'вопросы, обращайтесь в интернет-приемную: dep39.duma.mos.ru', str(start_keys))

    elif message['text'] == 'Да':
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(user_id) + '"').fetchone()
        if not data or data[1] == 2:
            cur.execute(f"UPDATE users SET step=3, must_geo=1 WHERE id == '{user_id}'")
            con.commit()
            Timer(10.0, send_geo_error, args=(user_id,)).start()
            send_mess(user_id, 'Отправьте нам координаторы борщевика (геолокация должна быть включена).',
                      str(location_keys))
        elif not data or data[1] == 4:
            cur.execute(f"UPDATE users SET step=5, must_geo=0 WHERE id == '{user_id}'")
            con.commit()
            send_mess(user_id, 'Отлично, для того, чтобы сформировать обращение, нам потребуется ваше ФИО. ' +
                      'Представьте, пожалуйста.', str(ReplyKeyboardRemove()))
        else:
            send_mess(user_id, 'Не понял команды', '')
        return {}, 200

    elif message['text'] == 'Нет':
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(user_id) + '"').fetchone()
        if not data or data[1] == 2:
            cur.execute(f"UPDATE users SET step=3, must_geo=0 WHERE id == '{user_id}'")
            con.commit()
            send_mess(user_id, 'Укажите местоположение борщевика на нашем сайте.',
                      str(ReplyKeyboardRemove()))
            send_mess(user_id, 'При переходе на сайт просто зафиксируйте своё местоположение и закройте вкладку.',
                      str(InlineKeyboardMarkup(
                      ).add(InlineKeyboardButton('Отправить свою локацию',
                                                 url=f'https://location.easy-language.site/{user_id}'))))
        elif not data or data[1] == 4:
            cur.execute(f"UPDATE users SET step=3, must_geo=0 WHERE id == '{user_id}'")
            con.commit()
            send_mess(user_id, 'Жаль, давайте тогда попробуем указать местоположение борщевика на нашем сайте',
                      str(ReplyKeyboardRemove()))
            send_mess(user_id, 'При переходе на сайт просто зафиксируйте своё местоположение и закройте вкладку.',
                      str(InlineKeyboardMarkup(
                      ).add(InlineKeyboardButton('Отправить свою локацию',
                                                 url=f'https://location.easy-language.site/{user_id}'))))
        else:
            send_mess(user_id, 'Не понял команды', '')
    elif message['text'] == 'Я нашёл борщевик':
        count = cur.execute('SELECT MAX(id) FROM template_references').fetchone()[0]
        if not count:
            count = 0
        count += 1
        cur.execute("INSERT INTO template_references (id) VALUES (?)", (str(count),))
        cur.execute(f"UPDATE users SET step=1, template_references_id={count} WHERE id == '{user_id}'")
        con.commit()
        send_mess(user_id, 'Отлично, отправьте нам фото борщевика. (Лучше горизонтальное)', str(ReplyKeyboardRemove()))
    elif len(message['text'].split()) == 3:
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(user_id) + '"').fetchone()
        if not data or data[1] != 5:
            send_mess(user_id, 'Не понял команды', '')
            return {}, 200
        cur.execute(f'UPDATE template_references SET name="' + message['text'] + '" WHERE id == "' + str(data[2]) + '"')
        cur.execute(f"UPDATE users SET step=6 WHERE id == '{user_id}'")
        con.commit()
        send_mess(user_id, 'А теперь e-mail для связи.', str(ReplyKeyboardRemove()))
    elif len(message['text'].split('@')) == 2 and \
            re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', message['text']):
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(user_id) + '"').fetchone()
        if not data or data[1] != 6:
            send_mess(user_id, 'Не понял команды', '')
            return {}, 200
        count = cur.execute('SELECT MAX(id) FROM references_').fetchone()[0]
        if not count:
            count = 0
        count += 1
        data = cur.execute('SELECT place, image_patch, name FROM template_references WHERE id == "' + str(data[2]) + '"'
                           ).fetchone()
        cur.execute("INSERT INTO references_ (id, place, image_patch, email, is_done, name) VALUES (?, ?, ?, ?, ?, ?)",
                    (count, data[0], data[1], message['text'], False, data[2]))
        cur.execute(f"UPDATE users SET step=0 WHERE id == '{user_id}'")
        con.commit()
        send_mess(user_id, 'Спасибо! Вместе победим борщевик в Новой Москве!', str(start_keys))
        save_file(data[1], 'temp/img.png')
        save_docx([data[0], 'temp/img.png', message['text'], data[2], count])
        send_email(email_address, to_email_address, 'Новое обращение', '', [f'temp/file {count}.docx'],
                   password_address, 'smtp.yandex.ru')
    else:
        data = cur.execute('SELECT step FROM users WHERE id == "' + str(user_id) + '"').fetchone()[0]
        if data == 5:
            send_mess(user_id, 'Пожалуйста, укажите Фамилию Имя Отчество полностью.', '')
        elif data == 6:
            send_mess(user_id, 'Отправьте адрес электронной почты в формате test@test.ru', '')
        else:
            send_mess(user_id, 'Не понял команды', '')
    return {}, 200


@application.errorhandler(500)
def internal_error(exception):
    application.logger.error(exception)
    return {}, 200


if __name__ == '__main__':
    application.run()
