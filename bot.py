import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = '8846697145:AAHSEbJmLqPq9e9MDeyPhk9MDilsR9J8KPA'
CHANNEL_ID = '-1003725750226' 
CHANNEL_URL = 'https://t.me/tiksnaps_com'
WEBSITE_URL = 'https://tiksnaps.com'

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def is_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_subscribed(context, user_id):
        keyboard = [[InlineKeyboardButton("🚀 Go to Downloader Website", url=WEBSITE_URL)]]
        await update.message.reply_text(
            "✅ **Access Granted!**\nYou are part of our community. Click the button below to download TikTok videos without watermark.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📢 Join Announcement Channel", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ Verify (Check Join)", callback_data='check')]
        ]
        await update.message.reply_text(
            "⚠️ **Access Denied!**\n\nPlease join our announcement channel first to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(context, query.from_user.id):
        keyboard = [[InlineKeyboardButton("🚀 Open Website", url=WEBSITE_URL)]]
        await query.edit_message_text(
            "✅ **Verified Successfully!**\nYou can now use our TikTok downloader website. Enjoy!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.answer("❌ You still haven't joined the channel!", show_alert=True)

def main():
    # ဒီနေရာကနေ စပြီး အောက်ကစာကြောင်းတွေကို Space ၄ ချက်စီ ခွာထားရပါတယ်
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern='check'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    
    print("TikSnap Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()