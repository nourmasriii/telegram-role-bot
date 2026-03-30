import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تخزين البيانات
users_data = {
    'readers': [],      # قائمة المسجلات للقراءة
    'listeners': [],    # قائمة المستمعات
    'apologizers': []   # قائمة المعتذرات
}

# تخزين طلبات تسجيل الاسم المؤقتة
pending_registrations = {}

# الأزرار الرئيسية
def get_main_keyboard():
    """الأزرار الرئيسية كما في الصورة"""
    keyboard = [
        [InlineKeyboardButton("📝 سجل اسمي", callback_data="register")],
        [InlineKeyboardButton("👂 مستمع", callback_data="listener")],
        [InlineKeyboardButton("📖 قرأت", callback_data="reader")],
        [InlineKeyboardButton("❌ معتذرة", callback_data="apologize")],
        [InlineKeyboardButton("🗑 احذف اسمي", callback_data="delete_me")],
    ]
    return InlineKeyboardMarkup(keyboard)

# أمر بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب وعرض الحالة الحالية"""
    user = update.effective_user
    
    # حساب الإحصائيات
    readers_count = len(users_data['readers'])
    listeners_count = len(users_data['listeners'])
    apologizers_count = len(users_data['apologizers'])
    
    # الحصول على التاريخ الهجري (تقريبي)
    current_date = datetime.now().strftime("%d %B %Y")
    
    welcome_message = f"""
🌟 *احفظ معنا القرآن بالتكرار* 🌟

*{current_date}*

*المسجلات للقراءة:* 
{format_list(users_data['readers']) if users_data['readers'] else 'لا توجد مسجلات للقراءة'}

*المستمعات:* 
{format_list(users_data['listeners']) if users_data['listeners'] else 'لا توجد مستمعات'}

*المعتذرات:* 
{format_list(users_data['apologizers']) if users_data['apologizers'] else 'لا توجد معتذرات'}

---
✨ *{get_random_ayah()}* ✨

_تلاوة وتدبّر!_ 📖
"""
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )

def format_list(items):
    """تنسيق القائمة للعرض"""
    return "\n".join([f"• {item}" for item in items])

def get_random_ayah():
    """آيات تحفيزية متنوعة"""
    ayahs = [
        "وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِرٍ",
        "إِنَّ هَٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ",
        "وَنُنَزِّلُ مِنَ الْقُرْآنِ مَا هُوَ شِفَاءٌ وَرَحْمَةٌ لِّلْمُؤْمِنِينَ",
        "الَّذِينَ آمَنُوا وَتَطْمَئِنُّ قُلُوبُهُم بِذِكْرِ اللَّهِ ۗ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ",
        "فَاذْكُرُونِي أَذْكُرْكُمْ وَاشْكُرُوا لِي وَلَا تَكْفُرُونِ"
    ]
    import random
    return random.choice(ayahs)

# طلب تسجيل الاسم
async def request_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب اسم المستخدم للتسجيل"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    pending_registrations[user_id] = True
    
    await query.edit_message_text(
        "✏️ *أرسل اسمك الثلاثي أو اسمك الذي تريد التسجيل به*\n\n"
        "مثال: سارة محمد أحمد\n\n"
        "_سيتم إضافتك إلى قائمة المسجلات للقراءة_",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
        ])
    )

