import os
import asyncio
import threading
from flask import Flask
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler, CallbackQueryHandler
)

# === CONFIGURATION ===
BOT_TOKEN = "8025238786:AAEle3_zq8Iz7Gt1GwzicPKLAYLPdrIVIrQ"
ADMIN_CHANNEL_USERNAME = "@curpasideldfwffa"
ADMIN_ID = 8062273832

# === STATES ===
(ASK_NAME, ASK_PHONE, ASK_PASSPORT, ASK_JSHSHIR, ASK_DIPLOM_PHOTO, ASK_RECEIPT) = range(6)

user_data = {}

# === COMMAND: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {}
    await update.message.reply_text("👤 To'liq ism-sharifingizni kiriting:")
    return ASK_NAME

# === ASK NAME ===
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['name'] = update.message.text
    contact_btn = KeyboardButton("📞 Raqamni yuborish", request_contact=True)
    markup = ReplyKeyboardMarkup([[contact_btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("📱 Telefon raqamingizni yuboring:", reply_markup=markup)
    return ASK_PHONE

# === ASK PHONE ===
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    contact = update.message.contact
    phone = contact.phone_number if contact else update.message.text
    user_data[user_id]['phone'] = phone
    await update.message.reply_text("🛂 Pasport seriya va raqamini kiriting (AA1234567):", reply_markup=None)
    return ASK_PASSPORT

# === ASK PASSPORT ===
async def ask_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['passport'] = update.message.text
    await update.message.reply_text("🔢 JSHSHIR raqamingizni kiriting:")
    return ASK_JSHSHIR

# === ASK JSHSHIR ===
async def ask_jshshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]['jshshir'] = update.message.text
    await update.message.reply_text("📸 Iltimos, diplom suratini yuboring (sifatli bo‘lishi kerak):")
    return ASK_DIPLOM_PHOTO

# === ASK DIPLOM PHOTO ===
async def ask_diplom_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.photo:
        user_data[user_id]['diplom_photo'] = update.message.photo[-1].file_id
        await update.message.reply_text(
            "💳 20 000 so'm to‘lovni ushbu karta raqamiga o‘tkazing: \n\n💳 *9860 2566 0118 3567*\n\n"
            "So‘ng kvitansiya (check) rasmini yuboring.",
            parse_mode="Markdown"
        )
        return ASK_RECEIPT
    else:
        await update.message.reply_text("❗ Iltimos, diplom suratini yuboring.")
        return ASK_DIPLOM_PHOTO

# === ASK RECEIPT PHOTO ===
async def ask_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.photo:
        check_photo = update.message.photo[-1].file_id
        diplom_photo = user_data[user_id].get('diplom_photo')

        caption = (
            f"📥 Yangi ariza\n\n"
            f"👤 Ism: {user_data[user_id]['name']}\n"
            f"📞 Tel: {user_data[user_id]['phone']}\n"
            f"🛂 Pasport: {user_data[user_id]['passport']}\n"
            f"🔢 JSHSHIR: {user_data[user_id]['jshshir']}\n"
            f"👤 Username: @{update.effective_user.username or 'yo‘q'}\n"
            f"🆔 ID: {user_id}"
        )

        media = [
            InputMediaPhoto(media=diplom_photo, caption="🎓 Diplom surati"),
            InputMediaPhoto(media=check_photo, caption=caption),
        ]

        await context.bot.send_media_group(chat_id=ADMIN_CHANNEL_USERNAME, media=media)

        # 🎓 Diplomni tasdiqlash tugmasi
        button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎓 Diplomni tasdiqlash", callback_data="confirm_diplom")]
        ])
        await update.message.reply_text(
            "✅ Ma'lumotlaringiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.",
            reply_markup=button
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("❗ Iltimos, kvitansiya (check) suratini yuboring.")
        return ASK_RECEIPT

# === CALLBACK BUTTON HANDLER ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirm_diplom":
        await query.message.reply_text("🔄 Qaytadan boshlaymiz...")
        await start(update, context)

# === CANCEL ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

# === CONVERSATION HANDLER ===
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        ASK_PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, ask_phone)],
        ASK_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_passport)],
        ASK_JSHSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_jshshir)],
        ASK_DIPLOM_PHOTO: [MessageHandler(filters.PHOTO, ask_diplom_photo)],
        ASK_RECEIPT: [MessageHandler(filters.PHOTO, ask_receipt)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# === FLASK SERVER ===
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Bot va server ishlayapti."

# === ASYNC BOT START FUNCTION ===
async def run_bot_async():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Telegram bot ishga tushdi...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.wait()

# === ENTRY POINT ===
def start():
    flask_thread = threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))))
    flask_thread.start()

    loop = asyncio.get_event_loop()
    loop.create_task(run_bot_async())
    loop.run_forever()

if __name__ == "__main__":
    start()

