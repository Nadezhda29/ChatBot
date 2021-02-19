from loader import bot
from telebot import types
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import pyodbc
import re
from connectDB import conn_str
from loader import create_keyboard

global clientID
global fullName
global course
global group
global formOfStudy
global levelOfStudy
global addition
addition = None
global faculty
global direction
direction = None
global specialization
specialization = None
global numberGradebook
global phone
global e_mail


# обработчик команд "start" и "help"
@bot.message_handler(commands=['start', 'help'])
def start_request(message: Message):
    global clientID
    clientID = message.from_user.id
    send = bot.send_message(message.from_user.id, f'Привет! Я чат-бот Информационного центра НГУЭУ.'
                                                  f' Для начала работы необходимо будет ввести данные.'
                                                  f' Введите ФИО:')
    bot.register_next_step_handler(send, request_phone)


def request_phone(message: Message):
    string = r'[А-Я][а-я]*\s[А-Я][а-я]*\s[А-Я][а-я]*'
    match = re.search(string, message.text)
    if match:
        global fullName
        fullName = message.text
        send = bot.send_message(message.from_user.id, f"Введите номер телефона в формате 79*********:")
        bot.register_next_step_handler(send, request_email)
    else:
        send = bot.send_message(message.from_user.id, f"ФИО введено некорректно. Повторите попытку.")
        bot.register_next_step_handler(send, request_phone)


def request_email(message: Message):
    string = r'[7]\d{10}'
    match = re.search(string, message.text)
    if match:
        global phone
        phone = message.text
        send = bot.send_message(message.from_user.id, f"Введите ваш e-mail:")
        bot.register_next_step_handler(send, request_cource)
    else:
        send = bot.send_message(message.from_user.id, f"Пожалуйста, введите корректный номер телефона.")
        bot.register_next_step_handler(send, request_email)


def request_cource(message: Message):
    string = r'(^|\s)[-a-zA-Z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)'
    match = re.search(string, message.text)
    if match:
        global e_mail
        e_mail = message.text
        send = bot.send_message(message.from_user.id, f"Введите курс:")
        bot.register_next_step_handler(send, req_num_gradebook)
    else:
        send = bot.send_message(message.from_user.id, f"Пожалуйста, введите корректный E-mail.")
        bot.register_next_step_handler(send, request_cource)


def req_num_gradebook(message: Message):
    string = r'[1-8]{1}'
    match = re.search(string, message.text)
    if match:
        global course
        course = int(message.text)

        send = bot.send_message(message.from_user.id, f"Введите номер зачетной книжки:")
        bot.register_next_step_handler(send, request_group)
    else:
        send = bot.send_message(message.from_user.id, f"Курс введен некорректно. Введите, пожалуйста еще раз.")
        bot.register_next_step_handler(send, req_num_gradebook)


def request_group(message: Message):
    string = r'\d{6}'
    match = re.search(string, message.text)
    if match:
        global numberGradebook
        numberGradebook = int(message.text)

        send = bot.send_message(message.from_user.id, f"Введите название группы:")
        bot.register_next_step_handler(send, req_form_of_study)
    else:
        send = bot.send_message(message.from_user.id, f"Номер зачетной книжки должен состоять из 6 цифр.")
        bot.register_next_step_handler(send, request_group)


def req_form_of_study(message: Message):
    global group
    group = message.text
    button_full_time = InlineKeyboardButton(text="Очная", callback_data="full_time")
    button_distance = InlineKeyboardButton(text="Заочная", callback_data="distance")
    button_part_time = InlineKeyboardButton(text="Очно-заочная", callback_data="part_time")

    inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_full_time, button_distance, button_part_time)

    bot.send_message(message.from_user.id, f"Выберите форму обучения: ", reply_markup=inline_keyboard)


# обработчик callback-функции levelOfStudy
@bot.callback_query_handler(func=lambda c: c.data == "spo" or c.data == "bachelor" or c.data == "specialist" or
                            c.data == "master" or c.data == "graduate")
def req_faculty(c: CallbackQuery):
    global levelOfStudy
    global faculty

    if c.data == "spo":
        button_11 = InlineKeyboardButton(text="На базе среднего общего образования", callback_data="11 class")
        button_9 = InlineKeyboardButton(text="На базе основного общего образования", callback_data="9 class")
        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_9, button_11)
        bot.send_message(c.from_user.id, f"Вы проходите обучение на базе 11 или 9 классов? Выберите.",
                         reply_markup=inline_keyboard)
        levelOfStudy = 'СПО'
    elif c.data == "bachelor":
        levelOfStudy = 'Бакалавриат'
        button_economy = InlineKeyboardButton(text="ФКЭиП", callback_data="faculty_economy")
        button_state_sector = InlineKeyboardButton(text="ФГС", callback_data="state_sector")
        button_legal = InlineKeyboardButton(text="ЮФ", callback_data="legal")
        inline_keyboard = InlineKeyboardMarkup(row_width=2).add(button_economy, button_state_sector, button_legal)
    elif c.data == "specialist":
        levelOfStudy = 'Специалитет'
        button_state_sector = InlineKeyboardButton(text="ФГС", callback_data="state_sector")
        button_legal = InlineKeyboardButton(text="ЮФ", callback_data="legal")
        inline_keyboard = InlineKeyboardMarkup(row_width=2).add(button_state_sector, button_legal)
    elif c.data == "master":
        levelOfStudy = 'Магистратура'
        button_economy = InlineKeyboardButton(text="ФКЭиП", callback_data="faculty_economy")
        button_state_sector = InlineKeyboardButton(text="ФГС", callback_data="state_sector")
        button_legal = InlineKeyboardButton(text="ЮФ", callback_data="legal")
        inline_keyboard = InlineKeyboardMarkup(row_width=2).add(button_economy, button_state_sector, button_legal)
    elif c.data == "graduate":
        levelOfStudy = 'Аспирантура'
        button_economy = InlineKeyboardButton(text="ФКЭиП", callback_data="faculty_economy")
        button_state_sector = InlineKeyboardButton(text="ФГС", callback_data="state_sector")
        inline_keyboard = InlineKeyboardMarkup(row_width=2).add(button_economy, button_state_sector)

    if (course == 1 or course == 2) and (c.data == "spo" or c.data == "bachelor" or c.data == "specialist"):
        faculty = "ФБП"
        bot.send_message(c.from_user.id, f"Ваш факультет ФБП: ")
        req_specialization(c)

    bot.send_message(c.from_user.id, f"Выберите факультет: ", reply_markup=inline_keyboard)


# обработчик callback-функции levelOfStudy
@bot.callback_query_handler(func=lambda c: c.data == "11 class" or c.data == "9 class")
def req_faculty(c: CallbackQuery):
    global addition
    if c.data == "11 class":
        addition = "На базе среднего общего образования"
    else:
        addition = "На базе основного общего образования"

    button_economy = InlineKeyboardButton(text="ФКЭиП", callback_data="faculty_economy")
    button_state_sector = InlineKeyboardButton(text="ФГС", callback_data="state_sector")
    inline_keyboard = InlineKeyboardMarkup(row_width=2).add(button_economy, button_state_sector)
    bot.send_message(c.from_user.id, f"Выберите факультет: ", reply_markup=inline_keyboard)


# обработчик callback-функции form_of_study
@bot.callback_query_handler(func=lambda c: c.data == "full_time" or c.data == "distance" or c.data == "part_time")
def req_form_study(c: CallbackQuery):
    global formOfStudy
    if c.data == "full_time":
        formOfStudy = "Очная"
    elif c.data == "distance":
        formOfStudy = "Заочная"
    elif c.data == "part_time":
        formOfStudy = "Очно-заочная"

    if formOfStudy == "Очная" or formOfStudy == "Заочная":
        button_spo = InlineKeyboardButton(text="СПО", callback_data="spo")
        button_bachelor = InlineKeyboardButton(text="Бакалавриат", callback_data="bachelor")
        button_specialist = InlineKeyboardButton(text="Специалитет", callback_data="specialist")
        button_master = InlineKeyboardButton(text="Магистратура", callback_data="master")
        button_graduate = InlineKeyboardButton(text="Аспирантура", callback_data="graduate")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_spo, button_bachelor, button_specialist,
                                                                button_master, button_graduate)
    if formOfStudy == "Очно-заочная":
        button_bachelor = InlineKeyboardButton(text="Бакалавриат", callback_data="bachelor")
        button_specialist = InlineKeyboardButton(text="Специалитет", callback_data="specialist")
        button_master = InlineKeyboardButton(text="Магистратура", callback_data="master")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_bachelor, button_specialist, button_master)

    bot.send_message(c.from_user.id, f"Выберите уровень образования: ", reply_markup=inline_keyboard)