# معالجة الاسم المرسل
async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الاسم المرسل من المستخدم"""
    user_id = update.effective_user.id
    
    if user_id not in pending_registrations:
        # ليس في وضع التسجيل، نعرض القائمة الرئيسية
        await update.message.reply_text(
            "استخدم الأزرار للتفاعل مع البوت:",
            reply_markup=get_main_keyboard()
        )
        return
    
    name = update.message.text.strip()
    
    # التحقق من عدم تكرار الاسم
    all_names = users_data['readers'] + users_data['listeners'] + users_data['apologizers']
    if name in all_names:
        await update.message.reply_text(
            f"⚠️ الاسم '{name}' مسجل مسبقاً!\n"
            f"الرجاء استخدام اسم مختلف أو استخدام 'احذف اسمي' أولاً.",
            reply_markup=get_main_keyboard()
        )
        del pending_registrations[user_id]
        return
    
    # إضافة الاسم إلى قائمة القراء
    users_data['readers'].append(name)
    del pending_registrations[user_id]
    
    # عرض الحالة المحدثة
    await update.message.reply_text(
        f"✅ *تم تسجيل اسمك بنجاح*\n\n"
        f"الاسم: {name}\n"
        f"القائمة: المسجلات للقراءة 📖\n\n"
        f"يمكنك تحديث حالتك باستخدام الأزرار:",
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )
    
    # إرسال التحديث الكامل للمجموعة (اختياري)
    await send_full_update(context, update.effective_chat.id)

# تسجيل كمستمع
async def set_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحويل المستخدم من قارئ إلى مستمع"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # نحتاج لمعرفة اسم المستخدم - سنطلب منه إرسال اسمه
    await query.edit_message_text(
        "👂 *للتسجيل كمستمع*\n\n"
        "الرجاء إرسال اسمك كما هو مسجل في القائمة:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
        ])
    )
    
    # تخزين أن المستخدم يريد التسجيل كمستمع
    pending_registrations[user_id] = "listener"

# تسجيل كقارئ (قرأت)
async def set_reader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحويل المستخدم إلى قارئ"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    await query.edit_message_text(
        "📖 *للتسجيل كقارئ (قرأت)*\n\n"
        "الرجاء إرسال اسمك كما هو مسجل في القائمة:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
        ])
    )
    
    pending_registrations[user_id] = "reader"

# تسجيل كمعتذرة
async def set_apologizer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحويل المستخدم إلى معتذرة"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    await query.edit_message_text(
        "❌ *للتسجيل كمعتذرة*\n\n"
        "الرجاء إرسال اسمك كما هو مسجل في القائمة:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
        ])
    )
    
    pending_registrations[user_id] = "apologizer"

# معالجة تغيير الحالة بناءً على الاسم
async def handle_status_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة تغيير حالة المستخدم بناءً على الاسم المرسل"""
    user_id = update.effective_user.id
    
    if user_id not in pending_registrations:
        return
    
    action = pending_registrations[user_id]
    if action in ["listener", "reader", "apologizer"]:
        name = update.message.text.strip()
        
        # البحث عن الاسم في القوائم
        found = False
        old_status = None
        
        # البحث في قائمة القراء
        if name in users_data['readers']:
            users_data['readers'].remove(name)
            found = True
            old_status = "قارئ"
        # البحث في قائمة المستمعين
        elif name in users_data['listeners']:
            users_data['listeners'].remove(name)
            found = True
            old_status = "مستمع"
        # البحث في قائمة المعتذرين
        elif name in users_data['apologizers']:
            users_data['apologizers'].remove(name)
            found = True
            old_status = "معتذرة"
        
        if not found:
            await update.message.reply_text(
                f"⚠️ الاسم '{name}' غير موجود في القوائم!\n"
                f"الرجاء التأكد من الاسم أو التسجيل أولاً باستخدام 'سجل اسمي'.",
                reply_markup=get_main_keyboard()
            )
            del pending_registrations[user_id]
            return
        
        # إضافة إلى القائمة الجديدة
        if action == "listener":
            users_data['listeners'].append(name)
            new_status = "مستمع 👂"
        elif action == "reader":
            users_data['readers'].append(name)
            new_status = "قارئ 📖"
        elif action == "apologizer":
            users_data['apologizers'].append(name)
            new_status = "معتذرة ❌"
        
        del pending_registrations[user_id]
        
        await update.message.reply_text(
            f"✅ *تم تحديث حالتك*\n\n"
            f"الاسم: {name}\n"
            f"الحالة السابقة: {old_status}\n"
            f"الحالة الجديدة: {new_status}\n\n"
            f"جزاك الله خيراً",
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
        
        await send_full_update(context, update.effective_chat.id)

# حذف اسم المستخدم
async def delete_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف اسم المستخدم من جميع القوائم"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🗑 *لحذف اسمك*\n\n"
        "الرجاء إرسال اسمك كما هو مسجل:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data="cancel")]
        ])
    )
    
    pending_registrations[query.from_user.id] = "delete"

# معالجة حذف الاسم
async def handle_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف الاسم من جميع القوائم"""
    user_id = update.effective_user.id
    
    if user_id not in pending_registrations or pending_registrations[user_id] != "delete":
        return
    
    name = update.message.text.strip()
    found = False
    
    # البحث والحذف من جميع القوائم
    if name in users_data['readers']:
        users_data['readers'].remove(name)
        found = True
    if name in users_data['listeners']:
        users_data['listeners'].remove(name)
        found = True
    if name in users_data['apologizers']:
        users_data['apologizers'].remove(name)
        found = True
    
    del pending_registrations[user_id]
    
    if found:
        await update.message.reply_text(
            f"🗑 *تم حذف اسمك بنجاح*\n\n"
            f"الاسم: {name}\n"
            f"تم حذفه من جميع القوائم.\n\n"
            f"يمكنك التسجيل مرة أخرى باستخدام 'سجل اسمي'",
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
        await send_full_update(context, update.effective_chat.id)
    else:
        await update.message.reply_text(
            f"⚠️ الاسم '{name}' غير موجود في القوائم!",
            reply_markup=get_main_keyboard()
        )

# إلغاء العملية
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء العملية الحالية"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id in pending_registrations:
        del pending_registrations[user_id]
    
    # عرض الحالة الحالية
    readers_count = len(users_data['readers'])
    listeners_count = len(users_data['listeners'])
    apologizers_count = len(users_data['apologizers'])
    
    current_status = f"""
