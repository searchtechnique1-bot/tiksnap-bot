import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = '8846697145:AAHSEbJmLqPq9e9MDeyPhk9MDilsR9J8KPA'
CHANNEL_ID = '-1003725750226' 
CHANNEL_URL = 'https://t.me/tiksnaps_com'
WEBSITE_URL = 'https://tiksnaps.com'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def is_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_subscribed(context, user_id):
        keyboard = [[InlineKeyboardButton("🚀 Go to Website", url=WEBSITE_URL)]]
        await update.message.reply_text("✅ Access Granted! Use the button below:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)],
                    [InlineKeyboardButton("✅ Verify", callback_data='check')]]
        await update.message.reply_text("⚠️ Join our channel first!", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(context, query.from_user.id):
        keyboard = [[InlineKeyboardButton("🚀 Open Website", url=WEBSITE_URL)]]
        await query.edit_message_text("✅ Success! Go to website:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.answer("❌ Join the channel first!", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern='check'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    
    print("Bot is running on Cloud...")
    # Render အတွက် အရေးကြီးသော အပိုင်း
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
