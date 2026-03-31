import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8647146626:AAFxKmo5-j4PanRK1kLDZsaaXiM7LeTVv2k"  # حطي توكن البوت
bot = telebot.TeleBot(TOKEN)

# قاموس لتخزين الأسماء
user_roles = {}

# ----- 1. بدء تسجيل الأدوار مع أزرار -----
@bot.message_handler(commands=['startlist'])
def start_list(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("سجل اسمي ✅", callback_data="register"),
        InlineKeyboardButton("قرأت ✅", callback_data="read")
    )
    bot.send_message(
        message.chat.id,
        "✅ تم بدء تسجيل الأدوار!\nاضغط على الأزرار لتسجيل اسمك أو تأكيد القراءة.",
        reply_markup=markup
    )

# ----- 2. التعامل مع ضغط الأزرار -----
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name

    if call.data == "register":
        if user_id not in user_roles:
            user_roles[user_id] = {"name": user_name, "read": False}
            bot.answer_callback_query(call.id, f"✅ {user_name} تم تسجيلك!")
        else:
            bot.answer_callback_query(call.id, "⚠️ أنت مسجل مسبقًا!")

    elif call.data == "read":
        if user_id in user_roles:
            user_roles[user_id]["read"] = True
            bot.answer_callback_query(call.id, f"✅ {user_roles[user_id]['name']} تم تأكيد القراءة!")
        else:
            bot.answer_callback_query(call.id, "⚠️ لم يتم تسجيلك بعد!")

# ----- 3. إيقاف تسجيل الأدوار -----
@bot.message_handler(commands=['stoplist'])
def stop_list(message):
    bot.send_message(message.chat.id, "⏹️ تم إيقاف تسجيل الأدوار.")

# ----- 4. مسح الأدوار -----
@bot.message_handler(commands=['clearlist'])
def clear_list(message):
    user_roles.clear()
    bot.send_message(message.chat.id, "🗑️ تم مسح جميع الأدوار!")

# ----- تشغيل البوت -----
bot.polling()
