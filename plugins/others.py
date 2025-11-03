import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import MSG_EFFECT
from pyrogram.errors import ChatAdminRequired, UsernameInvalid, PeerIdInvalid, FloodWait

#===============================================================#
# Helper function to avoid code duplication
#===============================================================#

async def _get_db_management_panel(client: Client):
    """Generates the text and markup for the DB management panel."""
    db_channels = getattr(client, 'db_channels', {})
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    if db_channels:
        channel_list = []
        for channel_id_str, channel_data in db_channels.items():
            channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            is_primary = "✓ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
            is_active = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            channel_list.append(f"• `{channel_name}` (`{channel_id_str}`)\n  {is_primary} | {is_active}")
        
        channels_display = "\n\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    msg = f"""<blockquote>✦ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</blockquote>

›› **ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅʙ:** `{primary_db or 'None'}`
›› **ᴛᴏᴛᴀʟ ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{len(db_channels)}`

**ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:**
{channels_display}

__ᴜsᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs!__
"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db_channel')],
        [InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db_channel')],
        [InlineKeyboardButton('›› sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db')],
        [InlineKeyboardButton('›› ᴛᴏɢɢʟᴇ sᴛᴀᴛᴜs', 'toggle_db_status')],
        [InlineKeyboardButton('›› ᴠɪᴇᴡ ᴅᴇᴛᴀɪʟs', 'db_details')]
    ])
    
    return msg, reply_markup

#===============================================================#

@Client.on_message(filters.command('db') & filters.private)
async def db_channels_command(client: Client, message: Message):
    """Direct command to manage DB channels"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    msg, reply_markup = await _get_db_management_panel(client)
    await message.reply(msg, reply_markup=reply_markup)

#===============================================================#
# NOTE: Callback handlers for add_db_channel, rm_db_channel, set_primary_db, and toggle_db_status
# are implemented in settings.py to avoid conflicts. Only direct commands are handled here.
#===============================================================#

@Client.on_callback_query(filters.regex("^db_details$"))
async def db_details(client, query):
    """Show detailed information about DB channels"""
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    
    db_channels = getattr(client, 'db_channels', {})
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ ᴅᴇᴛᴀɪʟᴇᴅ ᴅʙ ᴄʜᴀɴɴᴇʟs ɪɴғᴏʀᴍᴀᴛɪᴏɴ</blockquote>

›› **ᴘʀɪᴍᴀʀʏ ᴅʙ ᴄʜᴀɴɴᴇʟ:** `{primary_db or 'None'}`
›› **ᴛᴏᴛᴀʟ ᴄᴏɴғɪɢᴜʀᴇᴅ:** `{len(db_channels)}`

"""
    
    if db_channels:
        for i, (channel_id_str, channel_data) in enumerate(db_channels.items(), 1):
            channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            is_primary = channel_data.get('is_primary', False)
            is_active = channel_data.get('is_active', True)
            added_by = channel_data.get('added_by', 'ᴜɴᴋɴᴏᴡɴ')
            
            status_emoji = "✓" if is_primary else "•"
            active_emoji = "✓" if is_active else "✗"
            
            msg += f"""**{i}. {channel_name}**
• **ɪᴅ:** `{channel_id_str}`
• **sᴛᴀᴛᴜs:** {status_emoji} {'ᴘʀɪᴍᴀʀʏ' if is_primary else 'sᴇᴄᴏɴᴅᴀʀʏ'}
• **ᴀᴄᴛɪᴠᴇ:** {active_emoji} {'ʏᴇs' if is_active else 'ɴᴏ'}
• **ᴀᴅᴅᴇᴅ ʙʏ:** `{added_by}`

"""
    else:
        msg += "_ɴᴏ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_\n\n"
    
    msg += """**✦ ɴᴏᴛᴇs:**
• ᴘʀɪᴍᴀʀʏ ᴄʜᴀɴɴᴇʟ ɪs ᴜsᴇᴅ ғɪʀsᴛ ғᴏʀ ʀᴇᴛʀɪᴇᴠɪɴɢ ғɪʟᴇs
• sᴇᴄᴏɴᴅᴀʀʏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴜsᴇᴅ ᴀs ғᴀʟʟʙᴀᴄᴋ
• ɪɴᴀᴄᴛɪᴠᴇ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ sᴋɪᴘᴘᴇᴅ ᴅᴜʀɪɴɢ ғɪʟᴇ ʀᴇᴛʀɪᴇᴠᴀʟ
• ʏᴏᴜ ᴄᴀɴ ʜᴀᴠᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs ғᴏʀ ʙᴇᴛᴛᴇʀ ʀᴇʟɪᴀʙɪʟɪᴛʏ"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ ᴛᴏ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ', 'back_to_db_management')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_callback_query(filters.regex("^back_to_db_management$"))
async def back_to_db_management(client, query):
    """Go back to main DB channels management"""
    if not query.from_user.id in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    
    # Use the refactored helper function
    msg, reply_markup = await _get_db_management_panel(client)
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#

@Client.on_message(filters.command(['adddb', 'add_db']) & filters.private)
async def quick_add_db(client: Client, message: Message):
    """Quick command to add a DB channel"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("""<blockquote>✦ ᴀᴅᴅ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ</blockquote>

›› **ᴜsᴀɢᴇ:** `/adddb <channel_id>`
›› **ᴇxᴀᴍᴘʟᴇ:** `/adddb -1001234567890`

**ɴᴏᴛᴇ:** ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ!""")
    
    try:
        channel_id = int(args[1])
    except ValueError:
        return await message.reply("**✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ! ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ.**")
    
    db_channels = getattr(client, 'db_channels', {})
    if str(channel_id) in db_channels:
        return await message.reply(f"**✗ ᴄʜᴀNNᴇʟ `{channel_id}` ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ ᴀs ᴀ ᴅʙ ᴄʜᴀɴɴᴇʟ!**")
    
    try:
        chat = await client.get_chat(channel_id)
        test_msg = await client.send_message(chat_id=channel_id, text=f"ᴛᴇsᴛɪɴɢ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴀᴄᴄᴇss... @{client.me.username}")
        await test_msg.delete()
        
        channel_data = {
            'name': chat.title,
            'is_primary': len(db_channels) == 0,  # First channel becomes primary
            'is_active': True,
            'added_by': message.from_user.id
        }
        
        await client.mongodb.add_db_channel(channel_id, channel_data)
        
        if not hasattr(client, 'db_channels'):
            client.db_channels = {}
        client.db_channels[str(channel_id)] = channel_data
        
        if channel_data['is_primary']:
            client.primary_db_channel = channel_id
            client.db = channel_id 
            await client.mongodb.set_primary_db_channel(channel_id)
        
        await message.reply(f"""**✓ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**

›› **ᴄʜᴀɴɴᴇʟ:** `{chat.title}`
›› **ɪᴅ:** `{channel_id}`
›› **sᴛᴀᴛᴜs:** {'ᴘʀɪᴍᴀʀʏ' if channel_data['is_primary'] else 'sᴇᴄᴏɴᴅᴀʀʏ'}

ᴜsᴇ `/db` ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀʟʟ ʏᴏᴜʀ ᴅʙ ᴄʜᴀɴɴᴇʟs.""")
    
    except (ChatAdminRequired, UsernameInvalid, PeerIdInvalid, Exception) as e:
        await message.reply(f"""**✗ ᴇʀʀᴏʀ ᴀᴄᴄᴇssɪɴɢ ᴄʜᴀɴɴᴇʟ!**

›› **ᴇʀʀᴏʀ:** `{str(e)}`

**ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ:**
• ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ
• ᴄʜᴀɴɴᴇʟ ɪᴅ ɪs ᴄᴏʀʀᴇᴄᴛ
• ᴄʜᴀɴɴᴇʟ ᴇxɪsᴛs""")

#===============================================================#

@Client.on_message(filters.command(['removedb', 'rm_db']) & filters.private)
async def quick_remove_db(client: Client, message: Message):
    """Quick command to remove a DB channel"""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    args = message.text.split()
    if len(args) < 2:
        db_channels = getattr(client, 'db_channels', {})
        if not db_channels:
            return await message.reply("**✗ ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴛᴏ ʀᴇᴍᴏᴠᴇ!**")
        
        msg = """<blockquote>✦ ʀᴇᴍᴏᴠᴇ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ</blockquote>

›› **ᴜsᴀɢᴇ:** `/removedb <channel_id>`

**ᴀᴠᴀɪʟᴀʙʟᴇ ᴄʜᴀɴɴᴇʟs:**
"""
        for channel_id_str, channel_data in db_channels.items():
            channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
            is_primary = " (ᴘʀɪᴍᴀʀʏ)" if channel_data.get('is_primary', False) else ""
            msg += f"• `{channel_name}` - `{channel_id_str}`{is_primary}\n"
        
        return await message.reply(msg)
    
    try:
        channel_id = int(args[1])
    except ValueError:
        return await message.reply("**✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ! ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ.**")
    
    db_channels = getattr(client, 'db_channels', {})
    
    if str(channel_id) not in db_channels:
        return await message.reply(f"**✗ ᴄʜᴀɴɴᴇʟ `{channel_id}` ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟs ʟɪsᴛ!**")
    
    if db_channels[str(channel_id)].get('is_primary', False) and len(db_channels) > 1:
        return await message.reply("**✗ ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴘʀɪᴍᴀʀʏ ᴄʜᴀɴɴᴇʟ!**\n\n__ᴘʟᴇᴀsᴇ sᴇᴛ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀɴɴᴇʟ ᴀs ᴘʀɪᴍᴀʀʏ ғɪʀsᴛ ᴜsɪɴɢ `/db`.__")
    
    # Remove from database and client
    channel_name = db_channels[str(channel_id)].get('name', 'ᴜɴᴋɴᴏᴡɴ')
    was_primary = db_channels[str(channel_id)].get('is_primary', False)
    
    await client.mongodb.remove_db_channel(channel_id)
    del client.db_channels[str(channel_id)]
    
    if was_primary and len(client.db_channels) == 0:
        client.primary_db_channel = None
        client.db = None
        await client.mongodb.set_primary_db_channel(None) 
    
    await message.reply(f"""**✓ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**

›› **ʀᴇᴍᴏᴠᴇᴅ:** `{channel_name}` (`{channel_id}`)

ᴜsᴇ `/db` ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʀᴇᴍᴀɪɴɪɴɢ ᴅʙ ᴄʜᴀɴɴᴇʟs.""")

#===============================================================#
# General Callbacks and Admin Commands
#==========================================================================#        

@Client.on_callback_query(filters.regex('^home$'))
async def home(client: Client, query: CallbackQuery):
    buttons = [[InlineKeyboardButton("Help", callback_data = "about"), InlineKeyboardButton("Close", callback_data = "close")]]
    if query.from_user.id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("⛩️ ꜱᴇᴛᴛɪɴɢꜱ ⛩️", callback_data="settings")])
    
    await query.message.edit_text(
        text=client.messages.get('START', 'No Start Message').format(
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
        # ❌ FIXED: Removed invalid 'message_effect_id' argument
    )
    return

#==========================================================================#        

@Client.on_callback_query(filters.regex('^about$'))
async def about(client: Client, query: CallbackQuery):
    buttons = [[InlineKeyboardButton("Back", callback_data = "home"), InlineKeyboardButton("Close", callback_data = "close")]]
    await query.message.edit_text(
        text=client.messages.get('ABOUT', 'No About Message').format(
            owner_id=client.owner,
            bot_username = client.me.username,
            first=query.from_user.first_name,
            last=query.from_user.last_name,
            username=None if not query.from_user.username else '@' + query.from_user.username,
            mention=query.from_user.mention,
            id=query.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
        # ❌ FIXED: Removed invalid 'message_effect_id' argument
    )
    return

#==========================================================================#        

@Client.on_callback_query(filters.regex('^close$'))
async def close(client: Client, query: CallbackQuery):
    try:
        await query.message.delete()
    except:
        pass
    try:
        # Also delete the command message that triggered the bot's reply
        await query.message.reply_to_message.delete()
    except:
        pass

#==========================================================================#        

@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.reply("Usage: /ban <user_id_1> <user_id_2> ...")
            
        user_ids_str = args[1]
        banned_count = 0
        admin_skipped_count = 0
        
        for user_id_str in user_ids_str.split():
            try:
                user_id = int(user_id_str)
            except ValueError:
                continue # Skip invalid numbers

            if user_id in client.admins or user_id == client.owner:
                admin_skipped_count += 1
                continue
                
            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, is_banned=True)
            else:
                await client.mongodb.ban_user(user_id)
            banned_count += 1
            
        reply_msg = f"__{banned_count} users have been banned!__"
        if admin_skipped_count > 0:
            reply_msg += f"\n__{admin_skipped_count} admins were skipped.__"
            
        return await message.reply(reply_msg)
        
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

#==========================================================================#        

@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
        
    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.reply("Usage: /unban <user_id_1> <user_id_2> ...")

        user_ids_str = args[1]
        unbanned_count = 0
        
        for user_id_str in user_ids_str.split():
            try:
                user_id = int(user_id_str)
            except ValueError:
                continue # Skip invalid numbers

            if not await client.mongodb.present_user(user_id):
                await client.mongodb.add_user(user_id, is_banned=False)
            else:
                await client.mongodb.unban_user(user_id)
            unbanned_count += 1
            
        return await message.reply(f"__{unbanned_count} users have been unbanned!__")
        
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

#==========================================================================#