# обработчик callback-функции faculty
@bot.callback_query_handler(func=lambda c: c.data == "faculty_economy" or c.data == "state_sector" or c.data == "legal")
def req_specialization(c: CallbackQuery):
    global faculty
    global levelOfStudy
    if c.data == "faculty_economy":
        faculty = "ФКЭиП"

        if levelOfStudy == "СПО":
            if formOfStudy == "Очная":
                button_economy_account = InlineKeyboardButton(text="38.02.01 Экономика и бухгалтерский учет",
                                                              callback_data="economyAccounting")
                button_insurance = InlineKeyboardButton(text="38.02.02 Страховое дело", callback_data="insurance")
                button_logistics = InlineKeyboardButton(text="38.02.03 Операционная деятельность в логистике",
                                                        callback_data="logistics")
                button_finance = InlineKeyboardButton(text="38.02.06 Финансы", callback_data="finance")
                button_banking = InlineKeyboardButton(text="38.02.07 Банковское дело", callback_data="banking")
                button_tourism = InlineKeyboardButton(text="43.02.10 Туризм", callback_data="tourismSPO")
                button_hotel_business = InlineKeyboardButton(text="43.02.14 Гостиничное дело",
                                                             callback_data="hotelBusinessSPO")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy_account, button_insurance,
                                                                        button_logistics, button_finance, button_banking,
                                                                        button_tourism, button_hotel_business)

            elif formOfStudy == "Заочная" and addition == "На базе основного общего образования":
                button_economy_account = InlineKeyboardButton(text="38.02.01 Экономика и бухгалтерский учет",
                                                              callback_data="economyAccounting")
                button_logistics = InlineKeyboardButton(text="38.02.03 Операционная деятельность в логистике",
                                                        callback_data="logistics")
                button_finance = InlineKeyboardButton(text="38.02.06 Финансы", callback_data="finance")
                button_tourism = InlineKeyboardButton(text="43.02.10 Туризм", callback_data="tourismSPO")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy_account, button_logistics,
                                                                        button_finance, button_tourism)

            elif formOfStudy == "Заочная" and addition == "На базе среднего общего образования":
                button_economy_account = InlineKeyboardButton(text="38.02.01 Экономика и бухгалтерский учет",
                                                              callback_data="economyAccounting")
                button_insurance = InlineKeyboardButton(text="38.02.02 Страховое дело", callback_data="insurance")
                button_logistics = InlineKeyboardButton(text="38.02.03 Операционная деятельность в логистике",
                                                        callback_data="logistics")
                button_finance = InlineKeyboardButton(text="38.02.06 Финансы", callback_data="finance")
                button_banking = InlineKeyboardButton(text="38.02.07 Банковское дело", callback_data="banking")
                button_tourism = InlineKeyboardButton(text="43.02.10 Туризм", callback_data="tourismSPO")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy_account, button_insurance,
                                                                        button_logistics, button_finance,
                                                                        button_banking, button_tourism)

            bot.send_message(c.from_user.id, "Выберите специальность: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Бакалавриат":
            if formOfStudy == "Очная":
                button_economy = InlineKeyboardButton(text="38.03.01 Экономика", callback_data="economy")
                button_management = InlineKeyboardButton(text="38.03.02 Менеджмент", callback_data="management")
                button_person_management = InlineKeyboardButton(text="38.03.03 Управление персоналом",
                                                                callback_data="personManagement")
                button_advert = InlineKeyboardButton(text="42.03.01  Реклама и связи с общественностью",
                                                     callback_data="advert")
                button_service = InlineKeyboardButton(text="38.02.07 Сервис", callback_data="service")
                button_tourism = InlineKeyboardButton(text="43.03.02 Туризм", callback_data="tourismBachelor")
                button_hotel_business = InlineKeyboardButton(text="43.03.03 Гостиничное дело",
                                                             callback_data="hotelBusiness")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy, button_management,
                                                                        button_person_management, button_advert,
                                                                        button_service, button_tourism,
                                                                        button_hotel_business)

            elif formOfStudy == "Очно-заочная":
                button_economy = InlineKeyboardButton(text="38.03.01 Экономика", callback_data="economy")
                button_management = InlineKeyboardButton(text="38.03.02 Менеджмент", callback_data="management")
                button_person_management = InlineKeyboardButton(text="38.03.03 Управление персоналом",
                                                                callback_data="personManagement")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy, button_management,
                                                                        button_person_management)
            else:
                button_advert = InlineKeyboardButton(text="42.03.01  Реклама и связи с общественностью",
                                                     callback_data="advert")
                button_service = InlineKeyboardButton(text="38.02.07 Сервис", callback_data="service")
                button_tourism = InlineKeyboardButton(text="43.03.02 Туризм", callback_data="tourismBachelor")
                button_hotel_business = InlineKeyboardButton(text="43.03.03 Гостиничное дело",
                                                             callback_data="hotelBusiness")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_advert, button_service, button_tourism,
                                                                        button_hotel_business)

            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Магистратура":
            if formOfStudy == "Очная" or formOfStudy == "Заочная":
                button_economy = InlineKeyboardButton(text="38.04.01 Экономика", callback_data="economyMaster")
                button_management = InlineKeyboardButton(text="38.04.02 Менеджмент", callback_data="managementMaster")
                button_person_management = InlineKeyboardButton(text="38.04.03 Управление персоналом",
                                                                callback_data="personManagementMaster")
                button_finance_credit = InlineKeyboardButton(text="38.04.08 Финансы и кредит",
                                                             callback_data="financeCredit")
                button_advert = InlineKeyboardButton(text="42.04.01  Реклама и связи с общественностью",
                                                     callback_data="advertMaster")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy, button_management,
                                                                        button_person_management, button_finance_credit,
                                                                        button_advert)
            else:
                button_economy = InlineKeyboardButton(text="38.04.01 Экономика", callback_data="economyMaster")
                button_management = InlineKeyboardButton(text="38.04.02 Менеджмент", callback_data="managementMaster")
                button_finance_credit = InlineKeyboardButton(text="38.04.08 Финансы и кредит",
                                                             callback_data="financeCredit")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy, button_management,
                                                                        button_finance_credit)

            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Аспирантура":
            button_economy = InlineKeyboardButton(text="38.06.01 Экономика", callback_data="economyGraduate")
            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy)
            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

    elif c.data == "state_sector":
        faculty = "ФГС"
        if levelOfStudy == "СПО":
            if formOfStudy == "Очная":
                button_informatics = InlineKeyboardButton(text="09.02.05 Прикладная информатика",
                                                          callback_data="informaticsSPO")
                button_land_property_relation = InlineKeyboardButton(text="21.02.05 Земельно-имущественные отношения",
                                                                     callback_data="landPropertyRelation")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_informatics,
                                                                        button_land_property_relation)

            elif formOfStudy == "Заочная":
                button_land_property_relation = InlineKeyboardButton(text="21.02.05 Земельно-имущественные отношения",
                                                                     callback_data="landPropertyRelation")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_land_property_relation)

            bot.send_message(c.from_user.id, "Выберите специальность: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Бакалавриат":
            if formOfStudy == "Очная":
                button_fundamental_informatic = InlineKeyboardButton(text="02.03.02 Фундаментальная информатика и"
                                                                          " информационные технологии",
                                                                     callback_data="fundamentalInformatic")
                button_ecology = InlineKeyboardButton(text="05.03.06 Экология и природопользование",
                                                      callback_data="ecology")
                button_ic_technology = InlineKeyboardButton(text="09.03.02 Информационные системы и технологии",
                                                            callback_data="icTechnology")
                button_informatics = InlineKeyboardButton(text="09.03.03 Прикладная информатика",
                                                          callback_data="informatics")
                button_innovation = InlineKeyboardButton(text="27.03.05 Инноватика", callback_data="innovation")
                button_economy = InlineKeyboardButton(text="38.03.01 Экономика", callback_data="economyStateSector")
                button_state_management = InlineKeyboardButton(text="38.03.04 Государственное и муниципальное"
                                                                    " управление", callback_data="stateManagement")
                button_business_informatic = InlineKeyboardButton(text="38.03.05 Бизнес-информатика",
                                                                  callback_data="businessInformatic")
                button_sociology = InlineKeyboardButton(text="39.03.01 Социология", callback_data="sociology")
                button_region = InlineKeyboardButton(text="41.03.01 Зарубежное регионоведение", callback_data="region")
                button_international_relation = InlineKeyboardButton(text="41.03.05 Международные отношения",
                                                                     callback_data="internationalRelation")
                button_housing_management = InlineKeyboardButton(text="38.03.10 Жилищное хозяйство и коммунальная"
                                                                      " инфраструктура",
                                                                 callback_data="housingManagement")
                button_statistics = InlineKeyboardButton(text="01.03.05 Статистика", callback_data="statistics")
                button_political_science = InlineKeyboardButton(text="41.03.04 Политология",
                                                                callback_data="politicalScience")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_fundamental_informatic, button_ecology,
                                                                        button_ic_technology, button_informatics,
                                                                        button_innovation, button_economy,
                                                                        button_state_management,
                                                                        button_business_informatic, button_sociology,
                                                                        button_region, button_international_relation,
                                                                        button_housing_management, button_statistics,
                                                                        button_political_science)
            elif formOfStudy == "Заочная":
                button_ecology = InlineKeyboardButton(text="05.03.06 Экология и природопользование",
                                                      callback_data="ecology")
                button_informatics = InlineKeyboardButton(text="09.03.03 Прикладная информатика",
                                                          callback_data="informatics")
                button_sociology = InlineKeyboardButton(text="39.03.01 Социология", callback_data="sociology")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_ecology, button_informatics,
                                                                        button_sociology)
            else:
                button_economy = InlineKeyboardButton(text="38.03.01 Экономика", callback_data="economyStateSector")
                button_state_management = InlineKeyboardButton(text="38.03.04 Государственное и муниципальное"
                                                                    " управление", callback_data="stateManagement")
                button_business_informatic = InlineKeyboardButton(text="38.03.05 Бизнес-информатика",
                                                                  callback_data="businessInformatic")
                button_housing_management = InlineKeyboardButton(text="38.03.10 Жилищное хозяйство и коммунальная"
                                                                      " инфраструктура",
                                                                 callback_data="housingManagement")
                button_psyсhology = InlineKeyboardButton(text="37.03.01 Психология", callback_data="psyсhology")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy, button_state_management,
                                                                        button_business_informatic,
                                                                        button_housing_management, button_psyсhology)

            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Специалитет":
            if formOfStudy == "Очная":
                button_psyсhology = InlineKeyboardButton(text="37.05.02 Психология служебной деятельности",
                                                         callback_data="psyсhologySpecialist")
                button_economy_security = InlineKeyboardButton(text="38.05.01 Экономическая безопасность",
                                                               callback_data="economySecurity")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_psyсhology, button_economy_security)

            elif formOfStudy == "Заочная":
                button_economy_security = InlineKeyboardButton(text="38.05.01 Экономическая безопасность",
                                                               callback_data="economySecurity")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy_security)

            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Магистратура":
            if formOfStudy == "Очная":
                button_ic_technology = InlineKeyboardButton(text="09.04.02 Информационные системы и технологии",
                                                            callback_data="icTechnologyMaster")
                button_innovation = InlineKeyboardButton(text="27.04.05 Инноватика", callback_data="innovationMaster")
                button_psyсhology = InlineKeyboardButton(text="37.04.01 Психология", callback_data="psyсhologyMaster")
                button_economy = InlineKeyboardButton(text="38.04.01 Экономика",
                                                      callback_data="economyStateSectorMaster")
                button_state_management = InlineKeyboardButton(text="38.04.04 Государственное и муниципальное"
                                                                    " управление",
                                                               callback_data="stateManagementMaster")
                button_business_informatic = InlineKeyboardButton(text="38.04.05 Бизнес-информатика",
                                                                  callback_data="businessInformaticMaster")
                button_finance_credit = InlineKeyboardButton(text="38.04.08 Финансы и кредит",
                                                             callback_data="financeCreditStateSector")
                button_sociology = InlineKeyboardButton(text="39.04.01 Социология", callback_data="sociologyMaster")
                button_region = InlineKeyboardButton(text="41.04.01 Зарубежное регионоведение",
                                                     callback_data="regionMaster")
                button_international_relation = InlineKeyboardButton(text="41.03.05 Международные отношения",
                                                                     callback_data="internationalRelationMaster")
                button_housing_management = InlineKeyboardButton(text="38.04.10 Жилищное хозяйство и коммунальная"
                                                                      " инфраструктура",
                                                                 callback_data="housingManagementMaster")
                button_statistics = InlineKeyboardButton(text="01.04.05 Статистика", callback_data="statiscMaster")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_ic_technology, button_innovation,
                                                                        button_psyсhology, button_economy,
                                                                        button_state_management,
                                                                        button_business_informatic,
                                                                        button_finance_credit, button_sociology,
                                                                        button_region, button_international_relation,
                                                                        button_housing_management, button_statistics)

            elif formOfStudy == "Заочная":
                button_innovation = InlineKeyboardButton(text="27.04.05 Инноватика", callback_data="innovationMaster")
                button_economy = InlineKeyboardButton(text="38.04.01 Экономика",
                                                      callback_data="economyStateSectorMaster")
                button_state_management = InlineKeyboardButton(text="38.04.04 Государственное и муниципальное"
                                                                    " управление",
                                                               callback_data="stateManagementMaster")
                button_business_informatic = InlineKeyboardButton(text="38.04.05 Бизнес-информатика",
                                                                  callback_data="businessInformaticMaster")
                button_finance_credit = InlineKeyboardButton(text="38.04.08 Финансы и кредит",
                                                             callback_data="financeCreditStateSector")
                button_sociology = InlineKeyboardButton(text="39.04.01 Социология", callback_data="sociologyMaster")
                button_housing_management = InlineKeyboardButton(text="38.04.10 Жилищное хозяйство и коммунальная"
                                                                      " инфраструктура",
                                                                 callback_data="housingManagementMaster")
                button_informatics = InlineKeyboardButton(text="09.04.03 Прикладная информатика",
                                                          callback_data="informaticsMaster")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_innovation, button_economy,
                                                                        button_state_management,
                                                                        button_business_informatic,
                                                                        button_finance_credit, button_sociology,
                                                                        button_housing_management, button_informatics)

            else:
                button_economy = InlineKeyboardButton(text="38.04.01 Экономика",
                                                      callback_data="economyStateSectorMaster")
                button_finance_credit = InlineKeyboardButton(text="38.04.08 Финансы и кредит",
                                                             callback_data="financeCreditStateSector")
                button_psyсhology = InlineKeyboardButton(text="37.04.01 Психология", callback_data="psyсhologyMaster")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy, button_finance_credit,
                                                                        button_psyсhology)

            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Аспирантура":
            if formOfStudy == "Очная":
                button_informatic_computer_tech = InlineKeyboardButton(text="09.06.01 Информатика и вычислительная"
                                                                            " техника",
                                                                       callback_data="informaticComputerTech")
                button_psyсhology = InlineKeyboardButton(text="37.06.01 Психологические науки",
                                                         callback_data="psyсhologyGraduate")
                button_economy = InlineKeyboardButton(text="38.06.01 Экономика",
                                                      callback_data="economyStateSectorGraduate")
                button_sociology = InlineKeyboardButton(text="39.06.01 Cоциологические науки",
                                                        callback_data="sociologyGraduate")
                button_historical_science = InlineKeyboardButton(text="46.06.01 Исторические науки и археология",
                                                                 callback_data="historicalScience")
                button_philosophy = InlineKeyboardButton(text="47.06.01 Философия, этика и религиоведение",
                                                         callback_data="philosophy")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_informatic_computer_tech,
                                                                        button_psyсhology, button_economy,
                                                                        button_sociology, button_historical_science,
                                                                        button_philosophy)

            elif formOfStudy == "Заочная":
                button_informatic_computer_tech = InlineKeyboardButton(text="09.06.01 Информатика и вычислительная"
                                                                            " техника",
                                                                       callback_data="informaticComputerTech")
                button_psyсhology = InlineKeyboardButton(text="37.06.01 Психологические науки",
                                                         callback_data="psyсhologyGraduate")
                button_economy = InlineKeyboardButton(text="38.06.01 Экономика",
                                                      callback_data="economyStateSectorGraduate")
                button_sociology = InlineKeyboardButton(text="39.06.01 Cоциологические науки",
                                                        callback_data="sociologyGraduate")
                button_philosophy = InlineKeyboardButton(text="47.06.01 Философия, этика и религиоведение",
                                                         callback_data="philosophy")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_informatic_computer_tech,
                                                                        button_psyсhology, button_economy,
                                                                        button_sociology, button_philosophy)

            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

    else:
        faculty = "ЮФ"

        if levelOfStudy == "Бакалавриат":
            button_law = InlineKeyboardButton(text="40.03.01 Юриспруденция", callback_data="law")

            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_law)
            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Специалитет":
            if formOfStudy == "Очная" or formOfStudy == "Заочная":
                button_legal_support = InlineKeyboardButton(text="40.05.01 Правовое обеспечение национальной"
                                                                 " безопасности", callback_data="legalSupport")
                button_law_enforcement = InlineKeyboardButton(text="40.05.02 Правоохранительная деятельность",
                                                              callback_data="lawEnforcement")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_legal_support, button_law_enforcement)

            else:
                button_law_enforcement = InlineKeyboardButton(text="40.05.02 Правоохранительная деятельность",
                                                              callback_data="lawEnforcement")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_law_enforcement)

            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Магистратура":
            button_law = InlineKeyboardButton(text="40.04.01 Юриспруденция", callback_data="lawMaster")

            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_law)
            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)

    if faculty == "ФБП":
        if levelOfStudy == "СПО":
            if formOfStudy == "Очная":
                button_economy_account = InlineKeyboardButton(text="38.02.01 Экономика и бухгалтерский учет",
                                                              callback_data="economyAccounting")
                button_insurance = InlineKeyboardButton(text="38.02.02 Страховое дело", callback_data="insurance")
                button_logistics = InlineKeyboardButton(text="38.02.03 Операционная деятельность в логистике",
                                                        callback_data="logistics")
                button_finance = InlineKeyboardButton(text="38.02.06 Финансы", callback_data="finance")
                button_banking = InlineKeyboardButton(text="38.02.07 Банковское дело", callback_data="banking")
                button_tourism = InlineKeyboardButton(text="43.02.10 Туризм", callback_data="tourismSPO")
                button_informatics = InlineKeyboardButton(text="09.02.05 Прикладная информатика",
                                                          callback_data="informaticsSPO")
                button_land_property_relation = InlineKeyboardButton(text="21.02.05 Земельно-имущественные отношения",
                                                                     callback_data="landPropertyRelation")
                button_hotel_business = InlineKeyboardButton(text="43.02.14 Гостиничное дело",
                                                             callback_data="hotelBusinessSPO")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy_account, button_insurance,
                                                                        button_logistics, button_finance, button_banking,
                                                                        button_tourism, button_informatics,
                                                                        button_land_property_relation,
                                                                        button_hotel_business)

            elif formOfStudy == "Заочная" and addition == "На базе основного общего образования":
                button_economy_account = InlineKeyboardButton(text="38.02.01 Экономика и бухгалтерский учет",
                                                              callback_data="economyAccounting")
                button_logistics = InlineKeyboardButton(text="38.02.03 Операционная деятельность в логистике",
                                                        callback_data="logistics")
                button_finance = InlineKeyboardButton(text="38.02.06 Финансы", callback_data="finance")
                button_tourism = InlineKeyboardButton(text="43.02.10 Туризм", callback_data="tourismSPO")
                button_land_property_relation = InlineKeyboardButton(text="21.02.05 Земельно-имущественные отношения",
                                                                     callback_data="landPropertyRelation")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy_account, button_logistics,
                                                                        button_finance, button_tourism,
                                                                        button_land_property_relation)

            elif formOfStudy == "Заочная" and addition == "На базе среднего общего образования":
                button_economy_account = InlineKeyboardButton(text="38.02.01 Экономика и бухгалтерский учет",
                                                              callback_data="economyAccounting")
                button_insurance = InlineKeyboardButton(text="38.02.02 Страховое дело", callback_data="insurance")
                button_logistics = InlineKeyboardButton(text="38.02.03 Операционная деятельность в логистике",
                                                        callback_data="logistics")
                button_finance = InlineKeyboardButton(text="38.02.06 Финансы", callback_data="finance")
                button_banking = InlineKeyboardButton(text="38.02.07 Банковское дело", callback_data="banking")
                button_tourism = InlineKeyboardButton(text="43.02.10 Туризм", callback_data="tourismSPO")
                button_land_property_relation = InlineKeyboardButton(text="21.02.05 Земельно-имущественные отношения",
                                                                     callback_data="landPropertyRelation")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy_account, button_insurance,
                                                                        button_logistics, button_finance,
                                                                        button_banking, button_tourism,
                                                                        button_land_property_relation)

            bot.send_message(c.from_user.id, "Выберите специальность: ", reply_markup=inline_keyboard)

        elif levelOfStudy == "Балавриат":
            if formOfStudy == "Очная":
                button_economy = InlineKeyboardButton(text="38.03.01 Экономика", callback_data="economy")
                button_management = InlineKeyboardButton(text="38.03.02 Менеджмент", callback_data="management")
                button_person_management = InlineKeyboardButton(text="38.03.03 Управление персоналом",
                                                                callback_data="personManagement")
                button_advert = InlineKeyboardButton(text="42.03.01  Реклама и связи с общественностью",
                                                     callback_data="advert")
                button_service = InlineKeyboardButton(text="38.02.07 Сервис", callback_data="service")
                button_tourism = InlineKeyboardButton(text="43.03.02 Туризм", callback_data="tourismBachelor")
                button_hotel_business = InlineKeyboardButton(text="43.03.03 Гостиничное дело",
                                                             callback_data="hotelBusiness")
                button_fundamental_informatic = InlineKeyboardButton(text="02.03.02 Фундаментальная информатика и"
                                                                          " информационные технологии",
                                                                     callback_data="fundamentalInformatic")
                button_ecology = InlineKeyboardButton(text="05.03.06 Экология и природопользование",
                                                      callback_data="ecology")
                button_ic_technology = InlineKeyboardButton(text="09.03.02 Информационные системы и технологии",
                                                            callback_data="icTechnology")
                button_informatics = InlineKeyboardButton(text="09.03.03 Прикладная информатика",
                                                          callback_data="informatics")
                button_innovation = InlineKeyboardButton(text="27.03.05 Инноватика", callback_data="innovation")
                button_economy_state = InlineKeyboardButton(text="38.03.01 Экономика", callback_data="economyStateSector")
                button_state_management = InlineKeyboardButton(text="38.03.04 Государственное и муниципальное"
                                                                    " управление", callback_data="stateManagement")
                button_business_informatic = InlineKeyboardButton(text="38.03.05 Бизнес-информатика",
                                                                  callback_data="businessInformatic")
                button_sociology = InlineKeyboardButton(text="39.03.01 Социология", callback_data="sociology")
                button_region = InlineKeyboardButton(text="41.03.01 Зарубежное регионоведение", callback_data="region")
                button_international_relation = InlineKeyboardButton(text="41.03.05 Международные отношения",
                                                                     callback_data="internationalRelation")
                button_housing_management = InlineKeyboardButton(text="38.03.10 Жилищное хозяйство и коммунальная"
                                                                      " инфраструктура",
                                                                 callback_data="housingManagement")
                button_statistics = InlineKeyboardButton(text="01.03.05 Статистика", callback_data="statistics")
                button_political_science = InlineKeyboardButton(text="41.03.04 Политология",
                                                                callback_data="politicalScience")
                button_law = InlineKeyboardButton(text="40.03.01 Юриспруденция", callback_data="law")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy, button_management,
                                                                        button_person_management, button_advert,
                                                                        button_service, button_tourism,
                                                                        button_hotel_business,
                                                                        button_fundamental_informatic, button_ecology,
                                                                        button_ic_technology, button_informatics,
                                                                        button_innovation, button_economy_state,
                                                                        button_state_management,
                                                                        button_business_informatic, button_sociology,
                                                                        button_region, button_international_relation,
                                                                        button_housing_management,
                                                                        button_statistics, button_political_science,
                                                                        button_law)

            elif formOfStudy == "Очно-заочная":
                button_economy = InlineKeyboardButton(text="38.03.01 Экономика", callback_data="economy")
                button_management = InlineKeyboardButton(text="38.03.02 Менеджмент", callback_data="management")
                button_person_management = InlineKeyboardButton(text="38.03.03 Управление персоналом",
                                                                callback_data="personManagement")
                button_economy_state = InlineKeyboardButton(text="38.03.01 Экономика", callback_data="economyStateSector")
                button_state_management = InlineKeyboardButton(text="38.03.04 Государственное и муниципальное"
                                                                    " управление", callback_data="stateManagement")
                button_business_informatic = InlineKeyboardButton(text="38.03.05 Бизнес-информатика",
                                                                  callback_data="businessInformatic")
                button_housing_management = InlineKeyboardButton(text="38.03.10 Жилищное хозяйство и коммунальная"
                                                                      " инфраструктура",
                                                                 callback_data="housingManagement")
                button_psyсhology = InlineKeyboardButton(text="37.03.01 Психология", callback_data="psyсhology")
                button_law = InlineKeyboardButton(text="40.03.01 Юриспруденция", callback_data="law")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy, button_management,
                                                                        button_person_management, button_economy_state,
                                                                        button_state_management,
                                                                        button_business_informatic,
                                                                        button_housing_management, button_psyсhology,
                                                                        button_law)
            else:
                button_advert = InlineKeyboardButton(text="42.03.01  Реклама и связи с общественностью",
                                                     callback_data="advert")
                button_service = InlineKeyboardButton(text="38.02.07 Сервис", callback_data="service")
                button_tourism = InlineKeyboardButton(text="43.03.02 Туризм", callback_data="tourismBachelor")
                button_hotel_business = InlineKeyboardButton(text="43.03.03 Гостиничное дело",
                                                             callback_data="hotelBusiness")
                button_ecology = InlineKeyboardButton(text="05.03.06 Экология и природопользование",
                                                      callback_data="ecology")
                button_informatics = InlineKeyboardButton(text="09.03.03 Прикладная информатика",
                                                          callback_data="informatics")
                button_sociology = InlineKeyboardButton(text="39.03.01 Социология", callback_data="sociology")
                button_law = InlineKeyboardButton(text="40.03.01 Юриспруденция", callback_data="law")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_advert, button_service, button_tourism,
                                                                        button_hotel_business, button_ecology,
                                                                        button_informatics, button_sociology,
                                                                        button_law)

        elif levelOfStudy == "Специалитет":
            if formOfStudy == "Очная":
                button_psyсhology = InlineKeyboardButton(text="37.05.02 Психология служебной деятельности",
                                                         callback_data="psyсhologySpecialist")
                button_economy_security = InlineKeyboardButton(text="38.05.01 Экономическая безопасность",
                                                               callback_data="economySecurity")
                button_legal_support = InlineKeyboardButton(text="40.05.01 Правовое обеспечение национальной"
                                                                 " безопасности", callback_data="legalSupport")
                button_law_enforcement = InlineKeyboardButton(text="40.05.02 Правоохранительная деятельность",
                                                              callback_data="lawEnforcement")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_psyсhology, button_economy_security,
                                                                        button_legal_support, button_law_enforcement)

            elif formOfStudy == "Заочная":
                button_economy_security = InlineKeyboardButton(text="38.05.01 Экономическая безопасность",
                                                               callback_data="economySecurity")
                button_legal_support = InlineKeyboardButton(text="40.05.01 Правовое обеспечение национальной"
                                                                 " безопасности", callback_data="legalSupport")
                button_law_enforcement = InlineKeyboardButton(text="40.05.02 Правоохранительная деятельность",
                                                              callback_data="lawEnforcement")

                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economy_security, button_legal_support,
                                                                        button_law_enforcement)

            else:
                button_law_enforcement = InlineKeyboardButton(text="40.05.02 Правоохранительная деятельность",
                                                              callback_data="lawEnforcement")
                inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_law_enforcement)

            bot.send_message(c.from_user.id, "Выберите направление подготовки: ", reply_markup=inline_keyboard)


