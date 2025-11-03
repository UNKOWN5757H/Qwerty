# (©) Codeflix_Bots

import sys
import asyncio
from datetime import datetime
from aiohttp import web
from pyrogram import Client, errors
from pyrogram.enums import ParseMode, ChatMemberStatus
from config import LOGGER, PORT, OWNER_ID, SHORT_URL, SHORT_API, SHORT_TUT
from helper import MongoDB
from plugins import web_server

version = "v1.1.0"


class Bot(Client):
    def __init__(
        self,
        session,
        workers,
        db,
        fsub,
        token,
        admins,
        messages,
        auto_del,
        db_uri,
        db_name,
        api_id,
        api_hash,
        protect,
        disable_btn,
    ):
        super().__init__(
            name=session,
            api_id=api_id,
            api_hash=api_hash,
            bot_token=token,
            workers=workers,
            plugins={"root": "plugins"},
            parse_mode=ParseMode.HTML,
        )
        self.LOGGER = LOGGER
        self.name = session
        self.db = db
        self.fsub = fsub
        self.owner = OWNER_ID
        self.fsub_dict = {}
        self.admins = admins + [OWNER_ID] if OWNER_ID not in admins else admins
        self.messages = messages
        self.auto_del = auto_del
        self.protect = protect
        self.req_fsub = {}
        self.disable_btn = disable_btn
        self.reply_text = messages.get("REPLY", "Do not send any useless message in the bot.")
        self.mongodb = MongoDB(db_uri, db_name)
        self.req_channels = []
        self.db_channels = {}
        self.primary_db_channel = db
        self.short_url = SHORT_URL
        self.short_api = SHORT_API
        self.tutorial_link = SHORT_TUT
        self.shortner_enabled = True

    # ================================================================
    #  Safe get_chat() wrapper
    # ================================================================
    async def safe_get_chat(self, chat_id, retries=3):
        for attempt in range(retries):
            try:
                return await self.get_chat(int(chat_id))
            except errors.FloodWait as e:
                self.LOGGER(__name__, self.name).warning(f"FloodWait {e.value}s while fetching {chat_id}. Retrying...")
                await asyncio.sleep(e.value)
            except errors.PeerIdInvalid:
                self.LOGGER(__name__, self.name).warning(f"PeerIdInvalid for {chat_id}. Retrying after short delay...")
                await asyncio.sleep(2)
            except errors.Forbidden:
                self.LOGGER(__name__, self.name).warning(f"Access denied for {chat_id}. Skipping...")
                return None
            except Exception as e:
                self.LOGGER(__name__, self.name).warning(f"Error fetching {chat_id}: {e}")
                await asyncio.sleep(1)
        return None

    # ================================================================
    #  Bot Start Logic
    # ================================================================
    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        log = self.LOGGER(__name__, self.name)
        log.info(f"Starting bot as @{usr_bot_me.username}")

        # --- Load Force Sub Channels ---
        if self.fsub:
            for channel in self.fsub:
                cid = channel[0]
                try:
                    chat = await self.safe_get_chat(cid)
                    if not chat:
                        continue
                    name = chat.title
                    invite_link = None

                    try:
                        invite_link = chat.invite_link or (await self.create_chat_invite_link(cid)).invite_link
                    except errors.ChatAdminRequired:
                        log.warning(f"⚠️ Bot lacks permission to create invite link in {name}")

                    self.fsub_dict[cid] = [name, invite_link, channel[1], channel[2]]
                    if channel[1]:
                        self.req_channels.append(cid)

                except Exception as e:
                    log.warning(f"Could not load ForceSub channel {cid}: {e}")

        # --- Load DB Channels ---
        try:
            db_channels_data = await self.mongodb.get_db_channels()
            self.db_channels = {}
            self.primary_db_channel = self.db

            for cid_str, channel_data in db_channels_data.items():
                cid = int(cid_str)
                chat = await self.safe_get_chat(cid)
                if not chat:
                    log.warning(f"Skipping invalid DB channel {cid}")
                    await self.mongodb.remove_db_channel(cid)
                    continue

                channel_data["name"] = chat.title
                self.db_channels[cid_str] = channel_data
                if channel_data.get("is_primary", False):
                    self.primary_db_channel = cid
                    self.db = cid

        except Exception as e:
            log.warning(f"Error loading DB channels: {e}")

        # --- Verify Primary DB Channel ---
        try:
            db_chat = await self.safe_get_chat(self.db)
            if not db_chat:
                raise Exception("DB channel not accessible")

            self.db_channel = db_chat
            msg = await self.send_message(self.db_channel.id, "🧩 DB Channel Verified!")
            await msg.delete()
            log.info(f"✅ Primary DB Channel: {self.primary_db_channel}")

        except Exception as e:
            log.warning(f"❌ Could not verify DB Channel ({self.db}): {e}")
            log.warning("Make sure the bot is admin and DB_CHANNEL ID is correct.")
            log.warning("Bot continuing in degraded mode (no DB channel).")
            self.db_channel = None  # Safe fallback (won't crash)

        # --- Load Shortener Settings ---
        try:
            short_settings = await self.mongodb.get_shortner_settings()
            self.short_url = short_settings.get("short_url", SHORT_URL)
            self.short_api = short_settings.get("short_api", SHORT_API)
            self.tutorial_link = short_settings.get("tutorial_link", SHORT_TUT)
            self.shortner_enabled = short_settings.get("enabled", True)
        except Exception as e:
            log.warning(f"Error loading shortener settings: {e}")

        # --- Notify Owner ---
        try:
            await self.send_message(self.owner, "<b>✅ Bot Restarted Successfully!</b>")
            log.info(f"Restart notification sent to owner: {self.owner}")
        except Exception as e:
            log.warning(f"Could not send restart message: {e}")

        log.info("🤖 Bot Started Successfully!")

    # ================================================================
    #  Bot Stop Logic
    # ================================================================
    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__, self.name).info("Bot stopped gracefully.")


# ================================================================
#  Web Server Setup
# ================================================================
async def web_app():
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
