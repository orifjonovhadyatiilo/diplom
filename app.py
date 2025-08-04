import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

BOT_TOKEN = "8025238786:AAFFe7tNp03c4Cr8fWy6Tie-EdIGHpzIqfY"
ADMIN_ID = 8062273832
CHANNEL_USERNAME = "@curpasideldfwffa"  # ommaviy kanal username

# Bosqichlar
(ASK_NAME, ASK_PASSPORT, ASK_JSHSHIR, ASK_PHONE, ASK_RECEIPT) = range(5)

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom! Ariza topshirish uchun ismingizni va familiyangizni kiriting:")
    return ASK_NAME

async def ask_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("🪪 Passport seriya va raqamingizni kiriting (masalan: AA1234567):")
    return ASK_PASSPORT

async def ask_jshshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["passport"] = update.message.text.strip()
    await update.message.reply_text("🔢 JSHSHIR raqamingizni kiriting:")
    return ASK_JSHSHIR

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["jshshir"] = update.message.text.strip()
    await update.message.reply_text("📱 Telefon raqamingizni kiriting:")
    return ASK_PHONE

async def ask_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text.strip()
    await update.message.reply_text("💳 20,000 so‘mni ushbu karta raqamiga to‘lang:\n\n9860 2566 0118 3567 (HUMO)\n\nSo‘ngra to‘lov chek rasmini yuboring:")
    return ASK_RECEIPT

async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    caption = (
        f"📥 Yangi ariza:\n"
        f"👤 Ism: {context.user_data['name']}\n"
        f"🪪 Passport: {context.user_data['passport']}\n"
        f"🔢 JSHSHIR: {context.user_data['jshshir']}\n"
        f"📞 Telefon: {context.user_data['phone']}"
    )

    # Kanal chat_id sini username orqali olish
    chat = await context.bot.get_chat(CHANNEL_USERNAME)
    channel_id = chat.id

    # Kanalga yuborish
    await context.bot.send_photo(
        chat_id=channel_id,
        photo=photo.file_id,
        caption=caption
    )

    await update.message.reply_text("✅ Arizangiz qabul qilindi! Tez orada siz bilan bog‘lanamiz.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Jarayon bekor qilindi.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_passport)],
            ASK_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_jshshir)],
            ASK_JSHSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_receipt)],
            ASK_RECEIPT: [MessageHandler(filters.PHOTO, receive_receipt)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