# обработчик callback-функции specialization_spo
@bot.callback_query_handler(func=lambda c: c.data == "economyAccounting" or c.data == "insurance" or
                            c.data == "logistics" or c.data == "finance" or c.data == "banking" or
                            c.data == "tourismSPO" or c.data == "informaticsSPO" or
                            c.data == "landPropertyRelation")
def write_specialization_spo(c: CallbackQuery):
    global specialization
    if c.data == "economyAccounting":
        specialization = "38.02.01 Экономика и бухгалтерский учет"
    elif c.data == "insurance":
        specialization = "38.02.02 Страховое дело"
    elif c.data == "logistics":
        specialization = "38.02.03 Операционная деятельность в логистике"
    elif c.data == "finance":
        specialization = "38.02.06 Финансы"
    elif c.data == "banking":
        specialization = "38.02.07 Банковское дело"
    elif c.data == "tourismSPO":
        specialization = "43.02.10 Туризм"
    elif c.data == "informatics":
        specialization = "09.02.05 Прикладная информатика"
    elif c.data == "landPropertyRelation":
        specialization = "21.02.05 Земельно-имущественные отношения"

    write_db(c)


# обработчик callback-функции direction_bachelor
@bot.callback_query_handler(func=lambda c: c.data == "fundamentalInformatic" or c.data == "ecology" or
                            c.data == "icTechnology" or c.data == "informatics" or c.data == "innovation"
                            or c.data == "psychology" or c.data == "economyStateSector" or
                            c.data == "stateManagement" or c.data == "businessInformatic" or
                            c.data == "sociology" or c.data == "region" or
                            c.data == "internationalRelation" or c.data == "housingManagement" or
                            c.data == "statistics" or c.data == "politicalScience" or
                            c.data == "economy" or c.data == "management" or c.data == "personManagement"
                            or c.data == "advert" or c.data == "service" or c.data == "tourismBachelor"
                            or c.data == "hotelBusiness" or c.data == "law")
