import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from helper.helper_func import encode
from datetime import datetime

#===============================================================#

@Client.on_message(filters.private & ~filters.command([
    'start', 'shortner', 'users', 'broadcast', 'batch', 'genlink', 'stats', 
    'pbroadcast', 'db', 'adddb', 'add_db', 'removedb', 'rm_db',
    'ban', 'unban', 'addpremium', 'delpremium', 'premiumusers', 
    'request', 'profile'
]))
async def channel_post(client: Client, message: Message):
    # Only admins can use this
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    reply_text = await message.reply_text("Please wait... ⏳", quote=True)

    try:
        # Copy message to database channel
        post_message = await message.copy(chat_id=client.db, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(chat_id=client.db, disable_notification=True)
    except Exception as e:
        print(e)
        return await reply_text.edit_text("❌ Something went wrong!")

    # Use message ID + date for unique link encoding
    today_str = datetime.now().strftime("%Y%m%d")
    string = f"get-{today_str}{post_message.id}"
    base64_string = await encode(string)

    # Create shareable link
    link = f"https://krpicture1.blogspot.com?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    await reply_text.edit(
        f"<b>✅ Here is your link:</b>\n\n{link}",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

    if not client.disable_btn:
        try:
            await post_message.edit_reply_markup(reply_markup)
        except Exception as e:
            print(e)

#===============================================================#

@Client.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    # Ensure only database channel posts are handled
    if message.chat.id != client.db:
        return
    if client.disable_btn:
        return

    today_str = datetime.now().strftime("%Y%m%d")
    string = f"get-{today_str}{message.id}"
    base64_string = await encode(string)
    link = f"https://krpicture1.blogspot.com?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
