import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os

# ضع توكن البوت هنا
TOKEN = "8647146626:AAGT-Ia07RxDycsDh8BPBmsMBRzLlXtyMQo"
bot = telebot.TeleBot(TOKEN)

# IDs المشرفين فقط يمكنهم التحكم
ADMINS = [123456789]  # ضع هنا الـID الخاص بك أو المشرفين

roles = {}  # تخزين كل شخص وحالته
registration_open = False
chat_id = None
message_id = None

def build_list():
    if not roles:
        return "القائمة فارغة"
    text = "قائمة الأدوار:\n\n"
    for i, (name, status) in enumerate(roles.items(), start=1):
        text += f"{i}- {name} | {status}\n"
    return text

def keyboard():
    markup = InlineKeyboardMarkup()
    if registration_open:
        markup.add(
            InlineKeyboardButton("تسجيل اسم", callback_data="register"),
            InlineKeyboardButton("مستمعة 👂", callback_data="listening"),
            InlineKeyboardButton("معتذرة ❌", callback_data="absent"),
            InlineKeyboardButton("قرأت ✅", callback_data="read")
        )
    return markup

# أمر تشغيل الدور للمشرف
@bot.message_handler(commands=['start_roles'])
def start_roles(message):
    global registration_open, chat_id, message_id
    if message.from_user.id not in ADMINS:
        bot.reply_to(message, "أنت لست مشرفاً 🚫")
        return
    registration_open = True
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, build_list(), reply_markup=keyboard())
    message_id = msg.message_id

# أمر إيقاف الدور
@bot.message_handler(commands=['stop_roles'])
def stop_roles(message):
    global registration_open
    if message.from_user.id not in ADMINS:
        bot.reply_to(message, "أنت لست مشرفاً 🚫")
        return
    registration_open = False
    bot.send_message(message.chat.id, "تم إيقاف تسجيل الأدوار ✅")

# أمر مسح القائمة
@bot.message_handler(commands=['reset_roles'])
def reset_roles(message):
    global roles
    if message.from_user.id not in ADMINS:
        bot.reply_to(message, "أنت لست مشرفاً 🚫")
        return
    roles = {}
    bot.send_message(message.chat.id, "تم مسح القائمة والبدء من جديد 🗑️")

# تعامل مع الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global roles, registration_open
    name = call.from_user.first_name

    if not registration_open:
        bot.answer_callback_query(call.id, "التسجيل مغلق الآن 🚫")
        return

    if call.data == "register":
        if name not in roles:
            roles[name] = "مسجل"
            bot.answer_callback_query(call.id, "تم تسجيل اسمك ✅")
        else:
            bot.answer_callback_query(call.id, "أنت مسجل بالفعل ✅")
    elif call.data == "listening":
        if name in roles:
            roles[name] = "مستمعة 👂"
            bot.answer_callback_query(call.id, "تم وضعك في المستمعة 👂")
        else:
            bot.answer_callback_query(call.id, "يجب التسجيل أولاً")
    elif call.data == "absent":
        if name in roles:
            roles[name] = "معتذرة ❌"
            bot.answer_callback_query(call.id, "تم وضعك في المعتذرة ❌")
        else:
            bot.answer_callback_query(call.id, "يجب التسجيل أولاً")
    elif call.data == "read":
        if name in roles:
            roles[name] = "قرأت ✅"
            bot.answer_callback_query(call.id, "تم تسجيل القراءة ✅")
        else:
            bot.answer_callback_query(call.id, "يجب التسجيل أولاً")

    # تحديث الرسالة
    if message_id and chat_id:
        bot.edit_message_text(build_list(), chat_id, message_id, reply_markup=keyboard())

# تشغيل البوت
threading.Thread(target=bot.infinity_polling).start()
 