def write_direction_bachelor(c: CallbackQuery):
    global direction
    global specialization
    if c.data == "fundamentalInformatic":
        direction = "02.03.02 Фундаментальная информатика и информационные технологии"
        specialization = "Инженерия программного обеспечения"
    elif c.data == "ecology":
        direction = "05.03.06 Экология и природопользование"
        specialization = "Природопользование"
    elif c.data == "icTechnology":
        direction = "09.03.02 Информационные системы и технологии"
        specialization = "Проектирование, разработка и сопровождение информационных систем"
    elif c.data == "informatics":
        direction = "09.03.03 Прикладная информатика"
        specialization = "Прикладная информатика и бизнес-анализ"
    elif c.data == "innovation":
        direction = "27.03.05 Инноватика"
        specialization = "Информационные и инновационные технологии цифровой экономики"
    elif c.data == "psychology":
        direction = "37.03.01 Психология"
        specialization = "Психологическое консультирование и психология личности"
    elif c.data == "economyStateSector":
        direction = "38.03.01 Экономика"
        if faculty == "ФБП":
            write_db(c)
        else:
            button_business_statistic = InlineKeyboardButton(text="Бизнес-статистика и аналитика",
                                                             callback_data="businessStatistic")
            button_global_economy = InlineKeyboardButton(text="Мировая экономика", callback_data="globalEconomy")
            button_taxing = InlineKeyboardButton(text="Налоги и налогообложение", callback_data="taxing")
            button_economy_statistic = InlineKeyboardButton(text="Статистика", callback_data="economyStatistic")
            button_investment_design = InlineKeyboardButton(text="Инвестиционное проектирование и развитие территории",
                                                            callback_data="investmentDesign")

            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_business_statistic, button_global_economy,
                                                                    button_taxing, button_economy_statistic,
                                                                    button_investment_design)

            bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "stateManagement":
        direction = "38.03.04 Государственное и муниципальное управление"
        specialization = "Государственное управление экономическим развитием"
    elif c.data == "businessInformatic":
        direction = "38.03.05 Бизнес-информатика"
        specialization = "Цифровая экономика"
    elif c.data == "sociology":
        direction = "39.03.01 Социология"
        specialization = "Социология экономики и маркетинга"
    elif c.data == "region":
        direction = "41.03.01 Зарубежное регионоведение"
        specialization = "Политика и экономика регионов мира (Азиатско-Тихоокеанский регион)"
    elif c.data == "internationalRelation":
        direction = "41.03.05 Международные отношения"
        specialization = "Мировая политика"
    elif c.data == "housingManagement":
        direction = "38.03.10 Жилищное хозяйство и коммунальная инфраструктура"
        specialization = "Управление жилищным фондом и коммерческой недвижимостью"
    elif c.data == "statistics":
        direction = "01.03.05 Статистика"
        specialization = "Анализ и управление данными"
    elif c.data == "politicalScience":
        direction = "41.03.04 Политология"
        specialization = "Международные политические и экономические коммуникации"
    elif c.data == "economy":
        direction = "38.03.01 Экономика"
        if faculty == "ФБП":
            write_db(c)
        else:
            button_audit = InlineKeyboardButton(text="Аудит и информационное сопровождение бизнеса",
                                                callback_data="audit")
            button_economy_banking = InlineKeyboardButton(text="Банковское дело", callback_data="economyBanking")
            button_corporate_finance = InlineKeyboardButton(text="Корпоративные финансы и бизнес-разведка",
                                                            callback_data="corporateFinance")
            button_analytical_support = InlineKeyboardButton(text="Учетно-аналитическое обеспечение бизнеса",
                                                             callback_data="analyticalSupport")
            button_financial_market = InlineKeyboardButton(text="Финансовый рынок", callback_data="financialMarket")
            button_enterprise_economy = InlineKeyboardButton(text="Экономика предприятий и организаций",
                                                             callback_data="enterpriseEconomy")
            button_business_economy = InlineKeyboardButton(text="Экономика предпринимательской деятельности",
                                                           callback_data="businessEconomy")

            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_audit, button_economy_banking,
                                                                    button_corporate_finance, button_analytical_support,
                                                                    button_financial_market, button_enterprise_economy,
                                                                    button_business_economy)

            bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "management":
        direction = "38.03.02 Менеджмент"
        if faculty == "ФБП":
            write_db(c)
        else:
            button_internet_marketing = InlineKeyboardButton(text="Интернет-маркетинг и бизнес-коммуникации",
                                                             callback_data="internetMarketing")
            button_corporate_management = InlineKeyboardButton(text="Корпоративный и международный менеджмент",
                                                               callback_data="corporateManagement")
            button_management_logistic = InlineKeyboardButton(text="Логистика и управление цепями поставок",
                                                              callback_data="managementLogistic")
            button_organization_management = InlineKeyboardButton(text="Менеджмент организации",
                                                                  callback_data="organizationManagement")
            button_business_project_management = InlineKeyboardButton(text="Управление предпринимательскими проектами",
                                                                      callback_data="businessProjectManagement")
            button_human_resource_management = InlineKeyboardButton(text="Управление человеческими ресурсами",
                                                                    callback_data="humanResourceManagement")
            button_hr_branding = InlineKeyboardButton(text="Брендинг человеческих ресурсов (HR-брендинг)"
                                                           " в медиапространстве", callback_data="HR-branding")

            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_internet_marketing,
                                                                    button_corporate_management,
                                                                    button_management_logistic,
                                                                    button_organization_management,
                                                                    button_business_project_management,
                                                                    button_human_resource_management,
                                                                    button_hr_branding)
            bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "personManagement":
        direction = "38.03.03 Управление персоналом"
        specialization = "Управление персоналом организации"
    elif c.data == "advert":
        direction = "42.03.01  Реклама и связи с общественностью"
        if faculty == "ФБП":
            write_db(c)
        else:
            button_public_relation = InlineKeyboardButton(text="Связи с общественностью и реклама в различных сферах",
                                                          callback_data="publicRelation")
            button_digital_communication= InlineKeyboardButton(text="Цифровые коммуникации и маркетинг",
                                                               callback_data="digitalCommunication")

            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_public_relation,
                                                                    button_digital_communication)
            bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "service":
        direction = "38.02.07 Сервис"
        specialization = "Международная ярмарочно-выставочная деятельность и торгово-промышленный маркетинг"
    elif c.data == "tourismBachelor":
        direction = "43.03.02 Туризм"
        specialization = "Туристический и экскурсионный бизнес"
    elif c.data == "hotelBusiness":
        direction = "43.03.03 Гостиничное дело"
        specialization = "Управление гостиничным и санаторно-курортным комплексом"
    elif c.data == "law":
        direction = "40.03.01 Юриспруденция"
        if faculty == "ФБП":
            write_db(c)
        else:
            button_general_legal = InlineKeyboardButton(text="Общеюридический", callback_data="generalLegal")
            button_legal_service = InlineKeyboardButton(text="Юридические услуги гражданам и организациям",
                                                        callback_data="legalService")
            button_corporate_lawyer = InlineKeyboardButton(text="Юрист корпорации", callback_data="corporateLawyer")
            button_law_protection_economy = InlineKeyboardButton(text="Уголовно-правовая защита экономики",
                                                                 callback_data="lawProtectionEconomy")

            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_general_legal, button_legal_service,
                                                                    button_corporate_lawyer,
                                                                    button_law_protection_economy)
            bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)

    if specialization is not None:
        write_db(c)


