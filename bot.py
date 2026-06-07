import logging
import httpx
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = '8846697145:AAHSEbJmLqPq9e9MDeyPhk9MDilsR9J8KPA'
RAPIDAPI_KEY = '1d5f47a2b3msh0422d74dc9adb15p14469ejsn0cc8479c0662'
CHANNEL_ID = '-1003725750226'
CHANNEL_URL = 'https://t.me/tiksnaps'
WEBSITE_URL = 'https://www.tiksnaps.com/'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# User Usage Tracking (ဒါက Memory ထဲမှာပဲ သိမ်းမှာပါ၊ Bot restart ကျရင် ပြန် Reset ဖြစ်ပါမယ်)
user_data = {}

def get_daily_count(user_id):
    today = datetime.now().strftime('%Y-%m-%d')
    if user_id not in user_data or user_data[user_id]['date'] != today:
        user_data[user_id] = {'date': today, 'count': 0}
    return user_data[user_id]['count']

def increment_count(user_id):
    user_data[user_id]['count'] += 1

async def is_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# API မှ Data ယူခြင်း (Video ရော Photo ပါ ရအောင်)
async def fetch_tiktok_data(tiktok_url):
    api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
    headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"}
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(api_url, headers=headers, params={"url": tiktok_url, "hd": "1"}, timeout=20.0)
            return res.json().get("data") if res.json().get("code") == 0 else None
        except: return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_subscribed(context, user_id):
        await update.message.reply_text("👋 **Welcome!**\nSend me a TikTok link.\n\n🎁 Bot Limit: 5 per day\n🚀 Website: UNLIMITED!")
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)], [InlineKeyboardButton("✅ Verify", callback_data='check')]]
        await update.message.reply_text("⚠️ **Join our channel first!**", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text
    if not await is_subscribed(context, user_id):
        await start(update, context)
        return

    if "tiktok.com" in url:
        count = get_daily_count(user_id)
        
        # --- LIMIT CHECK (5 Videos) ---
        if count >= 5:
            keyboard = [[InlineKeyboardButton("🚀 Go to Website (UNLIMITED)", url=WEBSITE_URL)]]
            await update.message.reply_text(
                "❌ **DAILY LIMIT REACHED!** (5/5)\n\n"
                "You can download more on our website!\n\n"
                "👇 CLICK BELOW 👇",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # --- PROCESSING AD ---
        status_msg = await update.message.reply_text(
            "⏳ **Processing...**\n\n"
            "📺 **Video Quality: HD**\n"
            "🌍 **Web:** [tiksnaps.com](https://www.tiksnaps.com)\n"
            "🎁 *Unlimited downloads on website!*",
            disable_web_page_preview=True, parse_mode='Markdown'
        )

        data = await fetch_tiktok_data(url)
        if not data:
            await status_msg.edit_text("❌ Error! Try again or use website.")
            return

        # MP3 Button (Always goes to website)
        kb = [[InlineKeyboardButton("🎵 Download MP3 Audio", url=WEBSITE_URL)],
              [InlineKeyboardButton("🚀 Unlimited Downloads", url=WEBSITE_URL)]]
        
        try:
            # CASE 1: Video
            if data.get("play"):
                await update.message.reply_video(video=data["play"], caption=f"✅ Done! ({count+1}/5 Today)\n\n🌐 {WEBSITE_URL}", reply_markup=InlineKeyboardMarkup(kb))
            
            # CASE 2: Photos (Slideshow)
            elif data.get("images"):
                media_group = [InputMediaPhoto(img) for img in data["images"][:10]] # ပထမ ၁၀ ပုံပဲ ပို့မယ် (Telegram limit)
                await update.message.reply_media_group(media=media_group)
                await update.message.reply_text(f"✅ Photo Slideshow Done! ({count+1}/5)\n\n🌐 {WEBSITE_URL}", reply_markup=InlineKeyboardMarkup(kb))
            
            increment_count(user_id)
            await status_msg.delete()
        except:
            await status_msg.edit_text(f"❌ Failed! Use website: {WEBSITE_URL}")
    else:
        await update.message.reply_text("❗ Please send a TikTok link.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(context, query.from_user.id):
        await query.edit_message_text("✅ Verified! Send your link.")
    else:
        await query.answer("❌ Join the channel first!", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern='check'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("TikSnap Bot with Limits is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
