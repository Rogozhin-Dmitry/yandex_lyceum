import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from sqlite3 import connect
import traceback

con = connect('/tmp/db.sqlite')
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS "admins" ("id" INTEGER)""")
cur.execute("""CREATE TABLE IF NOT EXISTS "chat_ids" ("id" INTEGER)""")
cur.execute("""CREATE TABLE IF NOT EXISTS "references_" ("id"	INTEGER, "photos" INTEGER, "email_phone_no" INTEGER,
 "reason" TEXT, "to_whom" TEXT, "user_id" INTEGER, "media_group_id" INTEGER, "count_id"	INTEGER)""")
cur.execute("""CREATE TABLE IF NOT EXISTS "template_references" (	"id" INTEGER, "photos" INTEGER, 
"email_phone_no" INTEGER, "reason" TEXT, "to_whom" TEXT, "user_id" INTEGER)""")
cur.execute(
    """CREATE TABLE IF NOT EXISTS "users" ("id" INTEGER, "template_references_id"	INTEGER, "step"	INTEGER)""")

bot = Bot(os.environ.get('TOKEN'))
dp_official = Dispatcher(bot)
contacts_keys = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('ДА, НАПИШИТЕ В ТГ'), KeyboardButton('ДА, ПОЗВОНИТЕ МНЕ ПО ТЕЛЕФОНУ')).add(
    KeyboardButton('ДА, НАПИШИТЕ НА ПОЧТУ'), KeyboardButton('НЕТ')).add(KeyboardButton('Отмена'))

yes_no_keys_1 = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Прикрепить ещё одно фото')).add(KeyboardButton('Нет, спасибо')).add(KeyboardButton('Отмена'))

yes_no_keys = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Прикрепить фото')).add(KeyboardButton('Нет, спасибо')).add(KeyboardButton('Отмена'))

start_keys = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Отправить обращение')).add(KeyboardButton('О боте'))

start_keys_1 = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Отправить ещё одно обращение')).add(KeyboardButton('О боте'))

address_keys = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('НЕ ЗНАЮ'), KeyboardButton('ГЛАВА ГОРОДА')).add(
    KeyboardButton('АДМИНИСТРАЦИЯ'), KeyboardButton('СЛУЖБЫ')).add(
    KeyboardButton('СОВЕТ ДЕПУТАТОВ'), KeyboardButton('ДРУГОЕ')).add(KeyboardButton('Отмена'))

address_keys_1 = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Пресс-служба'), KeyboardButton('Организационный отдел')).add(
    KeyboardButton('Управление архитектуры и градостроительства')).add(
    KeyboardButton('Отдел культуры'), KeyboardButton('Отдел развития наукограда')).add(
    KeyboardButton('Отдел по учету и приватизации жилого фонда')).add(
    KeyboardButton('Отдел социального развития'), KeyboardButton('Управление образования')).add(
    KeyboardButton('Отдел торговли и предпринимательской деятельности')).add(
    KeyboardButton('Отдел физической культуры и спорта'), KeyboardButton('Юридический отдел')).add(
    KeyboardButton('Управление жилищно-коммунального хозяйства')).add(
    KeyboardButton('Управление муниципального имущества')).add(KeyboardButton('Управление по социальным вопросам')).add(
    KeyboardButton('Управление территориальной безопасности')).add(
    KeyboardButton('Управление экономики и муниципальных заказов')).add(
    KeyboardButton('ДРУГОЕ'), KeyboardButton('Отмена'))

address_keys_2 = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Троицкая электросеть'), KeyboardButton('ООО «Агентство «Талион»')).add(
    KeyboardButton('АО «Троицкая коммунальная служба»'), KeyboardButton('ООО «ТроицкЖилСервис»')).add(
    KeyboardButton('ООО «ЖЭК «Комфорт»'), KeyboardButton('Теплоэнерго')).add(
    KeyboardButton('МБУ "ДХБ"'), KeyboardButton('Здравоохранение')).add(
    KeyboardButton('ООО «Академсервис»'), KeyboardButton('ООО УК «ДОМКОМ-Изумруд»')).add(
    KeyboardButton('ДРУГОЕ'), KeyboardButton('Отмена'))

all_buttons = ['ГЛАВА ГОРОДА', 'СОВЕТ ДЕПУТАТОВ', 'Пресс-служба', 'Организационный отдел',
               'Управление архитектуры и градостроительства', 'Отдел культуры', 'Отдел развития наукограда',
               'Отдел по учету и приватизации жилого фонда', 'Отдел социального развития', 'Управление образования',
               'Отдел торговли и предпринимательской деятельности', 'Отдел физической культуры и спорта',
               'Юридический отдел', 'Управление жилищно-коммунального хозяйства', 'Управление муниципального имущества',
               'Управление по социальным вопросам', 'Управление территориальной безопасности',
               'Управление экономики и муниципальных заказов', 'Троицкая электросеть', 'ООО «Агентство «Талион»',
               'АО «Троицкая коммунальная служба»', 'ООО «ТроицкЖилСервис»', 'ООО «ЖЭК «Комфорт»', 'Теплоэнерго',
               'МБУ "ДХБ"', 'Здравоохранение', 'ООО «Академсервис»', 'ООО УК «ДОМКОМ-Изумруд»']


# Handlers
async def start_mess(message: types.Message):
    try:
        data = cur.execute('SELECT * FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()
        if not data:
            cur.execute("INSERT INTO users (id, template_references_id, step) VALUES (?, ?, ?)",
                        (message.from_user.id, '', 0))
            con.commit()
        else:
            cur.execute(f"UPDATE users SET template_references_id=0, step=0 WHERE id == '{message.from_user.id}'")
            cur.execute(f"DELETE FROM template_references WHERE id == '{data}'")
            con.commit()
        await bot.send_message(message.from_user.id,
                            "Здравствуйте, это бот, куда вы можете отправить вопрос, предложение или описание проблемы" +
                            ", с которой вы столкнулись в Троицке. Мы составим и отправим запрос в нужную инстанцию, и" +
                            " будем держать вас в курсе того, как решается проблема.", reply_markup=start_keys)
    except Exception as ex:
        await bot.send_message('1141685563', ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))


async def reserve_save(message: types.Message):
    data = cur.execute(f'SELECT * FROM admins WHERE id == "{message.from_user.id}"').fetchone()
    if 'chat' in message:
        _id = message.chat.id
    else:
        _id = message.from_user.id
    if data:
        await message.reply_document(open('/tmp/db.sqlite', 'rb'))
    else:
        await bot.send_message(_id, 'Вы не администратор')
    return


async def add_to_mailing_list_mess(message: types.Message):
    data = cur.execute(f'SELECT * FROM admins WHERE id == "{message.from_user.id}"').fetchone()
    if 'chat' in message:
        _id = message.chat.id
    else:
        _id = message.from_user.id
    if data:
        data = cur.execute(f'SELECT * FROM chat_ids WHERE id == "{_id}"').fetchone()
        if not data:
            cur.execute("INSERT INTO chat_ids (id) VALUES (?)", (_id,))
            con.commit()
        await bot.send_message(_id, 'Беседа добавлена в рассылку')
    else:
        await bot.send_message(_id, 'Вы не администратор')
    return


async def get_all_requests_mess(message: types.Message):
    data = cur.execute(f'SELECT * FROM admins WHERE id == "{message.from_user.id}"').fetchone()
    if 'chat' in message:
        _id = message.chat.id
    else:
        _id = message.from_user.id
    try:
        if data:
            data_1 = cur.execute(f"SELECT * FROM references_").fetchall()
            if not data_1:
                await bot.send_photo(_id, 'Обращений пока нет')
            for i in data_1:
                if '@' in str(i[2]):
                    text = 'Просил уведомить через почту: ' + str(i[2])
                elif i[2] == 'no':
                    text = 'Просил не уведомлять'
                elif len(str(i[2]).split()) > 1:
                    text = 'Просил уведомить через телефон: ' + str(i[2])
                else:
                    text = 'Просил уведомить через телегамм: ' + str(i[2])
                try:
                    if i[1]:
                        if len(i[1]) == 1:
                            await bot.send_photo(_id, i[1], caption=f'id обращения: # {i[5]}_{i[-1]}\n' +
                                                                    f'Кому направлено обращение: {i[4]}\n' +
                                                                    f' Причина обращения: {i[3]}\n{text}')
                        else:
                            media = [InputMediaPhoto(i[1].split()[0],
                                                     f'id обращения: # {i[5]}_{i[-1]}\nКому направлено обращение: {i[4]}' +
                                                     f'\nПричина обращения: {i[3]}\n{text}')]
                            for photo_id in i[1].split()[1:]:
                                media.append(InputMediaPhoto(photo_id))
                            await bot.send_media_group(_id, media)
                    else:
                        await bot.send_message(_id, f'id обращения: # {i[5]}_{i[-1]}\nКому направлено обращение: {i[4]}\n' +
                                               f'Причина обращения: {i[3]}\n{text}')
                except Exception as e:
                    print(e)
                    continue
        else:
            await bot.send_message(_id, 'Вы не администратор')
        return
    except Exception as ex:
        await bot.send_message(_id, ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)))


async def handle_docs_photo(message):
    data = cur.execute('SELECT step FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
    if data == 4:
        data = cur.execute(
            'SELECT template_references_id FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        data_1 = cur.execute('SELECT photos FROM template_references WHERE id == "' + str(data) + '"').fetchone()
        if data_1:
            data_1 = data_1[0] + ' ' + message.photo[-1]['file_id']
        else:
            data_1 = message.photo[-1]['file_id']
        cur.execute(f"UPDATE template_references SET photos='{data_1}' WHERE id == '{data}'")
        con.commit()
        await bot.send_message(message.from_user.id, 'Спасибо. Хотите прикрепить еще одну фотографию?',
                               reply_markup=yes_no_keys_1)


async def echo(message: types.Message):
    data = cur.execute('SELECT * FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()
    if not data:
        cur.execute("INSERT INTO users (id, template_references_id, step) VALUES (?, ?, ?)",
                    (message.from_user.id, '', 0))
        con.commit()
        await bot.send_message(message.from_user.id, "Здравствуйте, это бот, куда вы можете отправить вопрос, предлож" +
                               "ение или описание проблемы, с которой вы столкнулись в Троицке. Мы составим и отправи" +
                               "м запрос в нужную инстанцию, и будем держать вас в курсе того, как решается проблема.",
                               reply_markup=start_keys)
        return

    message.text = message.text.replace("'", '').replace('"', '')
    if message.reply_to_message:
        data = cur.execute(f'SELECT * FROM admins WHERE id == "{message.from_user.id}"').fetchone()
        if 'chat' in message:
            _id = message.chat.id
        else:
            _id = message.from_user.id
        if not data:
            await bot.send_message(_id, 'Вы не администратор')
            return
        if message.reply_to_message.text and message.reply_to_message.text.startswith('id обращения: # '):
            await bot.send_message(message.reply_to_message.text.replace('id обращения: # ', '').split('_')[0],
                                   message.text)
            await bot.send_message(_id, 'Ответ успешно отправлен')
            return
        if message.reply_to_message.caption and message.reply_to_message.caption.startswith('id обращения: # '):
            await bot.send_message(message.reply_to_message.caption.replace('id обращения: # ', '').split('_')[0],
                                   message.text)
            await bot.send_message(_id, 'Ответ успешно отправлен')
            return
        if message.reply_to_message.photo and message.reply_to_message.photo[-1]:
            data_1 = cur.execute(f"SELECT * FROM references_" +
                                 f" WHERE media_group_id == {message.reply_to_message['media_group_id']}").fetchone()
            if data_1:
                await bot.send_message(data_1[5], message.text)
                await bot.send_message(_id, 'Ответ успешно отправлен')
            return
    if message.text == 'АДМИНИСТРАЦИЯ':
        await bot.send_message(message.from_user.id, 'Кому конкретно из администрации?', reply_markup=address_keys_1)
        return
    elif len(message.text.split()) == 3 and 'Стать администратором' in message.text:
        if message.text.split()[-1] == os.environ.get('ADMIN_PASSWORD'):
            cur.execute("INSERT INTO admins (id) VALUES (?)", (message.from_user.id,))
            con.commit()
            await bot.send_message(message.from_user.id, 'Вы стали администратором')
        else:
            await bot.send_message(message.from_user.id, 'Неправильный пароль')
        return
    elif message.text == 'ДРУГОЕ':
        await bot.send_message(message.from_user.id, 'Напишите, кому направить вопрос?',
                               reply_markup=ReplyKeyboardRemove())
        return
    elif message.text == 'СЛУЖБЫ':
        await bot.send_message(message.from_user.id, 'Кому конкретно из служб?', reply_markup=address_keys_2)
        return
    elif message.text == 'НЕ ЗНАЮ':
        await bot.send_message(message.from_user.id, 'Опишите, кому примерно адресован вопрос?',
                               reply_markup=ReplyKeyboardRemove())
        return
    elif message.text == 'ДА, НАПИШИТЕ НА ПОЧТУ':
        data = cur.execute('SELECT step FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if str(data) == '5':
            cur.execute(f"UPDATE users SET step=6 WHERE id == '{message.from_user.id}'")
            con.commit()
            await bot.send_message(message.from_user.id, 'Укажите пожалуйста почту'
                                                         '',
                                   reply_markup=ReplyKeyboardRemove())
        return
    elif message.text == 'ДА, ПОЗВОНИТЕ МНЕ ПО ТЕЛЕФОНУ':
        data = cur.execute('SELECT step FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if str(data) == '5':
            cur.execute(f"UPDATE users SET step=6 WHERE id == '{message.from_user.id}'")
            con.commit()
            await bot.send_message(message.from_user.id, 'Укажите номер телефона и удобное время',
                                   reply_markup=ReplyKeyboardRemove())
        return
    elif message.text == 'ДА, НАПИШИТЕ В ТГ':
        data = cur.execute('SELECT step FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if str(data) == '5':
            cur.execute(f"UPDATE users SET step=8 WHERE id == '{message.from_user.id}'")
            con.commit()
            await bot.send_message(message.from_user.id, 'Укажите, пожалуйста контактный номер телефона, ' +
                                   'чтобы мы могли уточнить запрос', reply_markup=ReplyKeyboardRemove())
        return
    elif message.text in ['ДА, НАПИШИТЕ В ТГ', 'НЕТ']:
        data = cur.execute('SELECT template_references_id FROM users WHERE id == "'
                           + str(message.from_user.id) + '"').fetchone()[0]
        if data:
            data_1 = cur.execute(f"SELECT * FROM template_references WHERE id == '{data}'").fetchone()
            cur.execute(f"UPDATE users SET template_references_id=0, step=0 WHERE id == '{message.from_user.id}'")
            cur.execute(f"DELETE FROM template_references WHERE id == '{data}'")
            count = cur.execute('SELECT MAX(id) FROM references_').fetchone()[0]
            if not count:
                count = 0
            count += 1
            count_1 = \
                cur.execute('SELECT MAX(count_id) FROM references_ WHERE' +
                            f' user_id =="{message.from_user.id}"').fetchone()[0]
            if not count_1:
                count_1 = 0
            count_1 += 1
            if message.text == 'НЕТ':
                text = 'no'
            else:
                text = 'telegram'
            cur.execute(
                "INSERT INTO references_ (id, photos, email_phone_no, reason, to_whom, user_id, count_id) VALUES (" +
                "?, ?, ?, ?, ?, ?, ?)",
                (count, data_1[1], text, data_1[3], data_1[4], message.from_user.id, count_1))
            cur.execute(f"DELETE FROM template_references WHERE id == '{data}'")
            con.commit()
            await bot.send_message(message.from_user.id, 'Спасибо! Мы взяли ваше обращение в работу.',
                                   reply_markup=start_keys_1)
            message = [count, data_1[1], text, data_1[3], data_1[4], message.from_user.id]
            data = cur.execute(f"SELECT * FROM chat_ids").fetchall()
            for _id in data:
                if message[2] == 'telegram':
                    text = 'Просил уведомить через телеграм'
                elif '@' in message[2]:
                    text = 'Просил уведомить через почту: ' + message[2]
                elif message[2] == 'no':
                    text = 'Просил не уведомлять'
                else:
                    text = 'Просил уведомить через телефон: ' + message[2]
                try:
                    if message[1]:
                        if message[1][0] == ' ':
                            message[1] = message[1][1:]
                        if len(message[1].split()) == 1:
                            await bot.send_photo(_id[0], message[1],
                                                 caption=f'id обращения: # {message[-1]}_{count_1}\n' +
                                                         f'Кому направлено обращение: {message[4]}\n' +
                                                         f' Причина обращения: {message[3]}\n{text}',
                                                 reply_markup=ReplyKeyboardRemove())
                        else:
                            media = [InputMediaPhoto(message[1].split()[0],
                                                     f'id обращения: # {message[-1]}_{count_1}\nКому направлено ' +
                                                     f'обращение: {message[4]}' +
                                                     f'\nПричина обращения: {message[3]}\n{text}')]
                            for photo_id in message[1].split()[1:]:
                                media.append(InputMediaPhoto(photo_id))
                            mess = await bot.send_media_group(_id[0], media)
                            cur.execute(f"UPDATE references_ SET media_group_id={mess[0].media_group_id}" +
                                        f" WHERE id == {count}")
                            con.commit()
                    else:
                        await bot.send_message(_id[0],
                                               f'id обращения: # {message[-1]}_{count_1}\nКому направлено обращен' +
                                               f'ие: {message[4]}\n' +
                                               f'Причина обращения: {message[3]}\n{text}',
                                               reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    print(e)
                    continue
            return
    elif message.text == 'Прикрепить фото' or message.text == 'Прикрепить ещё одно фото':
        data = cur.execute('SELECT step FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if str(data) == '3' or str(data) == '4':
            cur.execute(f"UPDATE users SET step=4 WHERE id == '{message.from_user.id}'")
            con.commit()
            await bot.send_message(message.from_user.id, 'Отправьте фотографию в чат!',
                                   reply_markup=ReplyKeyboardRemove())
            return
    elif message.text == 'Нет, спасибо':
        data = cur.execute('SELECT step FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if str(data) == '3' or str(data) == '4':
            cur.execute(f"UPDATE users SET step=5 WHERE id == '{message.from_user.id}'")
            await bot.send_message(message.from_user.id,
                                   'Хотите, чтобы мы сообщали вам о том, что происходит с обращением?',
                                   reply_markup=contacts_keys)
            return
    elif message.text == 'Отмена':
        data = cur.execute(
            'SELECT template_references_id FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if data:
            cur.execute(f"DELETE FROM template_references WHERE id == '{data}'")
        cur.execute(f"UPDATE users SET template_references_id=0, step=0 WHERE id == '{message.from_user.id}'")
        con.commit()
        await bot.send_message(message.from_user.id, 'Главное меню', reply_markup=start_keys)
        return
    elif message.text == 'О боте':
        await bot.send_message(message.from_user.id, 'Это бот, куда вы можете отправить вопрос, предложение или описа' +
                               'ние проблемы, с которой вы столкнулись в Троицке. Мы составим и отправим запрос в нуж' +
                               'ную инстанцию, и будем держать вас в курсе того, как решается проблема.\nВажный момен' +
                               'т: мы не являемся представителями органов власти или коммунальных служб. Мы — простые' +
                               ' горожане, которые считают, что технологии должны упрощать жизнь.\nЧто попросит бот?' +
                               '\nУказать, кому адресовано обращение. Если точно не знаете, мы сами определим наиболе' +
                               'е подходящий вариант.\nПрикрепить фото. Фотография поможет проиллюстрировать суть воп' +
                               'роса / предложения / проблемы. Но если у вас нет фотографии, то обращение можно отпра' +
                               'вить и без нее.\nВыбрать способ связи. Мы можем информировать вас о том, как развивае' +
                               'тся судьба обращения. Выберете наиболее удобный способ связи: телеграм, телефон или п' +
                               'очта.\nСпасибо! Если у вас остались вопросы, напишите на troitsk2022@yandex.ru.',
                               reply_markup=start_keys)
        return
    elif message.text == 'Отправить обращение' or message.text == 'Отправить ещё одно обращение':
        data = cur.execute(
            'SELECT template_references_id FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if not data:
            count = cur.execute('SELECT MAX(id) FROM template_references').fetchone()[0]
            if not count:
                count = 0
            count += 1
            cur.execute(
                "INSERT INTO template_references (id, photos, email_phone_no, reason, to_whom, user_id) VALUES (" +
                "?, ?, ?, ?, ?, ?)",
                (count, '', '', '', '', message.from_user.id))
            cur.execute(f"UPDATE users SET template_references_id={count}, step=1 " +
                        f"WHERE id == '{message.from_user.id}'")
        else:
            cur.execute(f"UPDATE template_references SET photos='', email_phone_no='', reason='', to_whom='' " +
                        f"WHERE id == '{data}'")
        con.commit()
        await bot.send_message(message.from_user.id, 'Кому адресован вопрос?',
                               reply_markup=address_keys)
        return
    elif message.text in all_buttons:
        data = cur.execute(
            'SELECT template_references_id FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if data:
            cur.execute(f"UPDATE users SET step=2 WHERE id == '{message.from_user.id}'")
            cur.execute(f"UPDATE template_references SET to_whom='{message.text}' WHERE id == '{data}'")
            con.commit()
            await bot.send_message(message.from_user.id, 'Сформулируйте свой вопрос / предложение / описание проблемы.',
                                   reply_markup=ReplyKeyboardRemove())
            return
    else:
        data = cur.execute(
            'SELECT template_references_id FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
        if data:
            data_2 = cur.execute('SELECT to_whom FROM template_references WHERE id == "'
                                 + str(data) + '"').fetchone()[0]
            data_1 = cur.execute('SELECT step FROM users WHERE id == "' + str(message.from_user.id) + '"').fetchone()[0]
            if data_2 and str(data_1) == '2':
                cur.execute(f"UPDATE template_references SET reason='{message.text}' WHERE id == '{data}'")
                cur.execute(f"UPDATE users SET step=3 WHERE id == '{message.from_user.id}'")
                con.commit()
                await bot.send_message(message.from_user.id, 'Хотите прикрепить фото к обращению?',
                                       reply_markup=yes_no_keys)
                return
            elif str(data_1) == '1':
                cur.execute(f"UPDATE template_references SET to_whom='{message.text}' WHERE id == '{data}'")
                cur.execute(f"UPDATE users SET step=2 WHERE id == '{message.from_user.id}'")
                con.commit()
                await bot.send_message(message.from_user.id,
                                       'Сформулируйте свой вопрос / предложение / описание проблемы.',
                                       reply_markup=ReplyKeyboardRemove())
                return
            elif str(data_1) == '6':
                data_1 = cur.execute(f"SELECT * FROM template_references WHERE id == '{data}'").fetchone()
                cur.execute(f"UPDATE users SET template_references_id=0, step=0 WHERE id == '{message.from_user.id}'")
                cur.execute(f"DELETE FROM template_references WHERE id == '{data}'")
                count = cur.execute('SELECT MAX(id) FROM references_').fetchone()[0]
                if not count:
                    count = 0
                count += 1
                count_1 = \
                    cur.execute('SELECT MAX(count_id) FROM references_ WHERE' +
                                f' user_id =="{message.from_user.id}"').fetchone()[0]
                if not count_1:
                    count_1 = 0
                count_1 += 1
                cur.execute("INSERT INTO references_ (id, photos, email_phone_no, reason, to_whom, user_id, count_id)"
                            " VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (count, data_1[1], message.text, data_1[3], data_1[4], message.from_user.id, count_1))
                cur.execute(f"DELETE FROM template_references WHERE id == '{data}'")
                cur.execute(f"UPDATE users SET template_references_id=0, step=0 WHERE id == '{message.from_user.id}'")
                con.commit()
                await bot.send_message(message.from_user.id, 'Спасибо! Мы взяли ваше обращение в работу.',
                                       reply_markup=start_keys_1)
                message = [count, data_1[1], message.text, data_1[3], data_1[4], message.from_user.id]
                data = cur.execute(f"SELECT * FROM chat_ids").fetchall()
                for _id in data:
                    if message[2] == 'telegram':
                        text = 'Просил уведомить через телеграм'
                    elif '@' in message[2]:
                        text = 'Просил уведомить через почту: ' + message[2]
                    elif message[2] == 'no':
                        text = 'Просил не уведомлять'
                    else:
                        text = 'Просил уведомить через телефон: ' + message[2]
                    try:
                        if message[1]:
                            if message[1][0] == ' ':
                                message[1] = message[1][1:]
                            if len(message[1].split()) == 1:
                                await bot.send_photo(_id[0], message[1],
                                                     caption=f'id обращения: # {message[-1]}_{count_1}\n' +
                                                             f'Кому направлено обращение: {message[4]}\n' +
                                                             f' Причина обращения: {message[3]}\n{text}',
                                                     reply_markup=ReplyKeyboardRemove())
                            else:
                                media = [InputMediaPhoto(message[1].split()[0],
                                                         f'id обращения: # {message[-1]}_{count_1}\nКому направлено ' +
                                                         f'обращение: {message[4]}' +
                                                         f'\nПричина обращения: {message[3]}\n{text}')]
                                for photo_id in message[1].split()[1:]:
                                    media.append(InputMediaPhoto(photo_id))
                                mess = await bot.send_media_group(_id[0], media)
                                cur.execute(f"UPDATE references_ SET media_group_id={mess[0].media_group_id}" +
                                            f" WHERE id == {count}")
                                con.commit()
                        else:
                            await bot.send_message(_id[0],
                                                   f'id обращения: # {message[-1]}_{count_1}\nКому направлено обращен' +
                                                   f'ие: {message[4]}\n' +
                                                   f'Причина обращения: {message[3]}\n{text}',
                                                   reply_markup=ReplyKeyboardRemove())
                    except Exception as e:
                        print(e)
                        continue
                return
            elif str(data_1) == '8':
                data_1 = cur.execute(f"SELECT * FROM template_references WHERE id == '{data}'").fetchone()
                cur.execute(f"UPDATE users SET template_references_id=0, step=0 WHERE id == '{message.from_user.id}'")
                cur.execute(f"DELETE FROM template_references WHERE id == '{data}'")
                count = cur.execute('SELECT MAX(id) FROM references_').fetchone()[0]
                if not count:
                    count = 0
                count += 1
                count_1 = \
                    cur.execute('SELECT MAX(count_id) FROM references_ WHERE' +
                                f' user_id =="{message.from_user.id}"').fetchone()[0]
                if not count_1:
                    count_1 = 0
                count_1 += 1
                cur.execute("INSERT INTO references_ (id, photos, email_phone_no, reason, to_whom, user_id, count_id)"
                            " VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (count, data_1[1], message.text, data_1[3], data_1[4], message.from_user.id, count_1))
                cur.execute(f"DELETE FROM template_references WHERE id == '{data}'")
                cur.execute(f"UPDATE users SET template_references_id=0, step=0 WHERE id == '{message.from_user.id}'")
                con.commit()
                await bot.send_message(message.from_user.id, 'Спасибо! Мы взяли ваше обращение в работу.',
                                       reply_markup=start_keys_1)
                message = [count, data_1[1], message.text, data_1[3], data_1[4], message.from_user.id]
                data = cur.execute(f"SELECT * FROM chat_ids").fetchall()
                for _id in data:
                    text = 'Просил уведомить через телеграм: ' + message[2]
                    try:
                        if message[1]:
                            if message[1][0] == ' ':
                                message[1] = message[1][1:]
                            if len(message[1].split()) == 1:
                                await bot.send_photo(_id[0], message[1],
                                                     caption=f'id обращения: # {message[-1]}_{count_1}\n' +
                                                             f'Кому направлено обращение: {message[4]}\n' +
                                                             f' Причина обращения: {message[3]}\n{text}',
                                                     reply_markup=ReplyKeyboardRemove())
                            else:
                                media = [InputMediaPhoto(message[1].split()[0],
                                                         f'id обращения: # {message[-1]}_{count_1}\nКому направлено ' +
                                                         f'обращение: {message[4]}' +
                                                         f'\nПричина обращения: {message[3]}\n{text}')]
                                for photo_id in message[1].split()[1:]:
                                    media.append(InputMediaPhoto(photo_id))
                                mess = await bot.send_media_group(_id[0], media)
                                cur.execute(f"UPDATE references_ SET media_group_id={mess[0].media_group_id}" +
                                            f" WHERE id == {count}")
                                con.commit()
                        else:
                            await bot.send_message(_id[0],
                                                   f'id обращения: # {message[-1]}_{count_1}\nКому направлено обращен' +
                                                   f'ие: {message[4]}\n' +
                                                   f'Причина обращения: {message[3]}\n{text}',
                                                   reply_markup=ReplyKeyboardRemove())
                    except Exception as e:
                        print(e)
                        continue
                return
    if 'chat' in message:
        _id = message.chat.id
    else:
        _id = message.from_user.id
    await bot.send_message(_id, 'Не понял команду')


# Functions for Yandex.Cloud
async def register_handlers(dp: Dispatcher):
    """Registration all handlers before processing update."""

    dp.register_message_handler(start_mess, commands=['start'])
    dp.register_message_handler(reserve_save, commands=['reserve_save'])
    dp.register_message_handler(add_to_mailing_list_mess, commands=['add_to_mailing_list'])
    dp.register_message_handler(get_all_requests_mess, commands=['get_all_requests'])
    dp.register_message_handler(handle_docs_photo, content_types=['photo'])
    dp.register_message_handler(echo)


async def process_event(event, dp: Dispatcher):
    """
    Converting an Yandex.Cloud functions event to an update and
    handling tha update.
    """

    update = json.loads(event['body'])

    Bot.set_current(dp.bot)
    update = types.Update.to_object(update)
    await dp.process_update(update)


async def handler(event, context):
    """Yandex.Cloud functions handler."""

    if event['httpMethod'] == 'POST':
        await register_handlers(dp_official)
        await process_event(event, dp_official)

        return {'statusCode': 200, 'body': 'ok'}
    return {'statusCode': 405}
