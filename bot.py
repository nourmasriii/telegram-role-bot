from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime

# ضع التوكن هنا
TOKEN = "8647146626:AAFxKmo5-j4PanRK1kLDZsaaXiM7LeTVv2k"

# تخزين البيانات
readers = []
listeners = []
apologizers = []
waiting_for_name = {}

def get_buttons():
    keyboard = [
        [InlineKeyboardButton("📝 سجل اسمي", callback_data="register")],
        [InlineKeyboardButton("👂 مستمعة", callback_data="listen")],
        [InlineKeyboardButton("📖 قرأت", callback_data="read")],
        [InlineKeyboardButton("❌ معتذرة", callback_data="apologize")],
        [InlineKeyboardButton("🗑 امسح اسمي", callback_data="delete")],
    ]
    return InlineKeyboardMarkup(keyboard)

def show_list():
    date = datetime.now().strftime("%d/%m/%Y")
    msg = f"📅 {date}\n\n"
    msg += "📖 *قرأت:*\n"
    if readers:
        for r in readers:
            msg += f"• {r}\n"
    else:
        msg += "لا يوجد\n"
    msg += "\n👂 *مستمعة:*\n"
    if listeners:
        for l in listeners:
            msg += f"• {l}\n"
    else:
        msg += "لا يوجد\n"
    msg += "\n❌ *معتذرة:*\n"
    if apologizers:
        for a in apologizers:
            msg += f"• {a}\n"
    else:
        msg += "لا يوجد"
    return msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(show_list(), reply_markup=get_buttons(), parse_mode='Markdown')

async def stop_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏹ تم إيقاف الأدوار")

async def delete_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global readers, listeners, apologizers
    readers = []
    listeners = []
    apologizers = []
    await update.message.reply_text("🗑 تم مسح القائمة")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    waiting_for_name[q.from_user.id] = "register"
    keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]]
    await q.edit_message_text("✏️ أرسل اسمك:", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    waiting_for_name[q.from_user.id] = "listen"
    keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]]
    await q.edit_message_text("✏️ أرسل اسمك:", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    waiting_for_name[q.from_user.id] = "read"
    keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]]
    await q.edit_message_text("✏️ أرسل اسمك:", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_apologize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    waiting_for_name[q.from_user.id] = "apologize"
    keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]]
    await q.edit_message_text("✏️ أرسل اسمك:", reply_markup=InlineKeyboardMarkup(keyboard))

async def delete_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    waiting_for_name[q.from_user.id] = "delete"
    keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]]
    await q.edit_message_text("✏️ أرسل الاسم:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in waiting_for_name:
        return
    
    action = waiting_for_name[uid]
    name = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    if action == "register":
        if name in readers or name in listeners or name in apologizers:
            await update.message.reply_text("⚠️ الاسم موجود مسبقاً")
        else:
            readers.append(name)
            await update.message.reply_text(f"✅ تم تسجيل {name} في قائمة القراءة")
    
    elif action == "listen":
        if name in readers:
            readers.remove(name)
            listeners.append(name)
            await update.message.reply_text(f"👂 تم نقل {name} إلى المستمعات")
        elif name in apologizers:
            apologizers.remove(name)
            listeners.append(name)
            await update.message.reply_text(f"👂 تم نقل {name} إلى المستمعات")
        elif name in listeners:
            await update.message.reply_text(f"⚠️ {name} موجود بالفعل")
        else:
            await update.message.reply_text(f"⚠️ {name} غير موجود")
    
    elif action == "read":
        if name in listeners:
            listeners.remove(name)
            readers.append(name)
            await update.message.reply_text(f"📖 تم نقل {name} إلى القراءة")
        elif name in apologizers:
            apologizers.remove(name)
            readers.append(name)
            await update.message.reply_text(f"📖 تم نقل {name} إلى القراءة")
        elif name in readers:
            await update.message.reply_text(f"⚠️ {name} موجود بالفعل")
        else:
            await update.message.reply_text(f"⚠️ {name} غير موجود")
    
    elif action == "apologize":
        if name in readers:
            readers.remove(name)
            apologizers.append(name)
            await update.message.reply_text(f"❌ تم نقل {name} إلى المعتذرات")
        elif name in listeners:
            listeners.remove(name)
            apologizers.append(name)
            await update.message.reply_text(f"❌ تم نقل {name} إلى المعتذرات")
        elif name in apologizers:
            await update.message.reply_text(f"⚠️ {name} موجود بالفعل")
        else:
            await update.message.reply_text(f"⚠️ {name} غير موجود")
    
    elif action == "delete":
        if name in readers:
            readers.remove(name)
            await update.message.reply_text(f"🗑 تم حذف {name}")
        elif name in listeners:
            listeners.remove(name)
            await update.message.reply_text(f"🗑 تم حذف {name}")
        elif name in apologizers:
            apologizers.remove(name)
            await update.message.reply_text(f"🗑 تم حذف {name}")
        else:
            await update.message.reply_text(f"⚠️ {name} غير موجود")
    
    del waiting_for_name[uid]
    await context.bot.send_message(chat_id, show_list(), reply_markup=get_buttons(), parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if uid in waiting_for_name:
        del waiting_for_name[uid]
    await q.edit_message_text(show_list(), reply_markup=get_buttons(), parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stoplist", stop_list))
    app.add_handler(CommandHandler("deleteList", delete_list))
    
    app.add_handler(CallbackQueryHandler(register, pattern="^register$"))
    app.add_handler(CallbackQueryHandler(set_listen, pattern="^listen$"))
    app.add_handler(CallbackQueryHandler(set_read, pattern="^read$"))
    app.add_handler(CallbackQueryHandler(set_apologize, pattern="^apologize$"))
    app.add_handler(CallbackQueryHandler(delete_name, pattern="^delete$"))
    app.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
