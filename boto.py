from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- BOT TOKEN ---
TOKEN = "8496354252:AAEtknBNNJEl0y_Jg0J_IOXnOnBeBDOm-30"

# --- Products (Demo) ---
products = [
    {"id": 1, "name": "Berserk outfit", "price": 130000, "img": "bers.png"},
    {"id": 2, "name": "Compression shirt", "price": 80000, "img": "comp.png"},
]

# --- /start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Бүтээгдэхүүн", callback_data="products")],
        [InlineKeyboardButton("📞 Холбоо барих", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Манай дэлгүүрт тавтай морил! 🤖 Та доорх цэсээс сонгоно уу:",
        reply_markup=reply_markup
    )

# --- Button actions ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "products":
        for p in products:
            with open(p["bers.png"], "rb") as img:
                await query.message.reply_photo(
                    img,
                    caption=f"{p['name']}\nҮнэ: {p['price']}₮\nБарааг захиалахын тулд /order_{p['id']} гэж бичнэ үү"
                )

    elif query.data == "contact":
        await query.message.reply_text(
            "📞 Утас: 99119911\n🏬 Хаяг: Улаанбаатар, СБД\n🌐 Вэб: www.shop.mn"
        )

# --- /order command ---
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Жишээ: /order_1 гэж бичвэл product id 1-г сонгосон болно
    text = update.message.text
    try:
        product_id = int(text.split("_")[1])
        product = next((p for p in products if p["id"] == product_id), None)
        if product:
            await update.message.reply_text("✍️ Нэрээ бичнэ үү:")
            context.user_data["order"] = {"product": product}
        else:
            await update.message.reply_text("Бараа олдсонгүй.")
    except:
        await update.message.reply_text("Алдаа гарлаа. Жишээ: /order_1")

# --- Capture user name for order ---
async def capture_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "order" in context.user_data:
        context.user_data["order"]["name"] = update.message.text
        await update.message.reply_text("Утасны дугаараа бичнэ үү:")

# --- Capture phone ---
async def capture_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "order" in context.user_data and "name" in context.user_data["order"]:
        context.user_data["order"]["phone"] = update.message.text
        product = context.user_data["order"]["product"]
        # Админд мэдэгдэл (ADMIN_ID-г өөрийн Telegram id-р соль)
        ADMIN_ID = 123456789
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Шинэ захиалга ирлээ!\nБараа: {product['name']}\nНэр: {context.user_data['order']['name']}\nУтас: {context.user_data['order']['phone']}"
        )
        await update.message.reply_text("Таны захиалга бүртгэгдлээ. 🙏 Баярлалаа!")
        context.user_data.clear()

# --- Main function ---
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_name))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_phone))

    print("🤖 Shop bot ажиллаж эхэллээ...")
    app.run_polling()

if __name__ == "__main__":
    main()
