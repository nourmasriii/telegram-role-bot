import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading
import os

TOKEN = "8647146626:AAGT-Ia07RxDycsDh8BPBmsMBRzLlXtyMQo"

bot = telebot.TeleBot(TOKEN)

roles = []
message_id = None
chat_id = None

app = Flask('')


@app.route('/')
def home():
    return "Bot is running"


def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


def run_bot():
    bot.infinity_polling()


def build_list():
    if len(roles) == 0:
        return "القائمة فارغة"
    text = "قائمة الأدوار:\n\n"
    for i, name in enumerate(roles, start=1):
        text += f"{i}- {name}\n"
    return text


def keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("سجل اسمي", callback_data="register"),
        InlineKeyboardButton("قرأت ✅", callback_data="done")
    )
    return markup


@bot.message_handler(commands=['startlist'])
def start_list(message):
    global message_id, chat_id
    chat_id = message.chat.id

    msg = bot.send_message(chat_id, build_list(), reply_markup=keyboard())
    message_id = msg.message_id


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global roles

    name = call.from_user.first_name

    if call.data == "register":
        if name not in roles:
            roles.append(name)
            bot.answer_callback_query(call.id, "تم تسجيل اسمك")
        else:
            bot.answer_callback_query(call.id, "اسمك مسجل")

    elif call.data == "done":
        if name in roles:
            roles.remove(name)
            bot.answer_callback_query(call.id, "بارك الله فيك")

    bot.edit_message_text(build_list(), chat_id, message_id, reply_markup=keyboard())


threading.Thread(target=run_bot).start()
run()

 
