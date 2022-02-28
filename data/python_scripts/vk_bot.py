import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from PIL import Image, ImageDraw, ImageFont
from requests import post
from random import randint, choice
import json
import configparser
import sys
import time
import sqlite3


def set_text(event, img):
    image_new = img.copy()
    ImageDraw.Draw(image_new).text(shift, ' '.join(event['text'].split()).upper(), font=fnt, fill=(255, 255, 255))
    image_new = image_new.convert('RGB')
    image_new.save('data/intermediate.jpg')

    url = vk_session.method('photos.getMessagesUploadServer', {'peer_id': int(event['peer_id'])})['upload_url']
    image_address = post(url, files={'photo': open('data/intermediate.jpg', 'rb')}).json()
    return vk_session.method('photos.saveMessagesPhoto', image_address)[0]


def start():
    global vk, vk_session, long_poll, keyboard_1, shift, fnt, any_text, end_text, end_text, start_text
    global subscription_text, keyboard_2, cur, con, waifu_list, im_neko, config, waifu_images, im_loli
    try:
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')

        con = sqlite3.connect("data/users.db")
        cur = con.cursor()
    except Exception as err:
        print('проблема с конфигурационным файлом или базой данных', err)
        time.sleep(50)
        sys.exit()
    else:
        print('конфигурационный файл на месте, и прочитан успешно, так же как и база данных')

    try:
        vk_session = vk_api.VkApi(token=config['config']['token'])
        vk = vk_session.get_api()
        long_poll = VkBotLongPoll(vk_session, config['config']['group_id'])
    except Exception as err:
        print('проблема с авторизацией вк', err)
        time.sleep(50)
        sys.exit()
    else:
        print('соединение с вк успешно')
    try:
        inline = bool(int(config['config']['inline']))
        keyboard_1 = json.load(open('data/keyboards/1.json', 'r', encoding='UTF-8'))
        keyboard_1["inline"] = inline
        keyboard_1 = json.dumps(keyboard_1)
        im_loli = []
        for i in config['config']['loli'].split(', '):
            im_loli.append(Image.open("data/images/" + i))
        im_neko = []
        for i in config['config']['neko'].split(', '):
            im_neko.append(Image.open("data/images/" + i))
        shift = [int(i) for i in config['config']['shift'].split(', ')]
        fnt = ImageFont.truetype('data/font.ttf', int(config['config']['font_size']))
        any_text = config['text']['any'].replace('/n', '\n')
        end_text = config['text']['end'].replace('/n', '\n')
        start_text = config['text']['start'].replace('/n', '\n')
        subscription_text = config['text']['subscription'].replace('/n', '\n')
    except Exception as err:
        print('проблема с загрузкой первой партии файлов (Неко, Лоли, и их клавиатура, размер шрифта, шрифт и сдвиг)',
              err)
        time.sleep(50)
        sys.exit()
    else:
        print('все файлы первой партии (Неко, Лоли, и их клавиатура, размер шрифта, шрифт и сдвиг) успешно открыты')
    try:
        waifu_images = {}
        waifu_list = config['waifu']['waifu'].split(', ')
        keys = []
        if inline:
            max_count = 6
        else:
            max_count = 10
        if len(waifu_list) <= max_count:
            for i in waifu_list:
                im_list = []
                for j in config['waifu'][i].split(', '):
                    im_list.append(Image.open("data/images/" + j))
                waifu_images[i] = im_list
                keys.append([{"action": {"type": "text", "label": i}, "color": "secondary"}])
        else:
            for i in range(max_count):
                keys.append([])
            counter = 0
            for i in waifu_list:
                im_list = []
                for j in config['waifu'][i].split(', '):
                    im_list.append(Image.open("data/images/" + j))
                waifu_images[i] = im_list
                keys[counter % max_count].append({"action": {"type": "text", "label": i}, "color": "secondary"})
                counter += 1
        keyboard_2 = json.dumps({"buttons": keys, "one_time": False, "inline": inline})
    except Exception as err:
        print('проблема с файлами второй партии Вайфу, скорее всего неправильный конфиг', err)
        time.sleep(50)
        sys.exit()
    else:
        print('все файлы загружены нормально')
    print('бот запущен успешно')


