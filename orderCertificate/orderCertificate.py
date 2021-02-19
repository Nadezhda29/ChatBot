from loader import bot
from telebot import types
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

from connectDB import conn_str

import pyodbc

global typeCertificate
global clientID
global quantityCertificate
global deliveryMethod


# обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def send_services(message: Message):
    if message.text == "Выбрать услугу":
        global clientID
        clientID = int(message.from_user.id)

        button_order_certificate = InlineKeyboardButton(text="Заказ справки", callback_data="orderCertificate")
        button_reg_doc = InlineKeyboardButton(text="Оформление документов", callback_data="regDoc")
        button_give_review = InlineKeyboardButton(text="Оставить отзыв", callback_data="giveReview")
        button_ask_question = InlineKeyboardButton(text="Задать вопрос", callback_data="askQuestion")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_order_certificate, button_reg_doc,
                                                                button_give_review, button_ask_question)

        bot.send_message(message.from_user.id, f"Выберите услугу из списка: ", reply_markup=inline_keyboard)


# обработчик callback-функции orderCertificate
@bot.callback_query_handler(func=lambda c: c.data == "orderCertificate")
def send_types_certificate(message: Message):
    button_is_student = InlineKeyboardButton(text='Справка "Действительно является студентом"',
                                             callback_data="isStudent")
    button_place_request = InlineKeyboardButton(text="Справки по месту требования", callback_data="placeRequest")
    button_certificate_call = InlineKeyboardButton(text="Справка-вызов", callback_data="helpCertificate")

    inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_is_student, button_place_request,
                                                            button_certificate_call)
    bot.send_message(message.from_user.id, f"Какую справку вы хотите заказать?", reply_markup=inline_keyboard)


# обработчик callback-функции isStudent
@bot.callback_query_handler(func=lambda c: c.data == "isStudent")
def request_fio(message: Message):
    global typeCertificate
    typeCertificate = 'Справка "Действительно является студентом"'
    button1 = InlineKeyboardButton(text="1", callback_data="1")
    button2 = InlineKeyboardButton(text="2", callback_data="2")
    button3 = InlineKeyboardButton(text="3", callback_data="3")
    button4 = InlineKeyboardButton(text="4", callback_data="4")

    inline_keyboard = InlineKeyboardMarkup(row_width=4).add(button1, button2, button3, button4)
    bot.send_message(message.from_user.id, f"Выберите количество справок: ", reply_markup=inline_keyboard)


# обработчик callback-функции quantity
@bot.callback_query_handler(func=lambda c: c.data == "1" or c.data == "2" or c.data == "3" or c.data == "4")
def req_delivery_meth(c: CallbackQuery):
    global quantityCertificate
    if c.data == '1':
        quantityCertificate = 1
    elif c.data == '2':
        quantityCertificate = 2
    elif c.data == '3':
        quantityCertificate = 3
    else:
        quantityCertificate = 4

    button_take = InlineKeyboardButton(text="Забрать лично в ИЦ", callback_data="take_ic")
    button_send = InlineKeyboardButton(text="Отправить на E-mail", callback_data="send")
    button_take_send = InlineKeyboardButton(text="Забрать в ИЦ и отправить на E-mail", callback_data="take_send")

    inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_take, button_send, button_take_send)

    bot.send_message(c.from_user.id, f"Выберите способ доставки:", reply_markup=inline_keyboard)


# обработчик callback-функции deliveryMeth
@bot.callback_query_handler(func=lambda c: c.data == "take_ic" or c.data == "send" or c.data == "take_send")
def request(c: CallbackQuery):
    global deliveryMethod
    global clientID
    if c.data == "take_ic":
        deliveryMethod = "Забрать лично в ИЦ"
    elif c.data == "send":
        deliveryMethod = "Отправить на E-mail"
    else:
        deliveryMethod = "Забрать в ИЦ и отправить на E-mail"

    send = bot.send_message(c.from_user.id, f"Ваша заявка принята в работу. Вам будет отправлено письмо на"
                                            f" электронную почту о готовности справки.")

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute(f"select FullName, Course, StudentGroup, FormStudy, LevelStudy, Faculty, Direction, NumberGradebook,"
                   f" Phone, Email"
                   f" from DataStudents"
                   f" where ID = {clientID}")
    data_user = tuple(cursor.fetchone())
    conn.close()

    keys = ("ФИО", "Курс", "Группа", "Форма обучения", "Уровень образование", "Факультет", "Направление подготовки",
            "Специальность", "Номер зачетной книжки", "Телефон", "E-mail")
    users = dict(zip(keys, data_user))
    users["Тип справки"] = typeCertificate
    users["Количество справок"] = quantityCertificate
    users["Способ доставки"] = deliveryMethod

    with open("data_file.txt", "w", encoding='utf-8') as write_file:
        for key, val in users.items():
            write_file.write('{}:{}\n'.format(key, val))

    subject = "Новая заявка"
    body = "Поступила новая заявка"
    sender_email = "nadegda9966n@gmail.com"
    receiver_email = "99nadegda99@mail.ru"
    password = "D!Winchester1"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Внесение тела письма
    message.attach(MIMEText(body, "plain"))

    filename = "data_file.txt"  # В той же папке что и код

    #Открытие файла в бинарном режиме
    with open(filename, "rb") as attachment:
    # Заголовок письма application/octet-stream
    # Почтовый клиент обычно может загрузить это автоматически в виде вложения
        part = MIMEBase("application", "octet-stream")
        print(part.set_payload(attachment.read()))

    # Шифровка файла под ASCII символы для отправки по почте
    encoders.encode_base64(part)

    # Внесение заголовка в виде пара/ключ к части вложения
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}")

    # Внесение вложения в сообщение и конвертация сообщения в строку
    message.attach(part)
    text = message

    # Подключение к серверу при помощи безопасного контекста и отправка письма
    # context = ssl.create_default_context()
    # with smtplib.SMTP_SSL("smtp.gmail.com", context=context) as server:
    #     server.login(sender_email, password)
    #     print("hfj")
    #     server.sendmail(sender_email, receiver_email, text)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    # подключиться к SMTP-серверу в режиме TLS (безопасный) и отправить EHLO
    server.starttls()
    # войти в учетную запись, используя учетные данные
    server.login(sender_email, password)
    # отправить электронное письмо
    server.sendmail(sender_email, receiver_email, text.as_string())
    # завершить сеанс SMTP
    server.quit()

    print("должно отправиться")
