import logging
import httpx
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = '8846697145:AAHSEbJmLqPq9e9MDeyPhk9MDilsR9J8KPA'
CHANNEL_ID = '-1003725750226'
CHANNEL_URL = 'https://t.me/tiksnaps'
WEBSITE_URL = 'https://www.tiksnaps.com/?utm_source=telegram&utm_medium=bot'

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)

db = {}

def get_user(user_id):
    today = datetime.now().strftime('%Y-%m-%d')
    if user_id not in db:
        db[user_id] = {'daily_date': today, 'daily_count': 0, 'invites': 0, 'bonus': 0, 'referred_by': None, 'is_new': True}
    if db[user_id]['daily_date'] != today:
        db[user_id]['daily_date'] = today
        db[user_id]['daily_count'] = 0
    return db[user_id]

async def is_subscribed(context, user_id):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Subscription Error: {e}")
        return False

# Public API - Key လုံးဝ မလိုဘဲ TikTok Video/Photo ယူပေးမည့် Function
async def fetch_tiktok_data(tiktok_url):
    api_url = "https://www.tikwm.com/api/"
    async with httpx.AsyncClient() as client:
        try:
            # API Key မပါဘဲ တိုက်ရိုက်ခေါ်ယူခြင်း
            res = await client.get(api_url, params={"url": tiktok_url, "hd": 1}, timeout=30.0)
            result = res.json()
            if result.get("code") == 0:
                return result.get("data")
            return None
        except Exception as e:
            logging.error(f"Fetch Error: {e}")
            return None

async def send_invite_info(update_or_query, user_id):
    invite_link = f"https://t.me/tikdown_snaps_bot?start={user_id}"
    share_url = f"https://t.me/share/url?url={invite_link}&text=Download%20TikTok%20videos%20without%20watermark!%20🚀"
    
    text = (
        "🎁 **Want +5 Bonus Downloads?**\n\n"
        "1️⃣ Copy your link below or click Share.\n"
        "2️⃣ Send it to your friends.\n"
        "3️⃣ When 3 friends join, you get **+5 extra downloads**! 🎁\n\n"
        f"🔗 **Your Link:** `{invite_link}`\n"
        "*(Tap the link to copy)*"
    )
    keyboard = [[InlineKeyboardButton("🚀 Share with Friends", url=share_url)],
                [InlineKeyboardButton("🌐 Go to Website (Unlimited)", url=WEBSITE_URL)]]
    
    if hasattr(update_or_query, 'message') and update_or_query.message:
        await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update_or_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if context.args and user.get('is_new'):
        try:
            referrer_id = int(context.args[0])
            if referrer_id != user_id:
                if referrer_id not in db: get_user(referrer_id)
                db[referrer_id]['invites'] += 1
                if db[referrer_id]['invites'] % 3 == 0:
                    db[referrer_id]['bonus'] += 5
                    await context.bot.send_message(chat_id=referrer_id, text="🎉 **CONGRATS!** 3 friends joined! You got **+5 Bonus Downloads**! 🎁")
        except: pass
    
    user['is_new'] = False
    if await is_subscribed(context, user_id):
        msg = f"👋 **Welcome!**\n📊 Today: {user['daily_count']} / {5 + user['bonus']}\n🌟 Bonus: +{user['bonus']} downloads"
        keyboard = [[InlineKeyboardButton("🚀 Web: Unlimited Download", url=WEBSITE_URL)],
                    [InlineKeyboardButton("🎁 Get +5 Bonus Downloads", callback_data='invite_info')]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)], [InlineKeyboardButton("✅ Verify", callback_data='check')]]
        await update.message.reply_text("⚠️ **Please JOIN our channel first!**", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text
    if not await is_subscribed(context, user_id):
        await start(update, context)
        return

    if "tiktok.com" in url:
        user = get_user(user_id)
        max_allowed = 5 + user['bonus']
        if user['daily_count'] >= max_allowed:
            await send_invite_info(update, user_id)
            return

        status_msg = await update.message.reply_text("⏳ **Processing...**")
        data = await fetch_tiktok_data(url)

        if not data:
            await status_msg.edit_text(f"❌ **Error!** Video not found.\nPlease use our website: {WEBSITE_URL}")
            return

        kb = [[InlineKeyboardButton("🎵 Download MP3 Audio", url=WEBSITE_URL)],
              [InlineKeyboardButton("🎁 Get +5 Bonus Downloads", callback_data='invite_info')]]
        
        try:
            # Slideshow Photos ရှိမရှိ အရင်စစ်မယ်
            if data.get("images"):
                media_group = [InputMediaPhoto(img) for img in data["images"][:10]]
                await update.message.reply_media_group(media=media_group)
                await update.message.reply_text(f"📸 **Done!** ({user['daily_count']+1}/{max_allowed})\n🌐 {WEBSITE_URL}", reply_markup=InlineKeyboardMarkup(kb))
            # Video ရှိမရှိ စစ်မယ်
            elif data.get("play"):
                await update.message.reply_video(video=data["play"], caption=f"🎬 **Done!** ({user['daily_count']+1}/{max_allowed})\n🌐 Website: {WEBSITE_URL}", reply_markup=InlineKeyboardMarkup(kb))
            
            user['daily_count'] += 1
            await status_msg.delete()
        except:
            await status_msg.edit_text(f"❌ Failed! Use website: {WEBSITE_URL}")
    else:
        await update.message.reply_text("❗ Send a valid TikTok link.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'check':
        if await is_subscribed(context, query.from_user.id):
            await query.edit_message_text("✅ Verified! Send your link.")
        else: await query.answer("❌ Join the channel first!", show_alert=True)
    elif query.data == 'invite_info':
        await send_invite_info(query, query.from_user.id)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("TikSnap Bot is running forever...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