def main():
    for event in long_poll.check():
        # новое событие
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj['message']['peer_id'] == event.obj['message']['from_id']:
                event = event.obj['message']
                if event['peer_id'] == event['from_id']:  # обработка сообщений из лички
                    a = cur.execute(f"SELECT can_write FROM users WHERE id='{event['peer_id']}'").fetchall()
                    if not a:
                        cur.execute(f'INSERT INTO users VALUES ({event["peer_id"]}, {1})')
                        con.commit()
                        a.append([1])
                    if event['text'].lower() == 'лицензия':
                        cur.execute(f'UPDATE users SET can_write="{1}" WHERE id="{event["peer_id"]}"')
                        con.commit()
                        a.append([1])
                        vk.messages.send(
                            peer_id=event['peer_id'],
                            random_id=randint(0, 1000000),
                            message=start_text,
                            keyboard=keyboard_1
                        )
                    if event['text'].lower() == 'перезапуск' and (
                            event["peer_id"] == 389181122 or event["peer_id"] == 325805670):
                        vk.messages.send(
                            peer_id=event['peer_id'],
                            random_id=randint(0, 1000000),
                            message='бот будет перезапущен',
                            keyboard=keyboard_1
                        )
                        start()

                if a and int(a[0][0]):
                    if event['text'] in ['Лоли', 'Неко', *waifu_list]:
                        vk.messages.send(
                            peer_id=event['peer_id'],
                            random_id=randint(0, 1000000),
                            message='✨ Введите текст (никнейм) который будет на лицензии!\n⚠ До 12 символов!',
                            keyboard=json.dumps({"buttons": [], "one_time": True})
                        )
                    elif event['text'].lower() == 'стоп':
                        cur.execute(f'UPDATE users SET can_write="{0}" WHERE id="{event["peer_id"]}"')
                        con.commit()
                        vk.messages.send(
                            peer_id=event['peer_id'],
                            random_id=randint(0, 1000000),
                            message='Хорошо, умолкаю, пока )',
                            keyboard=json.dumps({"buttons": [], "one_time": True})
                        )
                    elif event['text'] == 'Вайфу':
                        vk.messages.send(
                            peer_id=event['peer_id'],
                            random_id=randint(0, 1000000),
                            message='Выберите вайфу из списка:\n' + '\n'.join(waifu_list),
                            keyboard=keyboard_2
                        )
                    else:
                        previous = \
                            vk_session.method('messages.getHistory', {'peer_id': int(event['peer_id'])})['items'][2]
                        if previous['text'] in ['Лоли', 'Неко', *waifu_list]:
                            if previous['text'] == 'Лоли':
                                image = choice(im_loli)
                            elif previous['text'] == 'Неко':
                                image = choice(im_neko)
                            else:
                                image = choice(waifu_images[previous['text']])
                            if 3 < len(''.join(event['text'].split())) and len(event['text']) <= 12:
                                ev = set_text(event, image)
                                if vk_session.method('groups.isMember', {'group_id': config['config']['group_id'],
                                                                         'user_id': int(event['peer_id'])}):
                                    vk.messages.send(
                                        peer_id=event['peer_id'],
                                        random_id=randint(0, 1000000),
                                        message=end_text,
                                        attachment=f'photo{ev["owner_id"]}_{ev["id"]}',
                                        keyboard=keyboard_1
                                    )
                                else:
                                    vk.messages.send(
                                        peer_id=event['peer_id'],
                                        random_id=randint(0, 1000000),
                                        message=end_text + '\n' + subscription_text,
                                        attachment=f'photo{ev["owner_id"]}_{ev["id"]}',
                                        keyboard=keyboard_1
                                    )
                            elif 3 >= len(''.join(event['text'].split())):
                                vk.messages.send(
                                    peer_id=event['peer_id'],
                                    random_id=randint(0, 1000000),
                                    message='Слишком мало символов в нике',
                                    keyboard=keyboard_1
                                )
                            else:
                                vk.messages.send(
                                    peer_id=event['peer_id'],
                                    random_id=randint(0, 1000000),
                                    message='Слишком много символов в нике',
                                    keyboard=keyboard_1
                                )
                        elif event['text'] != 'лицензия':
                            vk.messages.send(
                                peer_id=event['peer_id'],
                                random_id=randint(0, 1000000),
                                message=any_text,
                                keyboard=keyboard_1
                            )


vk, vk_session, long_poll, keyboard_1, shift, fnt, any_text, end_text = ['', '', '', '', '', '', '', '']
keyboard_2, cur, con, waifu_list, im_neko, config, waifu_images = ['', '', '', '', '', '', '']
end_text, start_text, subscription_text, im_loli = ['', '', '', '']
start()

while True:
    try:
        main()
    except Exception as err:
        print(err, 'перезапуск бота')
        start()
