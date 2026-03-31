import telebot

TOKEN = "8647146626:AAFxKmo5-j4PanRK1kLDZsaaXiM7LeTVv2k"  # حطي توكن البوت
bot = telebot.TeleBot(TOKEN)

# قاموس لتخزين الأسماء
user_roles = {}

# ----- 1. بدء تسجيل الأدوار -----
@bot.message_handler(commands=['startlist'])
def start_list(message):
    bot.send_message(
        message.chat.id,
        "✅ تم بدء تسجيل الأدوار!\nاضغط على 'سجل اسمي' للتسجيل.\nبعد القراءة اضغط 'قرأت ✅'."
    )

# ----- 2. تسجيل الأسماء -----
@bot.message_handler(func=lambda m: m.text == "سجل اسمي")
def register_user(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if user_id not in user_roles:
        user_roles[user_id] = {"name": user_name, "read": False}
        bot.send_message(message.chat.id, f"✅ {user_name} تم تسجيلك!")
    else:
        bot.send_message(message.chat.id, "⚠️ أنت مسجل مسبقًا!")

# ----- 3. تأكيد القراءة -----
@bot.message_handler(func=lambda m: m.text == "قرأت ✅")
def mark_read(message):
    user_id = message.from_user.id
    if user_id in user_roles:
        user_roles[user_id]["read"] = True
        bot.send_message(message.chat.id, f"✅ {user_roles[user_id]['name']} تم تأكيد القراءة!")
    else:
        bot.send_message(message.chat.id, "⚠️ لم يتم تسجيلك بعد!")

# ----- 4. إيقاف تسجيل الأدوار -----
@bot.message_handler(commands=['stoplist'])
def stop_list(message):
    bot.send_message(message.chat.id, "⏹️ تم إيقاف تسجيل الأدوار.")

# ----- 5. مسح الأدوار -----
@bot.message_handler(commands=['clearlist'])
def clear_list(message):
    user_roles.clear()
    bot.send_message(message.chat.id, "🗑️ تم مسح جميع الأدوار!")

# ----- تشغيل البوت -----
bot.polling()
