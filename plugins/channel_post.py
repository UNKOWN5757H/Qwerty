import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from helper.helper_func import encode
from config import LOGGER # Import your logger

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
        # Get primary DB channel ID safely
        db_channel_id = int(client.db)
    except (ValueError, TypeError):
        LOGGER(__name__, client.name).error("Primary DB Channel ID (client.db) is not set or invalid.")
        return await reply_text.edit_text("❌ Error: Primary DB channel is not configured correctly.")

    try:
        # Copy message to database channel
        post_message = await message.copy(chat_id=db_channel_id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(chat_id=db_channel_id, disable_notification=True)
    except Exception as e:
        LOGGER(__name__, client.name).error(f"Failed to copy message to DB channel: {e}")
        return await reply_text.edit_text("❌ Something went wrong while copying to DB channel.")

    # --- 💡 FIXED ENCODING ---
    # Use the same multiplier logic as genlink/batch
    string = f"get-{post_message.id * abs(db_channel_id)}"
    base64_string = await encode(string)

    # Create shareable link
    link = f"https://krpicture1.blogspot.com?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    await reply_text.edit(
        f"<b>✅ Here is your link:</b>\n\n<code>{link}</code>",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

    if not client.disable_btn:
        try:
            await post_message.edit_reply_markup(reply_markup)
        except Exception as e:
            LOGGER(__name__, client.name).warning(f"Failed to edit post_message reply markup: {e}")

#===============================================================#

@Client.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    
    # --- 💡 LOGIC FIX ---
    # Get all configured DB channel IDs
    all_db_ids = set()
    try:
        all_db_ids.add(int(client.db)) # Add primary
    except (ValueError, TypeError):
        LOGGER(__name__, client.name).error("Primary DB Channel ID (client.db) is not set or invalid in new_post.")
        
    db_channels = getattr(client, 'db_channels', {})
    for channel_id_str in db_channels.keys():
        try:
            all_db_ids.add(int(channel_id_str)) # Add secondaries
        except (ValueError, TypeError):
            pass # Ignore invalid entries

    # Ensure only configured database channel posts are handled
    if message.chat.id not in all_db_ids:
        return
        
    if client.disable_btn:
        return

    # --- 💡 FIXED ENCODING ---
    # Use the message's own channel ID as the multiplier
    source_channel_id = message.chat.id 
    string = f"get-{message.id * abs(source_channel_id)}"
    base64_string = await encode(string)
    link = f"https://krpicture1.blogspot.com?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        LOGGER(__name__, client.name).warning(f"Failed to edit new_post reply markup in {message.chat.id}: {e}")
        pass