# обработчик callback-функции direction_master
@bot.callback_query_handler(func=lambda c: c.data == "icTechnologyMaster" or c.data == "informaticsMaster" or
                            c.data == "innovationMaster" or c.data == "psychologyMaster" or
                            c.data == "economyStateSectorMaster" or c.data == "stateManagementMaster" or
                            c.data == "businessInformaticMaster" or c.data == "sociologyMaster" or
                            c.data == "regionMaster" or c.data == "internationalRelationMaster" or
                            c.data == "housingManagementMaster" or c.data == "statisticsMaster" or
                            c.data == "financeCreditStateSector" or c.data == "economyMaster" or
                            c.data == "managementMaster" or c.data == "personManagementMaster" or
                            c.data == "financeCredit" or c.data == "advertMaster" or c.data == "lawMaster")
def write_direction_master(c: CallbackQuery):
    global direction
    global specialization
    if c.data == "icTechnologyMaster":
        direction = "09.04.02 Информационные системы и технологии"
        specialization = "Технологии электронного бизнеса"
    elif c.data == "informaticsMaster":
        direction = "09.04.03 Прикладная информатика"
        specialization = "Бизнес-инжиниринг и управление ИТ-проектами"
    elif c.data == "innovationMaster":
        direction = "27.04.05 Инноватика"
        button_innovation_management = InlineKeyboardButton(text="Управление инновациями в сфере наукоемких технологий",
                                                            callback_data="innovationManagement")
        button_digital_technologies = InlineKeyboardButton(text="Цифровые технологии в управлении инновациями",
                                                           callback_data="digitalTechnologies")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_innovation_management,
                                                                button_digital_technologies)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "psychologyMaster":
        direction = "37.04.01 Психология"
        button_general_psychology = InlineKeyboardButton(text="Общая психология и психология личности",
                                                         callback_data="generalPsychology")
        button_sport_psychology = InlineKeyboardButton(text="Спортивная психология", callback_data="sportPsychology")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_general_psychology, button_sport_psychology)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "economyStateSectorMaster":
        direction = "38.04.01 Экономика"
        specialization = "Бизнес-статистика"
    elif c.data == "stateManagementMaster":
        direction = "38.04.04 Государственное и муниципальное управление"
        button_territory_development = InlineKeyboardButton(text="Государственное и муниципальное управление развитием"
                                                                 " территории", callback_data="territoryDevelopment")
        button_public_procurement = InlineKeyboardButton(text="Государственные и муниципальные закупки",
                                                         callback_data="publicProcurement")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_territory_development, button_public_procurement)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "businessInformaticMaster":
        direction = "38.04.05 Бизнес-информатика"
        specialization = "Управление бизнес-информацией"
    elif c.data == "sociologyMaster":
        direction = "39.04.01 Социология"
        specialization = "Социология бизнеса"
    elif c.data == "regionMaster":
        direction = "41.04.01 Зарубежное регионоведение"
        specialization = "Международно-политический анализ регионов мира"
    elif c.data == "internationalRelationMaster":
        direction = "41.04.05 Международные отношения"
        specialization = "Мировая политика"
    elif c.data == "housingManagementMaster":
        direction = "38.04.10 Жилищное хозяйство и коммунальная инфраструктура"
        specialization = "Управление развитием и модернизацией жилищного хозяйства"
    elif c.data == "statisticsMaster":
        direction = "01.04.05 Статистика"
        specialization = "Интеллектуальный анализ данных"
    elif c.data == "financeCreditStateSector":
        direction = "38.04.08 Финансы и кредит"
        specialization = "Противодействие незаконным финансовым операциям"
    elif c.data == "economyMaster":
        direction = "38.04.01 Экономика"
        button_international_audit = InlineKeyboardButton(text="Международный учет и аудит",
                                                          callback_data="internationalAudit")
        button_corporate_finance = InlineKeyboardButton(text="Корпоративные финансы и оценка стоимости бизнеса",
                                                        callback_data="corporateFinanceMaster")
        button_audit = InlineKeyboardButton(text="Учет, анализ и аудит", callback_data="auditMaster")
        button_firm_economic = InlineKeyboardButton(text="Экономика фирмы", callback_data="firmEconomic")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_international_audit, button_corporate_finance,
                                                                button_audit, button_firm_economic)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "managementMaster":
        direction = "38.04.02 Менеджмент"
        button_business_management = InlineKeyboardButton(text="Маркетинг и управление бизнесом",
                                                          callback_data="businessManagement")
        button_management_tourism_business = InlineKeyboardButton(text="Менеджмент и предпринимательство в туристском,"
                                                                       " гостиничном и санаторно-курортном бизнесе",
                                                                  callback_data="managementTourismBusiness")
        button_financial_management = InlineKeyboardButton(text="Финансовый менеджмент в цифровой экономике",
                                                           callback_data="financialManagement")
        button_management_competitiveness = InlineKeyboardButton(text="Управление конкурентоспособностью персонала в"
                                                                      " цифровой экономике",
                                                                 callback_data="managementCompetitiveness")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_business_management,
                                                                button_management_tourism_business,
                                                                button_financial_management,
                                                                button_management_competitiveness)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "personManagementMaster":
        direction = "38.04.03 Управление персоналом"
        specialization = "Экономика и управление персоналом"
    elif c.data == "financeCredit":
        direction = "38.04.08 Финансы и кредит"
        specialization = "Цифровые технологии на финансовом рынке"
    elif c.data == "advertMaster":
        direction = "42.04.01  Реклама и связи с общественностью"
        button_online_business = InlineKeyboardButton(text="Бизнес-онлайн и стратегические коммуникации",
                                                      callback_data="onlineBusiness")
        button_advertising_business = InlineKeyboardButton(text="Рекламный бизнес и управление брендами",
                                                           callback_data="advertisingBusiness")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_online_business,
                                                                button_advertising_business)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "lawMaster":
        direction = "40.04.01 Юриспруденция"
        button_legal_regulation_economy = InlineKeyboardButton(text="Правовое регулирования экономики",
                                                               callback_data="legalRegulationEconomy")
        button_countering_crime_economy = InlineKeyboardButton(text="Противодействие преступлениям в сфере экономики",
                                                               callback_data="counteringCrimeEconomy")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_legal_regulation_economy,
                                                                button_countering_crime_economy)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)

    if specialization is not None:
        write_db(c)


