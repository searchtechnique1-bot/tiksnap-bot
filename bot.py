import logging
import httpx
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = '8846697145:AAHSEbJmLqPq9e9MDeyPhk9MDilsR9J8KPA'
RAPIDAPI_KEY = '1d5f47a2b3msh0422d74dc9adb15p14469ejsn0cc8479c0662'
CHANNEL_ID = '-1003725750226'
CHANNEL_URL = 'https://t.me/tiksnaps'
WEBSITE_URL = 'https://www.tiksnaps.com/'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Membership စစ်ဆေးခြင်း
async def is_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# TikTok API ကနေ Video Link ယူခြင်း
async def get_tiktok_video(tiktok_url):
    api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
    }
    params = {"url": tiktok_url, "hd": "1"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=headers, params=params, timeout=20.0)
            data = response.json()
            if data.get("code") == 0:
                # No Watermark Video Link ကို ပြန်ပေးမယ်
                return data["data"]["play"]
            return None
        except Exception as e:
            logging.error(f"API Error: {e}")
            return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_subscribed(context, user_id):
        await update.message.reply_text("✨ **Welcome!** Just send me a TikTok link and I will send you the video without watermark.")
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)],
                    [InlineKeyboardButton("✅ Verify", callback_data='check')]]
        await update.message.reply_text("⚠️ **Access Denied!** Please join our channel to use this bot.", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text

    if not await is_subscribed(context, user_id):
        await start(update, context)
        return

    if "tiktok.com" in url:
        status_msg = await update.message.reply_text("⏳ **Processing...** Please wait.")
        video_url = await get_tiktok_video(url)
        
        if video_url:
            try:
                # Video ကို တန်းပို့ပေးမယ်
                await update.message.reply_video(
                    video=video_url, 
                    caption=f"✨ **Downloaded via @tikdown_snaps_bot**\n\n🌍 Use our website for more: {WEBSITE_URL}"
                )
                await status_msg.delete()
            except Exception as e:
                await status_msg.edit_text("❌ **Failed to send video.** Please try again or use our website.")
        else:
            await status_msg.edit_text("❌ **Error:** Could not find the video. Make sure the link is valid and public.")
    else:
        await update.message.reply_text("❗ Please send a valid TikTok link.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(context, query.from_user.id):
        await query.edit_message_text("✅ **Verified!** Now you can send me any TikTok link.")
    else:
        await query.answer("❌ Join the channel first!", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern='check'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("TikSnap Downloader Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
