# -*- coding: utf-8 -*-
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import filetype

# -------- إعدادات البوت --------
TOKEN = "8203080422:AAFYxonm0YHcrK6k3IDGcrkbrvAt3xBCGEg"
ADMIN_ID = 8335018015  # رقم أدمن تيليجرام
WHATSAPP_NUMBER = "+201118061407"

# -------- إعداد اللوج --------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# -------- القوائم --------
main_menu = [['📢 بلاغ', '📞 التواصل معنا']]
report_menu = [['إلغاء']]

# -------- قائمة البلاغات --------
reports = []

# -------- دوال البوت --------
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "أهلاً بك في البوت!",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(f"للتواصل معنا: {WHATSAPP_NUMBER}")

def get_reports(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        update.message.reply_text("غير مسموح لك بهذا الأمر!")
        return
    if not reports:
        update.message.reply_text("لا توجد أي بلاغات حتى الآن.")
        return
    report_text = "\n\n".join([f"الاسم: {r['name']}\nرقم الهاتف: {r['phone']}\nأسبوع المشكلة: {r['week']}" for r in reports])
    update.message.reply_text(f"جميع البلاغات:\n\n{report_text}")

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat_id

    # -------- التعامل مع الإلغاء --------
    if text == "إلغاء":
        context.user_data.clear()
        update.message.reply_text(
            "تم إلغاء العملية. توجه إلى القائمة الرئيسية.",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )
        return

    if text == '📢 بلاغ':
        update.message.reply_text("ادخل الاسم:", reply_markup=ReplyKeyboardMarkup(report_menu, resize_keyboard=True))
        context.user_data['step'] = 'name'
    elif text == '📞 التواصل معنا':
        update.message.reply_text(f"تقدر تتواصل على واتس آب: {WHATSAPP_NUMBER}")
    elif 'step' in context.user_data:
        step = context.user_data['step']
        if step == 'name':
            context.user_data['name'] = text
            update.message.reply_text("ادخل رقم الهاتف (رمز الدولة +20):", reply_markup=ReplyKeyboardMarkup(report_menu, resize_keyboard=True))
            context.user_data['step'] = 'phone'
        elif step == 'phone':
            phone_number = text
            if not phone_number.startswith("+20"):
                phone_number = "+20" + phone_number
            context.user_data['phone'] = phone_number
            update.message.reply_text("ادخل أسبوع المشكلة:", reply_markup=ReplyKeyboardMarkup(report_menu, resize_keyboard=True))
            context.user_data['step'] = 'week'
        elif step == 'week':
            context.user_data['week'] = text
            # حفظ البلاغ
            report_entry = {
                "name": context.user_data['name'],
                "phone": context.user_data['phone'],
                "week": context.user_data['week']
            }
            reports.append(report_entry)
            # إرسال البلاغ للأدمن
            report_msg = f"تم استلام بلاغ:\n\nالاسم: {report_entry['name']}\nرقم الهاتف: {report_entry['phone']}\nأسبوع المشكلة: {report_entry['week']}"
            context.bot.send_message(chat_id=ADMIN_ID, text=report_msg)
            update.message.reply_text("تم إرسال البلاغ! توجه إلى القائمة الرئيسية.", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))
            context.user_data.clear()

def handle_photo(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    photo_file.download("user_photo.jpg")

    kind = filetype.guess("user_photo.jpg")
    if kind is None:
        update.message.reply_text("الصورة غير صالحة")
    else:
        update.message.reply_text(f"تم استلام الصورة: {kind.mime}")

# -------- تشغيل البوت --------
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("sheet_log", get_reports))  # أمر الأدمن لعرض البلاغات
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
dp.add_handler(MessageHandler(Filters.photo, handle_photo))

updater.start_polling()
print("البوت شغال الآن...")
updater.idle()