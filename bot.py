import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "PUT_YOUR_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

roles = []
message_id = None
chat_id = None


def build_list():

    if len(roles) == 0:
        text = "القائمة فارغة"

    else:
        text = "قائمة الأدوار:\n\n"

        for i, name in enumerate(roles, start=1):
            text += f"{i}- {name}\n"

    return text


def keyboard():

    markup = InlineKeyboardMarkup()

    btn1 = InlineKeyboardButton("سجل اسمي", callback_data="register")
    btn2 = InlineKeyboardButton("قرأت ✅", callback_data="done")

    markup.add(btn1)
    markup.add(btn2)

    return markup


@bot.message_handler(commands=['startlist'])
def start_list(message):

    global message_id
    global chat_id

    chat_id = message.chat.id

    msg = bot.send_message(
        chat_id,
        build_list(),
        reply_markup=keyboard()
    )

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
            bot.answer_callback_query(call.id, "اسمك مسجل بالفعل")

    elif call.data == "done":

        if name in roles:
            roles.remove(name)
            bot.answer_callback_query(call.id, "بارك الله فيك")

    bot.edit_message_text(
        build_list(),
        chat_id,
        message_id,
        reply_markup=keyboard()
    )


bot.infinity_polling()
 
