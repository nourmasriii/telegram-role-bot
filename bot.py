import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ضع التوكن هنا
TOKEN = "8647146626:AAFxKmo5-j4PanRK1kLDZsaaXiM7LeTVv2k"

# تخزين البيانات
readers = []      # قرأت
listeners = []    # مستمعة
apologizers = []  # معتذرة

# انتظار الاسم للتسجيل
waiting_for_name = {}

# الأزرار
def get_buttons():
    keyboard = [
        [InlineKeyboardButton("📝 سجل اسمي", callback_data="register")],
        [InlineKeyboardButton("👂 مستمعة", callback_data="listen")],
        [InlineKeyboardButton("📖 قرأت", callback_data="read")],
        [InlineKeyboardButton("❌ معتذرة", callback_data="apologize")],
        [InlineKeyboardButton("🗑 امسح اسمي", callback_data="delete")],
    ]
    return InlineKeyboardMarkup(keyboard)

# عرض القائمة الرئيسية
def show_list():
    date = datetime.now().strftime("%d/%m/%Y")
    
    msg = f"📅 {date}\n\n"
    msg += "📖 *قرأت:*\n"
    msg += "\n".join([f"• {r}" for r in readers]) if readers else "لا يوجد\n"
    msg += "\n👂 *مستمعة:*\n"
    msg += "\n".join([f"• {l}" for l in listeners]) if listeners else "لا يوجد\n"
    msg += "\n❌ *معتذرة:*\n"
    msg += "\n".join([f"• {a}" for a in apologizers]) if apologizers else "لا يوجد"
    
    return msg

# أمر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        show_list(),
        reply_markup=get_buttons(),
        parse_mode='Markdown'
    )

# أمر إيقاف الأدوار
async def stop_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏹ تم إيقاف الأدوار")

# أمر مسح القائمة
async def delete_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global readers, listeners, apologizers
    readers = []
    listeners = []
    apologizers = []
    await update.message.reply_text("🗑 تم مسح القائمة")

# سجل اسمي
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    waiting_for_name[user_id] = "register"
    
    await query.edit_message_text(
        "✏️ أرسل اسمك:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]])
    )

# مستمعة
async def set_listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    waiting_for_name[user_id] = "listen"
    
    await query.edit_message_text(
        "✏️ أرسل اسمك:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]])
    )

# قرأت
async def set_read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    waiting_for_name[user_id] = "read"
    
    await query.edit_message_text(
        "✏️ أرسل اسمك:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]])
    )

# معتذرة
async def set_apologize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    waiting_for_name[user_id] = "apologize"
    
    await query.edit_message_text(
        "✏️ أرسل اسمك:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]])
    )

# امسح اسمي
async def delete_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    waiting_for_name[user_id] = "delete"
    
    await query.edit_message_text(
        "✏️ أرسل الاسم المراد حذفه:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]])
    )

# معالجة الأسماء
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in waiting_for_name:
        await update.message.reply_text(
            show_list(),
            reply_markup=get_buttons(),
            parse_mode='Markdown'
        )
        return
    
    action = waiting_for_name[user_id]
    name = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # سجل اسمي
    if action == "register":
        if name in readers or name in listeners or name in apologizers:
            await update.message.reply_text("⚠️ الاسم موجود مسبقاً")
        else:
            readers.append(name)
            await update.message.reply_text(f"✅ تم تسجيل {name} في قائمة القراءة")
    
    # مستمعة
    elif action == "listen":
        if name in readers:
            readers.remove(name)
            listeners.append(name)
            await update.message.reply_text(f"👂 تم نقل {name} إلى قائمة المستمعات")
        elif name in apologizers:
            apologizers.remove(name)
            listeners.append(name)
            await update.message.reply_text(f"👂 تم نقل {name} إلى قائمة المستمعات")
        elif name in listeners:
            await update.message.reply_text(f"⚠️ {name} موجود بالفعل في قائمة المستمعات")
        else:
            await update.message.reply_text(f"⚠️ {name} غير موجود في القوائم")
    
    # قرأت
    elif action == "read":
        if name in listeners:
            listeners.remove(name)
            readers.append(name)
            await update.message.reply_text(f"📖 تم نقل {name} إلى قائمة القراءة")
        elif name in apologizers:
            apologizers.remove(name)
            readers.append(name)
            await update.message.reply_text(f"📖 تم نقل {name} إلى قائمة القراءة")
        elif name in readers:
            await update.message.reply_text(f"⚠️ {name} موجود بالفعل في قائمة القراءة")
        else:
            await update.message.reply_text(f"⚠️ {name} غير موجود في القوائم")
    
    # معتذرة
    elif action == "apologize":
        if name in readers:
            readers.remove(name)
            apologizers.append(name)
            await update.message.reply_text(f"❌ تم نقل {name} إلى قائمة المعتذرات")
        elif name in listeners:
            listeners.remove(name)
            apologizers.append(name)
            await update.message.reply_text(f"❌ تم نقل {name} إلى قائمة المعتذرات")
        elif name in apologizers:
            await update.message.reply_text(f"⚠️ {name} موجود بالفعل في قائمة المعتذرات")
        else:
            await update.message.reply_text(f"⚠️ {name} غير موجود في القوائم")
    
    # امسح اسمي
    elif action == "delete":
        if name in readers:
            readers.remove(name)
            await update.message.reply_text(f"🗑 تم حذف {name} من القائمة")
        elif name in listeners:
            listeners.remove(name)
            await update.message.reply_text(f"🗑 تم حذف {name} من القائمة")
        elif name in apologizers:
            apologizers.remove(name)
            await update.message.reply_text(f"🗑 تم حذف {name} من القائمة")
        else:
            await update.message.reply_text(f"⚠️ {name} غير موجود")
    
    # حذف من انتظار الاسم
    if user_id in waiting_for_name:
        del waiting_for_name[user_id]
    
    # إرسال القائمة المحدثة
    await context.bot.send_message(
        chat_id=chat_id,
        text=show_list(),
        reply_markup=get_buttons(),
        parse_mode='Markdown'
    )

# إلغاء
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id in waiting_for_name:
        del waiting_for_name[user_id]
    
    await query.edit_message_text(
        show_list(),
        reply_markup=get_buttons(),
        parse_mode='Markdown'
    )

def main():
    # استخدام طريقة مبسطة بدون Updater
    from telegram.ext import Application
    
    app = Application.builder().token(TOKEN).build()
    
    # أوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stoplist", stop_list))
    app.add_handler(CommandHandler("deleteList", delete_list))
    
    # أزرار
    app.add_handler(CallbackQueryHandler(register, pattern="^register$"))
    app.add_handler(CallbackQueryHandler(set_listen, pattern="^listen$"))
    app.add_handler(CallbackQueryHandler(set_read, pattern="^read$"))
    app.add_handler(CallbackQueryHandler(set_apologize, pattern="^apologize$"))
    app.add_handler(CallbackQueryHandler(delete_name, pattern="^delete$"))
    app.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))
    
    # رسائل
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
