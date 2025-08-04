import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Config
BOT_TOKEN = "8025238786:AAFFe7tNp03c4Cr8fWy6Tie-EdIGHpzIqfY"
CHANNEL_ID = "@curpasideldfwffa"

# Logging
logging.basicConfig(level=logging.INFO)

# States
NAME, JSHSHIR, PASSPORT, PHONE, CHEK = range(5)

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Ism va familiyangizni kiriting:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🆔 JSHSHIR raqamingizni kiriting:")
    return JSHSHIR

async def get_jshshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["jshshir"] = update.message.text
    await update.message.reply_text("📄 Passport seriya va raqamini kiriting:")
    return PASSPORT

async def get_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["passport"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("💳 To‘lov chek rasmini yuboring:")
    return CHEK

async def get_chek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Iltimos, faqat rasm yuboring.")
        return CHEK

    photo_file = update.message.photo[-1].file_id

    # User info
    user_data = context.user_data
    caption = (
        f"🧾 Yangi so‘rov!\n\n"
        f"👤 Ism: {user_data['name']}\n"
        f"🆔 JSHSHIR: {user_data['jshshir']}\n"
        f"📄 Passport: {user_data['passport']}\n"
        f"📞 Telefon: {user_data['phone']}"
    )

    # Send to channel
    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=photo_file,
        caption=caption
    )

    await update.message.reply_text("✅ Ma’lumotlaringiz muvaffaqiyatli yuborildi!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Jarayon bekor qilindi.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            JSHSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_jshshir)],
            PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_passport)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CHEK: [MessageHandler(filters.PHOTO, get_chek)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("Bot ishlayapti...")
    app.run_polling()
