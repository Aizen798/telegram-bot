import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters, ConversationHandler
)

# --- BOT TOKEN & ADMIN IDs ---
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = int(os.environ.get("ADMIN_ID", "5907197742"))  # Олон админ бол list болгож болно

# --- States ---
NAME, PHONE = range(2)

# --- Load products dynamically ---
with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

# --- Start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Products", callback_data="products")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! Choose an option below:",
        reply_markup=reply_markup
    )

# --- Button handler ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "products":
        tasks = []
        for p in products:
            img_path = f"./images/{p.get('img', 'default.png')}"
            try:
                with open(img_path, "rb") as img:
                    tasks.append(
                        query.message.reply_photo(
                            img,
                            caption=f"{p['name']}\nPrice: {p['price']}₮\n/order_{p['id']}"
                        )
                    )
            except FileNotFoundError:
                await query.message.reply_text(f"Image {p.get('img', 'default.png')} not found.")
        await asyncio.gather(*tasks)

    elif query.data == "contact":
        await query.message.reply_text(
            "📞 Phone: 91803699\n🏬 Address: DIVA\n🌐 Web: https://facebook.com/dtuguldur1"
        )

# --- Order conversation ---
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        product_id = int(text.split("_")[1])
        product = next((p for p in products if p["id"] == product_id), None)
        if product:
            context.user_data["order"] = {"product": product}
            await update.message.reply_text("Enter your name:")
            return NAME
        else:
            await update.message.reply_text("Product not found.")
            return ConversationHandler.END
    except:
        await update.message.reply_text("Use /order_1 or /order_2 etc.")
        return ConversationHandler.END

# --- Capture name ---
async def capture_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if not name.isalpha():
        await update.message.reply_text("Name must contain only letters. Try again:")
        return NAME
    context.user_data["order"]["name"] = name
    await update.message.reply_text("Enter phone number:")
    return PHONE

# --- Capture phone ---
async def capture_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not phone.isdigit() or not 8 <= len(phone) <= 10:
        await update.message.reply_text("Phone must be 8-10 digits. Try again:")
        return PHONE
    context.user_data["order"]["phone"] = phone
    product = context.user_data["order"]["product"]

    # Send to admins
    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"New order!\nProduct: {product['name']}\nName: {context.user_data['order']['name']}\nPhone: {phone}"
        )

    # Log order
    with open("orders.json", "a", encoding="utf-8") as f:
        json.dump(context.user_data["order"], f, ensure_ascii=False)
        f.write("\n")

    await update.message.reply_text(
        "Order received! Payment info: Xacbank: 5006050144 Name:Tuguldur ✅"
    )
    context.user_data.clear()
    return ConversationHandler.END

# --- Main function ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^/order_\d+"), order)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_phone)],
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
