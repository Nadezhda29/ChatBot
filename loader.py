from config import TOKEN
from telebot import TeleBot

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery

bot = TeleBot(token=TOKEN)


# создание клавиатуры "Выбрать услугу"
def create_keyboard(c: CallbackQuery):
    keyboard = ReplyKeyboardMarkup(True, True)
    button_select_service = KeyboardButton("Выбрать услугу")
    keyboard.add(button_select_service)
    # hide_keyboard = types.ReplyKeyboardRemove()

    bot.send_message(c.from_user.id, f'Чтобы получить информацию о предоставляемых услугах, нажми на'
                                     f' кнопку "Выбрать услугу."', reply_markup=keyboard)