# обработчик callback-функции direction_specialist
@bot.callback_query_handler(func=lambda c: c.data == "psychologySpecialist" or c.data == "economySecurity" or
                            c.data == "legalSupport" or c.data == "lawEnforcement")
def write_direction_specialist(c: CallbackQuery):
    global direction
    global specialization
    if c.data == "psychologySpecialist":
        direction = "37.05.02 Психология служебной деятельности"
        specialization = "Психологическое обеспечение служебной деятельности в экстремальных условиях"
    elif c.data == "economySecurity":
        direction = "38.05.01 Экономическая безопасность"
        if faculty == "ФБП":
            write_db()
        else:
            button_economic_legal_support = InlineKeyboardButton(text="Экономико-правовое обеспечение экономической"
                                                                      " безопасности",
                                                                 callback_data="economicLegalSupport")
            button_financial_economic_support= InlineKeyboardButton(text="Финансово-экономическое обеспечение"
                                                                         " федеральных органов, обеспечивающих"
                                                                         " безопасность Российской Федерации",
                                                                    callback_data="financialEconomicSupport")

            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_economic_legal_support,
                                                                    button_financial_economic_support)
            bot.send_message(c.from_user.id, "Выберите специализацию: ", reply_markup=inline_keyboard)
    elif c.data == "legalSupport":
        direction = "40.05.01 Правовое обеспечение национальной безопасности"
        specialization = "Уголовно-правовая"
    elif c.data == "lawEnforcement":
        direction = "40.05.02 Правоохранительная деятельность"
        specialization = "Административная деятельность"

    if specialization is not None:
        write_db(c)


