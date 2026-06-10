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
    except: return False

async def fetch_tiktok_data(tiktok_url):
    api_url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
    headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"}
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(api_url, headers=headers, params={"url": tiktok_url, "hd": "1"}, timeout=25.0)
            return res.json().get("data") if res.json().get("code") == 0 else None
        except: return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if context.args and user.get('is_new'):
        referrer_id = int(context.args[0])
        if referrer_id != user_id and referrer_id in db:
            user['referred_by'] = referrer_id
            db[referrer_id]['invites'] += 1
            if db[referrer_id]['invites'] % 3 == 0:
                db[referrer_id]['bonus'] += 5
                try: await context.bot.send_message(chat_id=referrer_id, text="🎉 **SUCCESS!**\n3 Friends Joined! You got **+5 Bonus** downloads! 🎁")
                except: pass
            else:
                count_needed = 3 - (db[referrer_id]['invites'] % 3)
                try: await context.bot.send_message(chat_id=referrer_id, text=f"👤 **1 Friend Joined!**\nNeed {count_needed} more for Bonus! 🎁")
                except: pass
    
    user['is_new'] = False

    if await is_subscribed(context, user_id):
        invite_link = f"https://t.me/tikdown_snaps_bot?start={user_id}"
        msg = (
            f"👋 **Welcome to TikSnaps!**\n\n"
            f"🎁 **Daily Free:** 5\n"
            f"🌟 **Your Bonus:** +{user['bonus']}\n"
            f"📊 **Used Today:** {user['daily_count']} / {5 + user['bonus']}\n\n"
            f"🔗 **Your Invite Link:**\n`{invite_link}`\n\n"
            f"(Invite 3 Friends = Get +5 Bonus! 🎁)"
        )
        keyboard = [[InlineKeyboardButton("🚀 Web: UNLIMITED Download", url=WEBSITE_URL)]]
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
            invite_link = f"https://t.me/tikdown_snaps_bot?start={user_id}"
            await update.message.reply_text(
                f"❌ **LIMIT REACHED!** ({user['daily_count']}/{max_allowed})\n\n"
                f"1️⃣ **Invite 3 Friends** for +5 more:\n`{invite_link}`\n\n"
                f"2️⃣ **Use our Website** (No Limit!):\n🚀 {WEBSITE_URL}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Go to Website", url=WEBSITE_URL)]]),
                parse_mode='Markdown'
            )
            return

        status_msg = await update.message.reply_text("⏳ **Processing...**\n🚀 [tiksnaps.com](https://www.tiksnaps.com)", disable_web_page_preview=True, parse_mode='Markdown')
        data = await fetch_tiktok_data(url)

        if not data:
            await status_msg.edit_text("❌ **Error!** Video not found.")
            return

        invite_link = f"https://t.me/tikdown_snaps_bot?start={user_id}"
        kb = [[InlineKeyboardButton("🎵 Download MP3 Audio", url=WEBSITE_URL)],
              [InlineKeyboardButton("🎁 Get +5 Bonus Downloads", url=f"https://t.me/share/url?url={invite_link}&text=Download%20TikTok%20videos%20without%20watermark!")] ]
        
        try:
            if data.get("images"):
                media_group = [InputMediaPhoto(img) for img in data["images"][:10]]
                await update.message.reply_media_group(media=media_group)
                await update.message.reply_text(f"📸 **Done!** ({user['daily_count']+1}/{max_allowed})\n🌐 {WEBSITE_URL}", reply_markup=InlineKeyboardMarkup(kb))
            elif data.get("play"):
                await update.message.reply_video(video=data["play"], caption=f"🎬 **Done!** ({user['daily_count']+1}/{max_allowed})\n🌐 {WEBSITE_URL}", reply_markup=InlineKeyboardMarkup(kb))
            
            user['daily_count'] += 1
            await status_msg.delete()
        except:
            await status_msg.edit_text(f"❌ **Failed!** Use website: {WEBSITE_URL}")
    else:
        await update.message.reply_text("❗ **Please send a TikTok link.**")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_subscribed(context, query.from_user.id):
        await query.edit_message_text("✅ **Verified!** Send your link.")
    else:
        await query.answer("❌ Join the channel first!", show_alert=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern='check'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
