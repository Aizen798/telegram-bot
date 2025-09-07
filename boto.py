from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler
)
import os

# --- BOT TOKEN & ADMIN ID ---
TOKEN = os.environ.get("BOT_TOKEN")  # Render дээр нэмсэн BOT_TOKEN
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5907197742"))  # өөрийн Telegram ID

# --- States for ConversationHandler ---
NAME, PHONE = range(2)

# --- Products (Demo) ---
products = [
    {"id": 1, "name": "Berserk outfit", "price": 130000, "img": "bers.png"},
    {"id": 2, "name": "Compression shirt", "price": 80000, "img": "comp.png"},
]

# --- /start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Оргинал хувцаснууд", callback_data="products")],
        [InlineKeyboardButton("📞 Холбоо барих", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Манай онлайн шопд тавтай морил! 🤖 Хөөе чи доорх гал хувцаснуудаас захиал!:",
        reply_markup=reply_markup
    )

# --- Button actions ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "products":
        for p in products:
            img_path = f"./images/{p['img']}"  # Render-д image folder
            try:
                with open(img_path, "rb") as img:
                    await query.message.reply_photo(
                        img,
                        caption=f"{p['name']}\nҮнэ: {p['price']}₮\nБарааг өөрийн болгохын тулд👉🏿 /order_{p['id']} гэж явуул хөөрхөнөө❤️ "
                    )
            except FileNotFoundError:
                await query.message.reply_text(f"Image {p['img']} олдсонгүй.")

    elif query.data == "contact":
        await query.message.reply_text(
            "📞 Утас: 91803699\n🏬 Хаяг: Диваажин, СБД\n🌐 Вэб: https://facebook.com/dtuguldur1"
        )

# --- /order command ---
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        product_id = int(text.split("_")[1])
        product = next((p for p in products if p["id"] == product_id), None)
        if product:
            context.user_data["order"] = {"product": product}
            await update.message.reply_text("✍️ Нэрээ бичнэ үү:")
            return NAME
        else:
            await update.message.reply_text("Бараа олдсонгүй.")
            return ConversationHandler.END
    except:
        await update.message.reply_text("Алдаа гарлаа. Жишээ: /order_1")
        return ConversationHandler.END

# --- Capture user name ---
async def capture_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["name"] = update.message.text
    await update.message.reply_text("Утасны дугаараа бичнэ үү:")
    return PHONE

# --- Capture phone number ---
async def capture_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order"]["phone"] = update.message.text
    product = context.user_data["order"]["product"]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Шинэ захиалга ирлээ!\n"
             f"Бараа: {product['name']}\n"
             f"Нэр: {context.user_data['order']['name']}\n"
             f"Утас: {context.user_data['order']['phone']}"
    )

    await update.message.reply_text("Таны захиалгыг авлаа Данс Xacbank: iban-85003200 5006050144 Нэр:Төгөлдөр Баяртогох Thank you fineshy😹t!")
    context.user_data.clear()
    return ConversationHandler.END

# --- Main function ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # /start
    app.add_handler(CommandHandler("start", start))

    # Button callback
    app.add_handler(CallbackQueryHandler(button_handler))

    # Conversation for /order_1, /order_2 ...
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^/order_\d+"), order)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_phone)],
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)

    print("🤖 Shop bot ажиллаж эхэллээ...")
    app.run_polling()

if __name__ == "__main__":
    main()