# обработчик callback-функции direction_graduate
@bot.callback_query_handler(func=lambda c: c.data == "economyGraduate" or c.data == "informaticComputerTech" or
                            c.data == "psychologyGraduate" or c.data == "economyStateSectorGraduate" or
                            c.data == "sociologyGraduate" or c.data == "historicalScience" or c.data == "philosophy")
def write_direction_graduate(c: CallbackQuery):
    global direction
    global specialization
    if c.data == "economyGraduate" and formOfStudy == "Очная":
        direction = "38.06.01 Экономика"
        button_money_circulation = InlineKeyboardButton(text="Финансы, денежное обращение и кредит",
                                                             callback_data="moneyCirculation")
        button_management_economy = InlineKeyboardButton(text="Менеджмент", callback_data="managementEconomy")
        button_labour_economic = InlineKeyboardButton(text="Экономика труда", callback_data="labourEconomic")
        button_management_enterprise = InlineKeyboardButton(text="Экономика, организация и управление"
                                                                 " предприятиями, отраслями, комплексами:"
                                                                 " сфера услуг", callback_data="managementEnterprise")
        button_business_economy = InlineKeyboardButton(text="Экономика предпринимательства",
                                                       callback_data="businessEconomyGraduate")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_money_circulation, button_management_economy,
                                                                button_labour_economic, button_management_enterprise,
                                                                button_business_economy)

        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)

    elif c.data == "economyGraduate" and formOfStudy == "Заочная":
        direction = "38.06.01 Экономика"
        button_money_circulation = InlineKeyboardButton(text="Финансы, денежное обращение и кредит",
                                                        callback_data="moneyCirculation")
        button_management_economy = InlineKeyboardButton(text="Менеджмент", callback_data="managementEconomy")
        button_management_enterprise = InlineKeyboardButton(text="Экономика, организация и управление"
                                                                 " предприятиями, отраслями, комплексами:"
                                                                 " сфера услуг",
                                                            callback_data="managementEnterprise")
        button_business_economy = InlineKeyboardButton(text="Экономика предпринимательства",
                                                       callback_data="businessEconomyGraduate")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_money_circulation, button_management_economy,
                                                                button_management_enterprise, button_business_economy)

        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)

    elif c.data == "informaticComputerTech":
        direction = "09.06.01 Информатика и вычислительная техника"
        specialization = "Информационные системы и процессы"
    elif c.data == "psychologyGraduate":
        direction = "37.06.01 Психологические науки"
        specialization = "Психофизиология"
    elif c.data == "economyStateSectorGraduate":
        direction = "38.06.01 Экономика"
        button_accounting = InlineKeyboardButton(text="Бухгалтерский учет, статистика",
                                                 callback_data="accountingGraduate")
        button_regional_economy = InlineKeyboardButton(text="Региональная экономика",
                                                       callback_data="regionalEconomy")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_accounting, button_regional_economy)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)
    elif c.data == "sociologyGraduate":
        direction = "39.06.01 Cоциологические науки"
        specialization = "Социология управления"
    elif c.data == "historicalScience":
        direction = "46.06.01 Исторические науки и археология"
        specialization = "История международных отношений и внешней политики"
    elif c.data == "philosophy":
        direction = "47.06.01 Философия, этика и религиоведение"
        button_social_philosophy = InlineKeyboardButton(text="Социальная философия", callback_data="socialPhilosophy")
        button_science_philosophy = InlineKeyboardButton(text="Философия науки и техники",
                                                         callback_data="sciencePhilosophy")

        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(button_social_philosophy, button_science_philosophy)
        bot.send_message(c.from_user.id, "Выберите профиль обучения: ", reply_markup=inline_keyboard)

    if specialization is not None:
        write_db(c)


