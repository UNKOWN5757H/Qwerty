import asyncio
from bot import Bot, web_app
from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus
from pyrogram import compose
from config import *


async def verify_channels(bot: Client):
    """
    Ensure the bot can access and is admin in DB_CHANNEL and FSUB channels.
    Prevents PEER_ID_INVALID and permission issues.
    """
    print("\n🔍 Verifying bot channel access...")

    # --- Verify Database Channel ---
    try:
        chat = await bot.get_chat(int(DB_CHANNEL))
        print(f"✅ Bot found DB Channel: {chat.title} ({DB_CHANNEL})")

        member = await bot.get_chat_member(int(DB_CHANNEL), "me")
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            print(f"⚠️ Bot is NOT admin in DB Channel {DB_CHANNEL}. Please promote it.")
        else:
            print("✅ Bot is admin in DB Channel.")

    except errors.PeerIdInvalid:
        print(f"❌ Invalid DB_CHANNEL ID: {DB_CHANNEL}")
    except errors.ChatAdminRequired:
        print(f"⚠️ Bot lacks admin rights in DB Channel {DB_CHANNEL}.")
    except Exception as e:
        print(f"⚠️ DB Channel check failed: {e}")

    # --- Verify Force Subscription Channels ---
    for cid, enabled, _ in FSUBS:
        if not enabled:
            continue
        try:
            chat = await bot.get_chat(int(cid))
            print(f"✅ Bot found ForceSub Channel: {chat.title} ({cid})")

            member = await bot.get_chat_member(int(cid), "me")
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                print(f"⚠️ Bot is NOT admin in ForceSub Channel {cid}. Please promote it.")
            else:
                print("✅ Bot is admin in ForceSub Channel.")

        except errors.PeerIdInvalid:
            print(f"❌ Invalid ForceSub Channel ID: {cid}")
        except Exception as e:
            print(f"⚠️ ForceSub check failed for {cid}: {e}")

    print("✅ Channel verification complete.\n")


async def main():
    app = []

    # Create bot instance using config.py values
    bot = Bot(
        SESSION,
        WORKERS,
        DB_CHANNEL,
        FSUBS,
        BOT_TOKEN,
        ADMINS,
        MESSAGES,
        AUTO_DEL,
        DB_URI,
        DB_NAME,
        API_ID,
        API_HASH,
        PROTECT,
        DISABLE_BTN,
    )

    # Start bot briefly to verify channels
    await bot.start()
    await verify_channels(bot)
    await bot.stop()

    app.append(bot)
    await compose(app)


async def runner():
    await asyncio.gather(main(), web_app())


if __name__ == "__main__":
    try:
        asyncio.run(runner())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Bot stopped manually.")
