import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION (အချက်အလက်အမှန်များ) ---
TOKEN = '8846697145:AAHSEbJmLqPq9e9MDeyPhk9MDilsR9J8KPA'
CHANNEL_ID = '-1003725750226'  # မင်းအရင်ပေးထားတဲ့ Channel ID
CHANNEL_URL = 'https://t.me/tiksnaps'
WEBSITE_URL = 'https://www.tiksnaps.com/'

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# User Join/မJoin စစ်ဆေးခြင်း
async def is_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Membership check error: {e}")
        return False

# Website သို့ သွားရန် စာသား
ACCESS_GRANTED_TEXT = (
    "✅ **Success! Membership Verified.**\n\n"
    "You can now use TikSnaps to download your favorite TikTok videos without watermark.\n\n"
    "🚀 **Download Link:**\n"
    "Click the button below to open our website and start downloading."
)

# Channel Join ရန် တောင်းဆိုသည့် စာသား
JOIN_REQUIRED_TEXT = (
    "⚠️ **Join Required!**\n\n"
    "To use this bot, you must be a member of our official update channel.\n\n"
    "1️⃣ Join the channel via the button below.\n"
    "2️⃣ After joining, click the **Verify** button."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if await is_subscribed(context, user_id):
        # Join ထားပြီးသားသူများအတွက် Website Button ပြမည်
        keyboard = [[InlineKeyboardButton("🚀 Go to TikSnaps Website", url=WEBSITE_URL)]]
        await update.message.reply_text(
            ACCESS_GRANTED_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        # မ Join ရသေးသူများအတွက် Join Button ပြမည်
        keyboard = [
            [InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ Verify My Join", callback_data='check')]
        ]
        await update.message.reply_text(
            JOIN_REQUIRED_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if await is_subscribed(context, query.from_user.id):
        keyboard = [[InlineKeyboardButton("🚀 Go to TikSnaps Website", url=WEBSITE_URL)]]
        await query.edit_message_text(
            ACCESS_GRANTED_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        # Join မလုပ်သေးဘဲ နှိပ်ရင် Message ပြမည်
        await query.answer("❌ You haven't joined yet! Please join the channel first.", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern='check'))
    
    # User က ဘာပဲပို့ပို့ Join ထားလား စစ်မည်
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    
    print("TikSnap Global Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