# обработчик callback-функции specialization
@bot.callback_query_handler(func=lambda c: c.data == "businessStatistics" or c.data == "globalEconomy" or
                            c.data == "taxing" or c.data == "economyStatistic" or c.data == "investmentDesign" or
                            c.data == "audit" or c.data == "economyBanking" or c.data == "corporateFinance" or
                            c.data == "analyticalSupport" or c.data == "financialMarket" or
                            c.data == "enterpriseEconomy" or c.data == "businessEconomy" or
                            c.data == "internetMarketing" or c.data == "corporateManagement" or
                            c.data == "managementLogistic" or c.data == "organizationManagement" or
                            c.data == "businessProjectManagement" or c.data == "HumanResourceManagement" or
                            c.data == "HR-branding" or c.data == "publicRelation" or c.data == "digitalCommunication" or
                            c.data == "generalLegal" or c.data == "legalService" or c.data == "corporateLawyer" or
                            c.data == "innovationManagement" or c.data == "digitalTechnologies" or
                            c.data == "generalPsychology" or c.data == "sportPsychology" or
                            c.data == "territoryDevelopment" or c.data == "publicProcurement" or
                            c.data == "internationalAudit" or c.data == "corporateFinanceMaster" or
                            c.data == "auditMaster" or c.data == "firmEconomic" or c.data == "businessManagement" or
                            c.data == "managementTourismBusiness" or c.data == "financialManagement" or
                            c.data == "managementCompetitiveness" or c.data == "onlineBusiness" or
                            c.data == "advertisingBusiness" or c.data == "legalRegulationEconomy" or
                            c.data == "counteringCrimeEconomy" or c.data == "economicLegalSupport" or
                            c.data == "financialEconomicSupport" or c.data == "moneyCirculation" or
                            c.data == "managementEconomy" or c.data == "labourEconomic" or
                            c.data == "managementEnterprise" or c.data == "businessEconomyGraduate" or
                            c.data == "accountingGraduate" or c.data == "regionalEconomy" or
                            c.data == "socialPhilosophy" or c.data == "sciencePhilosophy" or
                            c.data == "lawProtectionEconomy")
def write_specialization(c: CallbackQuery):
    global specialization
    if c.data == "businessStatistics":
        specialization = "Бизнес-статистика и аналитика"
    elif c.data == "globalEconomy":
        specialization = "Мировая экономика"
    elif c.data == "taxing":
        specialization = "Налоги и налогообложение"
    elif c.data == "economyStatistic":
        specialization = "Статистика"
    elif c.data == "investmentDesign":
        specialization = "Инвестиционное проектирование и развитие территории"
    elif c.data == "audit":
        specialization = "Аудит и информационное сопровождение бизнеса"
    elif c.data == "economyBanking":
        specialization = "Банковское дело"
    elif c.data == "corporateFinance":
        specialization = "Корпоративные финансы и бизнес-разведка"
    elif c.data == "analyticalSupport":
        specialization = "Учетно-аналитическое обеспечение бизнеса"
    elif c.data == "financialMarket":
        specialization = "Финансовый рынок"
    elif c.data == "enterpriseEconomy":
        specialization = "Экономика предприятий и организаций"
    elif c.data == "businessEconomy":
        specialization = "Экономика предпринимательской деятельности"
    elif c.data == "internetMarketing":
        specialization = "Интернет-маркетинг и бизнес-коммуникации"
    elif c.data == "corporateManagement":
        specialization = "Корпоративный и международный менеджмент"
    elif c.data == "managementLogistic":
        specialization = "Логистика и управление цепями поставок"
    elif c.data == "organizationManagement":
        specialization = "Менеджмент организации"
    elif c.data == "businessProjectManagement":
        specialization = "Управление предпринимательскими проектами"
    elif c.data == "HumanResourceManagement":
        specialization = "Управление человеческими ресурсами"
    elif c.data == "HR-branding":
        specialization = "Брендинг человеческих ресурсов (HR-брендинг) в медиапространстве"
    elif c.data == "publicRelation":
        specialization = "Связи с общественностью и реклама в различных сферах"
    elif c.data == "digitalCommunication":
        specialization = "Цифровые коммуникации и маркетинг"
    elif c.data == "generalLegal":
        specialization = "Общеюридический"
    elif c.data == "legalService":
        specialization = "Юридические услуги гражданам и организациям"
    elif c.data == "corporateLawyer":
        specialization = "Юрист корпорации"
    elif c.data == "innovationManagement":
        specialization = "Управление инновациями в сфере наукоемких технологий"
    elif c.data == "lawProtectionEconomy":
        specialization = "Уголовно-правовая защита экономики"
    elif c.data == "digitalTechnologies":
        specialization = "Цифровые технологии в управлении инновациями"
    elif c.data == "generalPsychology":
        specialization = "Общая психология и психология личности"
    elif c.data == "sportPsychology":
        specialization = "Спортивная психология"
    elif c.data == "territoryDevelopment":
        specialization = "Государственное и муниципальное управление развитием территории"
    elif c.data == "publicProcurement":
        specialization = "Государственные и муниципальные закупки"
    elif c.data == "internationalAudit":
        specialization = "Международный учет и аудит"
    elif c.data == "corporateFinanceMaster":
        specialization = "Корпоративные финансы и оценка стоимости бизнеса"
    elif c.data == "auditMaster":
        specialization = "Учет, анализ и аудит"
    elif c.data == "firmEconomic":
        specialization = "Экономика фирмы"
    elif c.data == "businessManagement":
        specialization = "Маркетинг и управление бизнесом"
    elif c.data == "managementTourismBusiness":
        specialization = "Менеджмент и предпринимательство в туристском, гостиничном и санаторно-курортном бизнесе"
    elif c.data == "financialManagement":
        specialization = "Финансовый менеджмент в цифровой экономике"
    elif c.data == "managementCompetitiveness":
        specialization = "Управление конкурентоспособностью персонала в цифровой экономике"
    elif c.data == "onlineBusiness":
        specialization = "Бизнес-онлайн и стратегические коммуникации"
    elif c.data == "advertisingBusiness":
        specialization = "Рекламный бизнес и управление брендами"
    elif c.data == "legalRegulationEconomy":
        specialization = "Правовое регулирование экономики"
    elif c.data == "counteringCrimeEconomy":
        specialization = "Противодействие преступлениям в сфере экономики"
    elif c.data == "economicLegalSupport":
        specialization = "Экономико-правовое обеспечение экономической безопасности"
    elif c.data == "financialEconomicSupport":
        specialization = "Финансово-экономическое обеспечение федеральных органов, обеспечивающих безопасность" \
                         " Российской Федерации"
    elif c.data == "moneyCirculation":
        specialization = "Финансы, денежное обращение и кредит"
    elif c.data == "managementEconomy":
        specialization = "Менеджмент"
    elif c.data == "labourEconomic":
        specialization = "Экономика труда"
    elif c.data == "managementEnterprise":
        specialization = "Экономика, организация и управление предприятиями, отраслями , комплексами: сфера услуг"
    elif c.data == "businessEconomyGraduate":
        specialization = "Экономика предпринимательства"
    elif c.data == "accountingGraduate":
        specialization = "Бухгалтерский учет, статистика"
    elif c.data == "regionalEconomy":
        specialization = "Региональная экономика"
    elif c.data == "socialPhilosophy":
        specialization = "Социальная философия"
    elif c.data == "sciencePhilosophy":
        specialization = "Философия науки и техники"

    write_db(c)


def write_db(c: CallbackQuery):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    global direction
    global specialization
    if direction is None:
        cursor.execute(f"insert into DataStudents(ID, FullName, Course, StudentGroup, FormStudy, LevelStudy, Faculty,"
                       f" Specialization, NumberGradebook, Phone, Email)"
                       f" values({clientID}, '{fullName}', {course}, '{group}', '{formOfStudy}', '{levelOfStudy}',"
                       f" '{faculty}', '{specialization}', {numberGradebook}, '{phone}', '{e_mail}')")

    elif specialization is None:
        cursor.execute(f"insert into DataStudents(ID, FullName, Course, StudentGroup, FormStudy, LevelStudy, Faculty,"
                       f" Direction, NumberGradebook, Phone, Email)"
                       f" values({clientID}, '{fullName}', {course}, '{group}', '{formOfStudy}', '{levelOfStudy}',"
                       f" '{faculty}', '{direction}', {numberGradebook}, '{phone}', '{e_mail}')")
    else:
        cursor.execute(f"insert into DataStudents(ID, FullName, Course, StudentGroup, FormStudy, LevelStudy, Faculty,"
                       f" Direction, Specialization, NumberGradebook, Phone, Email)"
                       f" values({clientID}, '{fullName}', {course}, '{group}', '{formOfStudy}', '{levelOfStudy}',"
                       f" '{faculty}', '{direction}', '{specialization}', {numberGradebook}, '{phone}', '{e_mail}')")

    conn.commit()
    print("записано")
    conn.close()

    bot.send_message(c.from_user.id, f'Регистрация завершена.')

    create_keyboard(c)
