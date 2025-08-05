import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

BOT_TOKEN = "8025238786:AAFFe7tNp03c4Cr8fWy6Tie-EdIGHpzIqfY"
ADMIN_CHANNEL_ID = -1002682564809

ASK_NAME, ASK_PHONE, ASK_PASSPORT, ASK_JSHSHIR, ASK_DIPLOM_PHOTO, ASK_RECEIPT = range(6)

user_data_dict = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ismingizni kiriting:")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Pasport seriya va raqamingizni kiriting:")
    return ASK_PASSPORT

async def ask_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['passport'] = update.message.text
    await update.message.reply_text("JSHSHIR raqamingizni kiriting:")
    return ASK_JSHSHIR

async def ask_jshshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['jshshir'] = update.message.text
    await update.message.reply_text("🎓 Diplom rasmini yuklang (sifatli bo‘lishi kerak):")
    return ASK_DIPLOM_PHOTO

async def ask_diplom_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    bio = BytesIO()
    await photo_file.download(out=bio)
    context.user_data['diplom'] = bio.getvalue()
    await update.message.reply_text("💳 To‘lov cheki fotosuratini yuboring:")
    return ASK_RECEIPT

async def ask_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    receipt_file = await update.message.photo[-1].get_file()
    receipt_bio = BytesIO()
    await receipt_file.download(out=receipt_bio)
    context.user_data['receipt'] = receipt_bio.getvalue()

    # Image processing
    diplom_img = Image.open(BytesIO(context.user_data['diplom']))
    receipt_img = Image.open(BytesIO(context.user_data['receipt']))

    width = max(diplom_img.width, receipt_img.width)
    total_height = diplom_img.height + receipt_img.height + 200

    new_img = Image.new("RGB", (width, total_height), "white")
    new_img.paste(diplom_img, (0, 0))
    new_img.paste(receipt_img, (0, diplom_img.height))

    # Add text
    draw = ImageDraw.Draw(new_img)
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)

    text_y = diplom_img.height + receipt_img.height + 10
    texts = [
        f"🧾 Ismi: {context.user_data['name']}",
        f"📞 Tel: {context.user_data['phone']}",
        f"🪪 Pasport: {context.user_data['passport']}",
        f"🆔 JSHSHIR: {context.user_data['jshshir']}",
        f"🎓 Diplom: Mavjud",
        f"👤 Username: @{update.effective_user.username or 'yo‘q'}",
        f"🆔 ID: {update.effective_user.id}"
    ]

    for text in texts:
        draw.text((10, text_y), text, font=font, fill="black")
        text_y += 35

    final_bio = BytesIO()
    new_img.save(final_bio, format="PNG")
    final_bio.seek(0)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 Diplomni tasdiqlash", callback_data="restart")]
    ])

    await context.bot.send_photo(
        chat_id=ADMIN_CHANNEL_ID,
        photo=final_bio,
        caption="📬 Yangi ariza",
        reply_markup=keyboard
    )

    await update.message.reply_text("✅ Arizangiz qabul qilindi. Yaqinda javob beramiz.")
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "restart":
        await context.bot.send_message(chat_id=query.from_user.id, text="/start buyrug'i yuborildi.")
        await context.bot.send_message(chat_id=query.from_user.id, text="/start")
        # optionally call start here

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_passport)],
            ASK_JSHSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_jshshir)],
            ASK_DIPLOM_PHOTO: [MessageHandler(filters.PHOTO, ask_diplom_photo)],
            ASK_RECEIPT: [MessageHandler(filters.PHOTO, ask_receipt)],
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

if __name__ == "__main__":
    main()

