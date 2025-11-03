
from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
from helper.helper_func import check_subscription, is_user_subscribed
from plugins.processing import process_start_payload # Import our new function

@Client.on_chat_member_updated()
async def auto_fsub_handler(client: Client, update: ChatMemberUpdated):
    # Check if this is a user joining a channel
    if (
        update.new_chat_member
        and update.new_chat_member.status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR}
        and update.old_chat_member
        and update.old_chat_member.status not in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR}
    ):
        user_id = update.new_chat_member.user.id
        
        # Check if the channel is one of our fsub channels
        if str(update.chat.id) not in client.fsub_dict:
            return # Not an fsub channel

        client.LOGGER(__name__, client.name).info(f"User {user_id} just joined FSUB channel {update.chat.id}")

        # Check if the user is now subscribed to ALL required channels
        statuses = await check_subscription(client, user_id)
        if is_user_subscribed(statuses):
            client.LOGGER(__name__, client.name).info(f"User {user_id} is now fully subscribed.")
            
            # Check if they have a pending payload
            payload = await client.mongodb.get_pending_payload(user_id)
            
            if payload:
                client.LOGGER(__name__, client.name).info(f"Found pending payload for {user_id}. Processing...")
                
                # Clear the payload from DB
                await client.mongodb.clear_pending_payload(user_id)
                
                # Send a confirmation and start processing
                await client.send_message(user_id, "✅ Thank you for joining! Processing your request...")
                
                # Get the user object
                user = update.new_chat_member.user
                
                # Call the file processing function
                await process_start_payload(client, user, payload)
