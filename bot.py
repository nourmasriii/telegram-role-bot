from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

readers = []
listeners = []
excused = []
done = []

def format_list(lst, checked=False):
    text = ""
    for i, name in enumerate(lst, 1):
        mark = "✅ " if name in done else ""
        text += f"{i}- {mark}{name}\n"
    return text if text else "لا يوجد"

def get_text():
    text = "🌙 المسجلات للقراءة:\n\n"
    text += format_list(readers)

    text += "\n🎧 المستمعات:\n"
    text += "\n".join(listeners) if listeners else "لا يوجد"

    text += "\n\n🌸 المعتذرات:\n"
    text += "\n".join(excused) if excused else "لا يوجد"

    return text

def get_buttons():
    keyboard = [
        [InlineKeyboardButton("✏️ سجل اسمي", callback_data="register")],
        [InlineKeyboardButton("❌ احذف اسمي", callback_data="remove")],
        [
            InlineKeyboardButton("🎧 مستمعة", callback_data="listener"),
            InlineKeyboardButton("🌸 معتذرة", callback_data="excuse"),
        ],
        [InlineKeyboardButton("✅ قرأت", callback_data="done")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_text(), reply_markup=get_buttons())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    name = query.from_user.first_name

    await query.answer()

    if query.data == "register":
        if name not in readers:
            readers.append(name)

    elif query.data == "remove":
        if name in readers:
            readers.remove(name)
        if name in listeners:
            listeners.remove(name)
        if name in excused:
            excused.remove(name)
        if name in done:
            done.remove(name)

    elif query.data == "listener":
        if name not in listeners:
            listeners.append(name)
        if name in readers:
            readers.remove(name)

    elif query.data == "excuse":
        if name not in excused:
            excused.append(name)
        if name in readers:
            readers.remove(name)

    elif query.data == "done":
        if name in readers and name not in done:
            done.append(name)

    await query.edit_message_text(get_text(), reply_markup=get_buttons())

app = ApplicationBuilder().token("8647146626:AAFxKmo5-j4PanRK1kLDZsaaXiM7LeTVv2k").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
