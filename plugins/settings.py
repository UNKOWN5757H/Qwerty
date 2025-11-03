import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UsernameInvalid, PeerIdInvalid
from config import OWNER_ID
import humanize

# A helper function to avoid duplicating the main settings text
async def _get_settings_msg_text(client):
    """Generates the text for the settings panel."""
    total_fsub = len(client.fsub_dict)
    request_enabled = sum(1 for data in client.fsub_dict.values() if data[2])
    timer_enabled = sum(1 for data in client.fsub_dict.values() if data[3] > 0)
    
    total_db_channels = len(getattr(client, 'db_channels', {}))
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    return f"""<blockquote>✦ sᴇᴛᴛɪɴɢs ᴏғ @{client.me.username}</blockquote>
›› **ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟs:** `{total_fsub}` (ʀᴇǫᴜᴇsᴛ: {request_enabled}, ᴛɪᴍᴇʀ: {timer_enabled})
›› **ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{total_db_channels}` (ᴘʀɪᴍᴀʀʏ: `{primary_db or 'None'}`)
›› **ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:** `{client.auto_del}`
›› **ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:** `{"✓ ᴛʀᴜᴇ" if client.protect else "✗ ꜰᴀʟsᴇ"}`
›› **ᴅɪsᴀʙʟᴇ ʙᴜᴛᴛᴏɴ:** `{"✓ ᴛʀᴜᴇ" if client.disable_btn else "✗ ꜰᴀʟsᴇ"}`
›› **ᴀᴅᴍɪɴs:** `{len(client.admins)}`
›› **sʜᴏʀᴛɴᴇʀ ᴜʀʟ:** `{getattr(client, 'short_url', 'ɴᴏᴛ sᴇᴛ')}`
›› **ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ:** `{getattr(client, 'tutorial_link', 'ɴᴏᴛ sᴇᴛ')}`
›› **sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('START', 'ᴇᴍᴘᴛʏ')}</pre>
›› **sᴛᴀʀᴛ ɪᴍᴀɢᴇ:** `{bool(client.messages.get('START_PHOTO', ''))}`
›› **ꜰᴏʀᴄᴇ sᴜʙ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('FSUB', 'ᴇᴍᴘᴛʏ')}</pre>
›› **ꜰᴏʀᴄᴇ sᴜʙ ɪᴍᴀɢᴇ:** `{bool(client.messages.get('FSUB_PHOTO', ''))}`
›› **ᴀʙᴏᴜᴛ ᴍᴇssᴀɢᴇ:**
<pre>{client.messages.get('ABOUT', 'ᴇᴍᴘᴛʏ')}</pre>
›› **ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ:**
<pre>{client.reply_text or 'None'}</pre>
"""

#===============================================================#

