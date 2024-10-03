import telebot
from telebot import types

file = open('./token.txt')
token = file.read()

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton('создать заявку'))

    bot.send_message(message.chat.id,
                     'создай заявку по инструкциям для любого дз, включая проекты и т.п. и желающий выполнит ее за плату',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'создать заявку')
def create_task(message):
    bot.send_message(message.chat.id, 'напиши тему работы или название предмета')

    bot.register_next_step_handler(message, task_deadline)


def task_deadline(message):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        bot.send_message(message.chat.id, 'фото получено')
    elif message.content_type == 'text':
        bot.send_message(message.chat.id, 'напиши дату для дэдлайна, при необходимости укажи время')
    else:
        bot.send_message(message.chat.id, 'отправь фото или текст')


bot.polling(none_stop=True)