📋 *الحالة الحالية*

📖 المسجلات للقراءة: {readers_count}
👂 المستمعات: {listeners_count}
❌ المعتذرات: {apologizers_count}

_يمكنك استخدام الأزرار أدناه_
"""
    
    await query.edit_message_text(
        current_status,
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )

# أوامر الإدارة
async def show_full_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض القائمة الكاملة"""
    message = "📊 *التقرير الكامل*\n\n"
    
    message += f"📖 *المسجلات للقراءة ({len(users_data['readers'])}):*\n"
    message += format_list(users_data['readers']) if users_data['readers'] else "لا يوجد\n"
    
    message += f"\n👂 *المستمعات ({len(users_data['listeners'])}):*\n"
    message += format_list(users_data['listeners']) if users_data['listeners'] else "لا يوجد\n"
    
    message += f"\n❌ *المعتذرات ({len(users_data['apologizers'])}):*\n"
    message += format_list(users_data['apologizers']) if users_data['apologizers'] else "لا يوجد\n"
    
    message += f"\n👥 *الإجمالي:* {len(users_data['readers']) + len(users_data['listeners']) + len(users_data['apologizers'])}"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def clear_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسح جميع القوائم"""
    global users_data
    users_data = {
        'readers': [],
        'listeners': [],
        'apologizers': []
    }
    await update.message.reply_text(
        "🗑 *تم مسح جميع القوائم بنجاح*",
        parse_mode='Markdown'
    )

async def send_full_update(context, chat_id):
    """إرسال تحديث كامل للمجموعة"""
    readers_count = len(users_data['readers'])
    listeners_count = len(users_data['listeners'])
    apologizers_count = len(users_data['apologizers'])
    
    update_message = f"""
🔄 *تحديث القائمة*

📖 المسجلات للقراءة: {readers_count}
👂 المستمعات: {listeners_count}
❌ المعتذرات: {apologizers_count}

{get_random_ayah()}
"""
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=update_message,
        parse_mode='Markdown'
    )

# أمر إحصائيات سريع
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات سريعة"""
    total = len(users_data['readers']) + len(users_data['listeners']) + len(users_data['apologizers'])
    stats_message = f"""
📈 *إحصائيات الختمة*

📖 قارئات: {len(users_data['readers'])}
👂 مستمعات: {len(users_data['listeners'])}
❌ معتذرات: {len(users_data['apologizers'])}
👥 المجموع: {total}

_بارك الله فيكم جميعاً_
"""
    await update.message.reply_text(stats_message, parse_mode='Markdown')

def main():
    """تشغيل البوت"""
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        logger.error("لم يتم العثور على التوكن. يرجى إضافة TELEGRAM_BOT_TOKEN في ملف .env")
        print("❌ يرجى إضافة التوكن في ملف .env")
        return
    
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # أوامر البوت
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("list", show_full_list))
    application.add_handler(CommandHandler("clear", clear_all))
    
    # معالجات الأزرار
    application.add_handler(CallbackQueryHandler(request_name, pattern="^register$"))
    application.add_handler(CallbackQueryHandler(set_listener, pattern="^listener$"))
    application.add_handler(CallbackQueryHandler(set_reader, pattern="^reader$"))
    application.add_handler(CallbackQueryHandler(set_apologizer, pattern="^apologize$"))
    application.add_handler(CallbackQueryHandler(delete_me, pattern="^delete_me$"))
    application.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))
    
    # معالجات الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 البوت يعمل...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع الرسائل النصية"""
    user_id = update.effective_user.id
    
    if user_id in pending_registrations:
        action = pending_registrations[user_id]
        
        if action is True:  # تسجيل اسم جديد
            await handle_name(update, context)
        elif action in ["listener", "reader", "apologizer"]:
            await handle_status_change(update, context)
        elif action == "delete":
            await handle_delete(update, context)
    else:
        # رسالة عادية، نعرض القائمة
        await update.message.reply_text(
            "استخدم الأزرار للتفاعل مع البوت:",
            reply_markup=get_main_keyboard()
        )

if __name__ == "__main__":
    main()
