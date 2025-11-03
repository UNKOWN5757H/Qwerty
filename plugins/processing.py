# Save this as /app/plugins/processing.py
import asyncio
from pyrogram import Client
from pyrogram.types import User, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from config import OWNER_ID
from plugins.shortner import get_short
from helper.helper_func import (
    get_messages, 
    decode, 
    batch_auto_del_notification
)

async def process_start_payload(client: Client, user: User, original_payload: str):
    """
    This function contains the core logic for decoding a payload
    and sending the corresponding files to the user.
    """
    user_id = user.id
    base64_string = original_payload
    is_short_link = False

    if base64_string.startswith("yu3elk"):
        base64_string = base64_string[6:-1]
        is_short_link = True

    # 1. Check premium status
    is_user_pro = await client.mongodb.is_pro(user_id)
    
    # 2. Check if shortner is enabled
    shortner_enabled = getattr(client, 'shortner_enabled', True)

    # 3. If user is not premium AND shortner is enabled, send short URL and return
    if not is_user_pro and user_id != OWNER_ID and not is_short_link and shortner_enabled:
        try:
            short_link = get_short(f"https://krpicture1.blogspot.com?start=yu3elk{base64_string}7", client)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Shortener failed: {e}")
            return await client.send_message(user_id, "Couldn't generate short link.")

        short_photo = client.messages.get("SHORT_PIC", "")
        short_caption = client.messages.get("SHORT_MSG", "")
        tutorial_link = getattr(client, 'tutorial_link', "https://t.me/how_to_opan_linkz/6")

        await client.send_photo(
            chat_id=user_id,
            photo=short_photo,
            caption=short_caption,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• ᴏᴘᴇɴ ʟɪɴᴋ", url=short_link),
                    InlineKeyboardButton("ᴛᴜᴛᴏʀɪᴀʟ •", url=tutorial_link)
                ],
                [
                    InlineKeyboardButton(" • ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ •", url="https://t.me/how_to_opan_linkz/6")
                ]
            ])
        )
        return  # prevent sending actual files

    # 4. Decode and prepare file IDs
    try:
        string = await decode(base64_string)
        argument = string.split("-")
        ids = []
        source_channel_id = None

        if len(argument) == 3:
            encoded_start = int(argument[1])
            encoded_end = int(argument[2])
            primary_multiplier = abs(int(client.db))
            start_primary = int(encoded_start / primary_multiplier)
            end_primary = int(encoded_end / primary_multiplier)
            
            if encoded_start % primary_multiplier == 0 and encoded_end % primary_multiplier == 0:
                source_channel_id = client.db
                start = start_primary
                end = end_primary
                client.LOGGER(__name__, client.name).info(f"Decoded batch from primary channel {source_channel_id}: {start}-{end}")
            else:
                db_channels = getattr(client, 'db_channels', {})
                for channel_id_str in db_channels.keys():
                    channel_id = int(channel_id_str)
                    channel_multiplier = abs(channel_id)
                    start_test = int(encoded_start / channel_multiplier)
                    end_test = int(encoded_end / channel_multiplier)
                    
                    if encoded_start % channel_multiplier == 0 and encoded_end % channel_multiplier == 0:
                        source_channel_id = channel_id
                        start = start_test
                        end = end_test
                        client.LOGGER(__name__, client.name).info(f"Decoded batch from secondary channel {source_channel_id}: {start}-{end}")
                        break
                
                if source_channel_id is None:
                    source_channel_id = client.db
                    start = start_primary
                    end = end_primary
            
            ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))

        elif len(argument) == 2:
            encoded_msg = int(argument[1])
            
            if hasattr(client, 'db_channel') and client.db_channel:
                primary_multiplier = abs(int(client.db_channel.id))
                msg_id_primary = int(encoded_msg / primary_multiplier)
                
                if encoded_msg % primary_multiplier == 0:
                    source_channel_id = client.db_channel.id
                    ids = [msg_id_primary]
                else:
                    db_channels = getattr(client, 'db_channels', {})
                    for channel_id_str in db_channels.keys():
                        channel_id = int(channel_id_str)
                        channel_multiplier = abs(channel_id)
                        msg_id_test = int(encoded_msg / channel_multiplier)
                        
                        if encoded_msg % channel_multiplier == 0:
                            source_channel_id = channel_id
                            ids = [msg_id_test]
                            break
                    
                    if source_channel_id is None:
                        source_channel_id = client.db_channel.id if hasattr(client, 'db_channel') else int(client.db)
                        ids = [msg_id_primary]
            else:
                source_channel_id = client.db
                ids = [int(encoded_msg / abs(int(client.db)))]

    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Error decoding base64: {e}")
        return await client.send_message(user_id, "⚠️ Invalid or expired link.")

    # 5. Get messages
    temp_msg = await client.send_message(user_id, "Wait A Sec..")
    messages_raw = [] 

    try:
        if source_channel_id:
            client.LOGGER(__name__, client.name).info(f"Trying to get messages from source channel: {source_channel_id}")
            try:
                msgs = await client.get_messages(
                    chat_id=int(source_channel_id),
                    message_ids=list(ids)
                )
                valid_msgs = [msg for msg in msgs if msg is not None]
                messages_raw.extend(valid_msgs)
                client.LOGGER(__name__, client.name).info(f"Found {len(valid_msgs)} messages from source channel {source_channel_id}")
                
                if len(valid_msgs) < len(list(ids)):
                    missing_ids = [mid for mid in ids if mid not in {msg.id for msg in valid_msgs}]
                    if missing_ids:
                        client.LOGGER(__name__, client.name).info(f"Missing {len(missing_ids)} messages, trying fallback system")
                        additional_messages = await get_messages(client, missing_ids)
                        messages_raw.extend(additional_messages)
                        client.LOGGER(__name__, client.name).info(f"Found {len(additional_messages)} additional messages from fallback")
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Error getting messages from source channel {source_channel_id}: {e}")
                messages_raw = await get_messages(client, ids)
        else:
            client.LOGGER(__name__, client.name).info("No specific source channel identified, using multi-channel fallback")
            messages_raw = await get_messages(client, ids)
    except Exception as e:
        await temp_msg.edit_text("Something went wrong!")
        client.LOGGER(__name__, client.name).warning(f"Error getting messages: {e}")
        return

    # 6. Filter and send messages
    messages = [
        msg for msg in messages_raw 
        if msg.media or msg.text  # Only keep messages with actual content
    ]
    
    if not messages_raw:
        return await temp_msg.edit("Couldn't find the files in the database. (Messages may be deleted).")
    
    if not messages:
        client.LOGGER(__name__, client.name).warning(f"Found {len(messages_raw)} messages, but all were non-copyable service messages.")
        return await temp_msg.edit("Couldn't find any files to send. (Messages might be service messages).")
    
    await temp_msg.delete()

    yugen_msgs = []
    for msg in messages:
        caption = (
            client.messages.get('CAPTION', '').format(
                previouscaption=msg.caption.html if msg.caption else (msg.document.file_name if msg.document else "")
            ) if bool(client.messages.get('CAPTION', ''))
            else ("" if not msg.caption else msg.caption.html)
        )
        reply_markup = msg.reply_markup if not client.disable_btn else None

        try:
            copied_msg = await msg.copy(
                chat_id=user_id,
                caption=caption,
                reply_markup=reply_markup,
                protect_content=client.protect
            )
            yugen_msgs.append(copied_msg)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            copied_msg = await msg.copy(
                chat_id=user_id,
                caption=caption,
                reply_markup=reply_markup,
                protect_content=client.protect
            )
            yugen_msgs.append(copied_msg)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Failed to send message: {e}")
            pass

    # 7. Auto delete timer
    if yugen_msgs and client.auto_del > 0:
        transfer_link = original_payload
        
        asyncio.create_task(batch_auto_del_notification(
            bot_username = client.me.username,
            messages=yugen_msgs,
            delay_time=client.auto_del,
            transfer_link=transfer_link,
            chat_id=user_id,
            client=client
        ))
    return
