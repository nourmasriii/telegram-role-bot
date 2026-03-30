import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "PUT_YOUR_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

roles = []

@bot.message_handler(commands=['startlist'])
def start_list(message):
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("سجل اسمي", callback_data="register")
    btn2 = InlineKeyboardButton("قرأت ✅", callback_data="done")
    markup.add(btn1)
    markup.add(btn2)

    bot.send_message(message.chat.id, "قائمة الأدوار:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "register":
        name = call.from_user.first_name
        roles.append(name)
        bot.answer_callback_query(call.id, "تم تسجيل اسمك")

    if call.data == "done":
        name = call.from_user.first_name
        if name in roles:
            roles.remove(name)
            bot.answer_callback_query(call.id, "تم تسجيل القراءة")

bot.infinity_polling()
