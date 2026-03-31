from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime

# ضع التوكن هنا
TOKEN = "8647146626:AAFxKmo5-j4PanRK1kLDZsaaXiM7LeTVv2k"

# بيانات
readers = []
listeners = []
apologizers = []
waiting = {}

def get_buttons():
    keyboard = [
        [InlineKeyboardButton("📝 سجل اسمي", callback_data="reg")],
        [InlineKeyboardButton("👂 مستمعة", callback_data="lis")],
        [InlineKeyboardButton("📖 قرأت", callback_data="rea")],
        [InlineKeyboardButton("❌ معتذرة", callback_data="apo")],
        [InlineKeyboardButton("🗑 امسح اسمي", callback_data="del")],
    ]
    return InlineKeyboardMarkup(keyboard)

def show_list():
    d = datetime.now().strftime("%d/%m/%Y")
    msg = f"📅 {d}\n\n📖 *قرأت:*\n"
    msg += "\n".join([f"• {x}" for x in readers]) if readers else "لا يوجد\n"
    msg += "\n👂 *مستمعة:*\n"
    msg += "\n".join([f"• {x}" for x in listeners]) if listeners else "لا يوجد\n"
    msg += "\n❌ *معتذرة:*\n"
    msg += "\n".join([f"• {x}" for x in apologizers]) if apologizers else "لا يوجد"
    return msg

async def start(update, context):
    await update.message.reply_text(show_list(), reply_markup=get_buttons(), parse_mode='Markdown')

async def stop_list(update, context):
    await update.message.reply_text("⏹ تم إيقاف الأدوار")

async def delete_list(update, context):
    global readers, listeners, apologizers
    readers = []
    listeners = []
    apologizers = []
    await update.message.reply_text("🗑 تم مسح القائمة")

async def register(update, context):
    q = update.callback_query
    await q.answer()
    waiting[q.from_user.id] = "reg"
    await q.edit_message_text("✏️ أرسل اسمك:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="cancel")]]))

async def listen(update, context):
    q = update.callback_query
    await q.answer()
    waiting[q.from_user.id] = "lis"
    await q.edit_message_text("✏️ أرسل اسمك:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="cancel")]]))

async def read(update, context):
    q = update.callback_query
    await q.answer()
    waiting[q.from_user.id] = "rea"
    await q.edit_message_text("✏️ أرسل اسمك:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="cancel")]]))

async def apologize(update, context):
    q = update.callback_query
    await q.answer()
    waiting[q.from_user.id] = "apo"
    await q.edit_message_text("✏️ أرسل اسمك:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="cancel")]]))

async def delete_me(update, context):
    q = update.callback_query
    await q.answer()
    waiting[q.from_user.id] = "del"
    await q.edit_message_text("✏️ أرسل الاسم:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="cancel")]]))

async def handle_message(update, context):
    uid = update.effective_user.id
    if uid not in waiting:
        return
    
    act = waiting[uid]
    name = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    if act == "reg":
        if name in readers + listeners + apologizers:
            await update.message.reply_text("⚠️ الاسم موجود")
        else:
            readers.append(name)
            await update.message.reply_text(f"✅ تم تسجيل {name}")
    
    elif act == "lis":
        if name in readers:
            readers.remove(name)
            listeners.append(name)
            await update.message.reply_text(f"👂 {name} مستمعة")
        elif name in apologizers:
            apologizers.remove(name)
            listeners.append(name)
            await update.message.reply_text(f"👂 {name} مستمعة")
        else:
            await update.message.reply_text("⚠️ غير موجود")
    
    elif act == "rea":
        if name in listeners:
            listeners.remove(name)
            readers.append(name)
            await update.message.reply_text(f"📖 {name} قرأت")
        elif name in apologizers:
            apologizers.remove(name)
            readers.append(name)
            await update.message.reply_text(f"📖 {name} قرأت")
        else:
            await update.message.reply_text("⚠️ غير موجود")
    
    elif act == "apo":
        if name in readers:
            readers.remove(name)
            apologizers.append(name)
            await update.message.reply_text(f"❌ {name} معتذرة")
        elif name in listeners:
            listeners.remove(name)
            apologizers.append(name)
            await update.message.reply_text(f"❌ {name} معتذرة")
        else:
            await update.message.reply_text("⚠️ غير موجود")
    
    elif act == "del":
        if name in readers:
            readers.remove(name)
            await update.message.reply_text(f"🗑 حذف {name}")
        elif name in listeners:
            listeners.remove(name)
            await update.message.reply_text(f"🗑 حذف {name}")
        elif name in apologizers:
            apologizers.remove(name)
            await update.message.reply_text(f"🗑 حذف {name}")
        else:
            await update.message.reply_text("⚠️ غير موجود")
    
    del waiting[uid]
    await context.bot.send_message(chat_id, show_list(), reply_markup=get_buttons(), parse_mode='Markdown')

async def cancel(update, context):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if uid in waiting:
        del waiting[uid]
    await q.edit_message_text(show_list(), reply_markup=get_buttons(), parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stoplist", stop_list))
    app.add_handler(CommandHandler("deleteList", delete_list))
    
    app.add_handler(CallbackQueryHandler(register, pattern="^reg$"))
    app.add_handler(CallbackQueryHandler(listen, pattern="^lis$"))
    app.add_handler(CallbackQueryHandler(read, pattern="^rea$"))
    app.add_handler(CallbackQueryHandler(apologize, pattern="^apo$"))
    app.add_handler(CallbackQueryHandler(delete_me, pattern="^del$"))
    app.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
