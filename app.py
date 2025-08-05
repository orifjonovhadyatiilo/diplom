import os
from flask import Flask
import asyncio
import threading
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
)

# TOKEN
BOT_TOKEN = "8025238786:AAEle3_zq8Iz7Gt1GwzicPKLAYLPdrIVIrQ"
ADMIN_CHANNEL_USERNAME = "@curpasideldfwffa"  # ommaviy kanal username
ADMIN_ID = 8062273832

# States
(
    ASK_NAME, ASK_PHONE, ASK_PASSPORT, ASK_JSHSHIR,
    ASK_DIPLOM, ASK_RECEIPT
) = range(6)

# User data dictionary
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {}
    await update.message.reply_text("👤 To'liq ism-sharifingizni kiriting:")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['name'] = update.message.text
    contact_btn = KeyboardButton("📞 Raqamni yuborish", request_contact=True)
    markup = ReplyKeyboardMarkup([[contact_btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📱 Telefon raqamingizni yuboring:", reply_markup=markup)
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    contact = update.message.contact
    phone = contact.phone_number if contact else update.message.text
    user_data[user_id]['phone'] = phone
    await update.message.reply_text("🛂 Pasport seriya va raqamini kiriting (AA1234567):", reply_markup=None)
    return ASK_PASSPORT

async def ask_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['passport'] = update.message.text
    await update.message.reply_text("🔢 JSHSHIR raqamingizni kiriting:")
    return ASK_JSHSHIR

async def ask_jshshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['jshshir'] = update.message.text
    await update.message.reply_text("🎓 Diplom raqamingizni kiriting:")
    return ASK_DIPLOM

async def ask_diplom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['diplom'] = update.message.text
    await update.message.reply_text("💳 20 000 so'm to‘lovni ushbu karta raqamiga o‘tkazing: \n\n💳 *9860 2566 0118 3567*\n\nSo‘ng kvitansiya (check) rasmini yuboring.", parse_mode="Markdown")
    return ASK_RECEIPT

async def ask_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.photo:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        caption = (
            f"📥 Yangi ariza\n\n"
            f"👤 Ismi: {user_data[user_id]['name']}\n"
            f"📞 Tel: {user_data[user_id]['phone']}\n"
            f"🛂 Pasport: {user_data[user_id]['passport']}\n"
            f"🔢 JSHSHIR: {user_data[user_id]['jshshir']}\n"
            f"🎓 Diplom: {user_data[user_id]['diplom']}\n"
            f"👤 Username: @{update.effective_user.username or 'yo‘q'}\n"
            f"🆔 ID: {user_id}"
        )
        await context.bot.send_photo(
            chat_id=ADMIN_CHANNEL_USERNAME,
            photo=file_id,
            caption=caption
        )
        await update.message.reply_text("✅ Ma'lumotlaringiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("❗ Iltimos, kvitansiya fotosuratini yuboring.")
        return ASK_RECEIPT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

# ConversationHandler (boshqaruvchi)
conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        ASK_PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, ask_phone)],
        ASK_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_passport)],
        ASK_JSHSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_jshshir)],
        ASK_DIPLOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_diplom)],
        ASK_RECEIPT: [MessageHandler(filters.PHOTO, ask_receipt)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# Flask app
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot ishlayapti."

# Botni asosiy threadda ishga tushuramiz
async def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(conv)
    print("✅ Bot ishga tushdi...")
    await application.run_polling()

# Flask alohida threadda
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flask serverni threadda ishga tushuramiz
    threading.Thread(target=run_flask).start()
    # Telegram botni asosiy threadda ishga tushuramiz
    asyncio.run(run_bot())