@Client.on_callback_query(filters.regex("^settings$"))
async def settings(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    msg = await _get_settings_msg_text(client)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟꜱ', 'fsub'), InlineKeyboardButton('ᴅʙ ᴄʜᴀɴɴᴇʟꜱ', 'db_channels')],
        [InlineKeyboardButton('ᴀᴅᴍɪɴꜱ', 'admins'), InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', 'auto_del')],
        [InlineKeyboardButton('ʜᴏᴍᴇ', 'home'), InlineKeyboardButton('›› ɴᴇxᴛ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^settings_page_2$"))
async def settings_page_2(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    msg = await _get_settings_msg_text(client)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ', 'protect'), InlineKeyboardButton('ᴘʜᴏᴛᴏs', 'photos')],
        [InlineKeyboardButton('ᴛᴇxᴛs', 'texts'), InlineKeyboardButton('sʜᴏʀᴛɴᴇʀ', 'shortner')],
        [InlineKeyboardButton('‹ ᴘʀᴇᴠ', 'settings'), InlineKeyboardButton('ʜᴏᴍᴇ', 'home')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    if client.fsub_dict:
        channel_list = []
        for channel_id, channel_data in client.fsub_dict.items():
            channel_name = channel_data[0] if channel_data and len(channel_data) > 0 else "Unknown"
            request_status = "✓ ʀᴇѦᴜᴇsᴛ" if channel_data[2] else "✗ ʀᴇѦᴜᴇsᴛ"
            timer_status = f"ᴛɪᴍᴇʀ: {channel_data[3]}ᴍ" if channel_data[3] > 0 else "ᴛɪᴍᴇʀ: ∞"
            channel_list.append(f"• `{channel_name}` (`{channel_id}`) - {request_status}, {timer_status}")
        
        channels_display = "\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    msg = f"""<blockquote>✦ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛᴛɪɴɢs</blockquote>
›› **ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:**
{channels_display}

__ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴀᴅᴅ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴀ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ ʙᴀsᴇᴅ ᴏɴ ʏᴏᴜʀ ɴᴇᴇᴅs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ', 'add_fsub'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ', 'rm_fsub')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^db_channels$"))
async def db_channels(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    db_channels = getattr(client, 'db_channels', {})
    if db_channels:
        channel_list = []
        for channel_id_str, channel_data in db_channels.items():
            channel_name = channel_data.get('name', 'Unknown')
            is_primary = "✓ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
            is_active = "✓ ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "✗ ɪɴᴀᴄᴛɪᴠᴇ"
            channel_list.append(f"• `{channel_name}` (`{channel_id_str}`)\n  {is_primary} | {is_active}")
        
        channels_display = "\n\n".join(channel_list)
    else:
        channels_display = "_ɴᴏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs ᴄᴏɴғɪɢᴜʀᴇᴅ_"
    
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    msg = f"""<blockquote>✦ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs sᴇᴛᴛɪɴɢs</blockquote>
›› **ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴍᴀʀʏ ᴅʙ:** `{primary_db or 'None'}`
›› **ᴛᴏᴛᴀʟ ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{len(db_channels)}`

**ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄʜᴀɴɴᴇʟs:**
{channels_display}

__ᴜsᴇ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('›› ᴀᴅᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'add_db_channel'), InlineKeyboardButton('›› ʀᴇᴍᴏᴠᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ', 'rm_db_channel')],
        [InlineKeyboardButton('›› sᴇᴛ ᴘʀɪᴍᴀʀʏ', 'set_primary_db'), InlineKeyboardButton('›› sᴛᴀᴛᴜs', 'toggle_db_status')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'settings')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^add_db_channel$"))
async def add_db_channel(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    msg = f"""<blockquote>✦ ᴀᴅᴅ ɴᴇᴡ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ</blockquote>
›› **ᴄᴜʀʀᴇɴᴛ ᴅʙ ᴄʜᴀɴɴᴇʟs:** `{len(getattr(client, 'db_channels', {}))}`

__sᴇɴᴅ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ɪᴅ (ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ ᴠᴀʟᴜᴇ) ᴏғ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__

**ᴇxᴀᴍᴘʟᴇ:** `-1001234567675`
**ɴᴏᴛᴇ:** ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ!"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.ask(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id_text = res.text.strip()
        
        if not channel_id_text.lstrip('-').isdigit():
            return await query.message.edit_text("**✗ ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ɪᴅ! ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴇɢᴀᴛɪᴠᴇ ɪɴᴛᴇɢᴇʀ.**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_id = int(channel_id_text)
        
        db_channels = getattr(client, 'db_channels', {})
        if str(channel_id) in db_channels:
            return await query.message.edit_text(f"**✗ ᴄʜᴀɴɴᴇʟ `{channel_id}` ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴅᴅᴇᴅ ᴀs ᴀ ᴅʙ ᴄʜᴀɴɴᴇʟ!**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))
        
        try:
            chat = await client.get_chat(channel_id)
            test_msg = await client.send_message(chat_id=channel_id, text=f"ᴛᴇsᴛɪɴɢ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴀᴄᴄᴇss... @{client.me.username}")
            await test_msg.delete()
            
            channel_data = {
                'name': chat.title,
                'is_primary': len(db_channels) == 0,  # First channel becomes primary
                'is_active': True,
                'added_by': query.from_user.id
            }
            
            await client.mongodb.add_db_channel(channel_id, channel_data)
            
            if not hasattr(client, 'db_channels'):
                client.db_channels = {}
            client.db_channels[str(channel_id)] = channel_data
            
            if channel_data['is_primary']:
                client.primary_db_channel = channel_id
                client.db = channel_id # Set legacy db var
                await client.mongodb.set_primary_db_channel(channel_id)
            
            await query.message.edit_text(f"""**✓ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**

›› **ᴄʜᴀɴɴᴇʟ:** `{chat.title}`
›› **ɪᴅ:** `{channel_id}`
›› **sᴛᴀᴛᴜs:** {'ᴘʀɪᴍᴀʀʏ' if channel_data['is_primary'] else 'sᴇᴄᴏɴᴅᴀʀʏ'}""", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))
        
        except (ChatAdminRequired, UsernameInvalid, PeerIdInvalid, Exception) as e:
            await query.message.edit_text(f"""**✗ ᴇʀʀᴏʀ ᴀᴄᴄᴇssɪɴɢ ᴄʜᴀɴɴᴇʟ!**

›› **ᴇʀʀᴏʀ:** `{str(e)}`

**ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ:**
• ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ
• ᴄʜᴀɴɴᴇʟ ɪᴅ ɪs ᴄᴏʀʀᴇᴄᴛ
• ᴄʜᴀɴɴᴇʟ ᴇxɪsᴛs""", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))
    
    except asyncio.TimeoutError:
        await query.message.edit_text("**✗ ᴛɪᴍᴇᴏᴜᴛ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'db_channels')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^rm_db_channel$"))
async def rm_db_channel(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    db_channels = getattr(client, 'db_channels', {})
    
    if not db_channels:
        return await query.message.edit_text("**❌ No database channels to remove!**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    msg = "<blockquote>**Remove Database Channel:**</blockquote>\n**Available Channels:**\n"
    
    for channel_id_str, channel_data in db_channels.items():
        channel_name = channel_data.get('name', 'Unknown')
        is_primary = " (Primary)" if channel_data.get('is_primary', False) else ""
        msg += f"• `{channel_name}` - `{channel_id_str}`{is_primary}\n"
    
    msg += "\n__Send the channel ID you want to remove in the next 60 seconds!__"
    
    await query.message.edit_text(msg)
    try:
        res = await client.ask(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id_text = res.text.strip()
        
        if not channel_id_text.lstrip('-').isdigit():
            return await query.message.edit_text("**❌ Invalid channel ID!**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_id = int(channel_id_text)
        
        if str(channel_id) not in db_channels:
            return await query.message.edit_text(f"**❌ Channel `{channel_id}` is not in the DB channels list!**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        if db_channels[str(channel_id)].get('is_primary', False) and len(db_channels) > 1:
            return await query.message.edit_text("**❌ Cannot remove primary channel!**\n\n__Please set another channel as primary first.__", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_name = db_channels[str(channel_id)].get('name', 'Unknown')
        await client.mongodb.remove_db_channel(channel_id)
        del client.db_channels[str(channel_id)]
        
        # If the last channel was removed, clear primary/db vars
        if len(client.db_channels) == 0:
            client.primary_db_channel = None
            client.db = None
        
        await query.message.edit_text(f"**✅ Database channel removed successfully!**\n\n**Removed:** `{channel_name}` (`{channel_id}`)", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    except asyncio.TimeoutError:
        await query.message.edit_text("**❌ Timeout! Please try again.**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^set_primary_db$"))
async def set_primary_db(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    db_channels = getattr(client, 'db_channels', {})
    
    if not db_channels:
        return await query.message.edit_text("**❌ No database channels available!**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    msg = "<blockquote>**Set Primary Database Channel:**</blockquote>\n**Available Channels:**\n"
    
    for channel_id_str, channel_data in db_channels.items():
        channel_name = channel_data.get('name', 'Unknown')
        is_primary = " (Current Primary)" if channel_data.get('is_primary', False) else ""
        msg += f"• `{channel_name}` - `{channel_id_str}`{is_primary}\n"
    
    msg += "\n__Send the channel ID you want to set as primary in the next 60 seconds!__"
    
    await query.message.edit_text(msg)
    try:
        res = await client.ask(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id_text = res.text.strip()
        
        if not channel_id_text.lstrip('-').isdigit():
            return await query.message.edit_text("**❌ Invalid channel ID!**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_id = int(channel_id_text)
        
        if str(channel_id) not in db_channels:
            return await query.message.edit_text(f"**❌ Channel `{channel_id}` is not in the DB channels list!**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        await client.mongodb.set_primary_db_channel(channel_id)
        
        for ch_id, ch_data in client.db_channels.items():
            ch_data['is_primary'] = (int(ch_id) == channel_id)
        
        client.primary_db_channel = channel_id
        client.db = channel_id
        
        channel_name = db_channels[str(channel_id)].get('name', 'Unknown')
        await query.message.edit_text(f"**✅ Primary database channel updated!**\n\n**New Primary:** `{channel_name}` (`{channel_id}`)", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    except asyncio.TimeoutError:
        await query.message.edit_text("**❌ Timeout! Please try again.**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^toggle_db_status$"))
async def toggle_db_status(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
    
    await query.answer()
    db_channels = getattr(client, 'db_channels', {})
    
    if not db_channels:
        return await query.message.edit_text("**❌ No database channels available!**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    
    msg = "<blockquote>**Toggle Channel Status:**</blockquote>\n**Available Channels:**\n"
    
    for channel_id_str, channel_data in db_channels.items():
        channel_name = channel_data.get('name', 'Unknown')
        status = "🟢 ᴀᴄᴛɪᴠᴇ" if channel_data.get('is_active', True) else "🔴 ɪɴᴀᴄᴛɪᴠᴇ"
        msg += f"• `{channel_name}` - `{channel_id_str}` ({status})\n"
    
    msg += "\n__Send the channel ID you want to ᴀᴄᴛɪᴠᴇ/ɪɴᴀᴄᴛɪᴠᴇ status for in the next 60 seconds!__"
    
    await query.message.edit_text(msg)
    try:
        res = await client.ask(user_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id_text = res.text.strip()
        
        if not channel_id_text.lstrip('-').isdigit():
            return await query.message.edit_text("**❌ Invalid channel ID!**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        channel_id = int(channel_id_text)
        
        if str(channel_id) not in db_channels:
            return await query.message.edit_text(f"**❌ Channel `{channel_id}` is not in the DB channels list!**", 
                                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        
        new_status = await client.mongodb.toggle_db_channel_status(channel_id)
        
        if new_status is not None:
            client.db_channels[str(channel_id)]['is_active'] = new_status
            
            channel_name = db_channels[str(channel_id)].get('name', 'Unknown')
            status_text = "🟢 Active" if new_status else "🔴 Inactive"
            await query.message.edit_text(f"**✅ Channel status updated!**\n\n**Channel:** `{channel_name}` (`{channel_id}`)\n**New Status:** {status_text}", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
        else:
            await query.message.edit_text("**❌ Failed to toggle channel status!**", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))
    except asyncio.TimeoutError:
        await query.message.edit_text("**❌ Timeout! Please try again.**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'db_channels')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^admins$"))
async def admins(client, query):
    if not (query.from_user.id == OWNER_ID):
        return await query.answer('✗ ᴛʜɪs ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ.', show_alert=True)
        
    msg = f"""<blockquote>**Admin Settings:**</blockquote>
**Admin User IDs:** {", ".join(f"`{a}`" for a in client.admins)}

__Use the appropriate button below to add or remove an admin based on your needs!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('ᴀᴅᴅ ᴀᴅᴍɪɴ', 'add_admin'), InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ', 'rm_admin')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]
    )
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^photos$"))
async def photos(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    msg = f"""<blockquote>**Photo Settings:**</blockquote>
**Start Photo:** `{client.messages.get("START_PHOTO", "None")}`
**Force Sub Photo:** `{client.messages.get('FSUB_PHOTO', 'None')}`

__Use the appropriate button below to set or remove images.__
"""
    reply_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            ('ꜱᴇᴛ' if not client.messages.get("START_PHOTO") else 'ᴄʜᴀɴɢᴇ') + '\nꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ', 
            callback_data='add_start_photo'
        ),
        InlineKeyboardButton(
            ('ꜱᴇᴛ' if not client.messages.get("FSUB_PHOTO") else 'ᴄʜᴀɴɢᴇ') + '\nꜰꜱᴜʙ ᴘʜᴏᴛᴏ', 
            callback_data='add_fsub_photo'
        )
    ],
    [
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ\nꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ', callback_data='rm_start_photo'),
        InlineKeyboardButton('ʀᴇᴍᴏᴠᴇ\nꜰꜱᴜʙ ᴘʜᴏᴛᴏ', callback_data='rm_fsub_photo')
    ],
    [InlineKeyboardButton('◂ ʙᴀᴄᴋ', callback_data='settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex("^protect$"))
async def protect(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    client.protect = not client.protect # Cleaner toggle
    await query.answer(f"Protect Content set to {client.protect}")
    await settings_page_2(client, query) # Refresh page 2

#===============================================================#

@Client.on_callback_query(filters.regex("^auto_del$"))
async def auto_del(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)

    msg = f"""<blockquote>**Change Auto Delete Time:**</blockquote>
**Current Timer:** `{client.auto_del}`

__Enter new integer value of auto delete timer (in seconds).
Keep 0 to disable auto delete.
Wait for 60 seconds or send -1 to cancel.__
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.ask(user_id=query.from_user.id, filters=filters.text, timeout=60)
        timer_text = res.text.strip()
        
        try:
            timer = int(timer_text) # Handles '+', '-', and numbers
            if timer >= 0:
                client.auto_del = timer
                await client.mongodb.update_config('AUTO_DEL', timer) # Persist setting
                return await query.message.edit_text(f'**✅ Auto Delete timer value changed to {timer} seconds!**', 
                                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
            else:
                # User sent -1 or other negative number
                return await query.message.edit_text("**✗ No change done in auto delete timer!**", 
                                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
        except ValueError:
            return await query.message.edit_text("**✗ This is not an integer value!**", 
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))
            
    except asyncio.TimeoutError:
        return await query.message.edit_text("**✗ Timeout, try again!**", 
                                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^texts$"))
async def texts(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    msg = f"""<blockquote>**Text Configuration:**</blockquote>
**Start Message:**
<pre>{client.messages.get('START', 'Empty')}</pre>
**Force Sub Message:**
<pre>{client.messages.get('FSUB', 'Empty')}</pre>
**About Message:**
<pre>{client.messages.get('ABOUT', 'Empty')}</pre>
**Reply Message:**
<pre>{client.reply_text or 'None'}</pre>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'ꜱᴛᴀʀᴛ ᴛᴇxᴛ', 'start_txt'), InlineKeyboardButton(f'ꜰꜱᴜʙ ᴛᴇxᴛ', 'fsub_txt')],
        [InlineKeyboardButton('ʀᴇᴘʟʏ ᴛᴇxᴛ', 'reply_txt'), InlineKeyboardButton('ᴀʙᴏᴜᴛ ᴛᴇxᴛ', 'about_txt')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'settings_page_2')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

#===============================================================#

@Client.on_callback_query(filters.regex('^rm_start_photo$'))
async def rm_start_photo(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    client.messages['START_PHOTO'] = ''
    await client.mongodb.update_message('START_PHOTO', '') # Persist
    await query.answer("Start Photo Removed!", show_alert=True)
    await photos(client, query)

#===============================================================#

@Client.on_callback_query(filters.regex('^rm_fsub_photo$'))
async def rm_fsub_photo(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    client.messages['FSUB_PHOTO'] = ''
    await client.mongodb.update_message('FSUB_PHOTO', '') # Persist
    await query.answer("FSUB Photo Removed!", show_alert=True)
    await photos(client, query)

#===============================================================#

@Client.on_callback_query(filters.regex("^add_start_photo$"))
async def add_start_photo(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    msg = f"""<blockquote>**Change Start Image:**</blockquote>
**Current Start Image:** `{client.messages.get('START_PHOTO', '')}`

__Send a new photo or a public image link.
Wait for 60 seconds to cancel.__
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.ask(user_id=query.from_user.id, filters=(filters.text | filters.photo), timeout=60)
        
        new_photo_val = ""
        reply_msg = ""

        if res.text and (res.text.startswith('https://') or res.text.startswith('http://')):
            new_photo_val = res.text
            reply_msg = "**✅ This link has been set as the start photo!**"
        elif res.photo:
            # You can't save a downloaded file path permanently,
            # as it will be lost on restart.
            # You must use the photo's file_id.
            new_photo_val = res.photo.file_id
            reply_msg = "**✅ This image has been set as the starting image!**"
        else:
            return await query.message.edit_text("**✗ Invalid Photo or Link format!**\n__Link must start with 'http://' or 'https://'.__", 
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
        
        client.messages['START_PHOTO'] = new_photo_val
        await client.mongodb.update_message('START_PHOTO', new_photo_val) # Persist
        return await query.message.edit_text(reply_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))

    except asyncio.TimeoutError:
        return await query.message.edit_text("**✗ Timeout, try again!**", 
                                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))

#===============================================================#

@Client.on_callback_query(filters.regex("^add_fsub_photo$"))
async def add_fsub_photo(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer('✗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!', show_alert=True)
        
    msg = f"""<blockquote>**Change Force Sub Image:**</blockquote>
**Current Force Sub Image:** `{client.messages.get('FSUB_PHOTO', '')}`

__Send a new photo or a public image link.
Wait for 60 seconds to cancel.__
"""
    await query.answer()
    await query.message.edit_text(msg)
    try:
        res = await client.ask(user_id=query.from_user.id, filters=(filters.text | filters.photo), timeout=60)
        
        new_photo_val = ""
        reply_msg = ""

        if res.text and (res.text.startswith('https://') or res.text.startswith('http://')):
            new_photo_val = res.text
            reply_msg = "**✅ This link has been set as the FSUB photo!**"
        elif res.photo:
            new_photo_val = res.photo.file_id
            reply_msg = "**✅ This image has been set as the FSUB image!**"
        else:
            return await query.message.edit_text("**✗ Invalid Photo or Link format!**\n__Link must start with 'http://' or 'https://'.__", 
                                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))

        client.messages['FSUB_PHOTO'] = new_photo_val
        await client.mongodb.update_message('FSUB_PHOTO', new_photo_val) # Persist
        return await query.message.edit_text(reply_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))

    except asyncio.TimeoutError:
        return await query.message.edit_text("**✗ Timeout, try again!**", 
                                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'photos')]]))
