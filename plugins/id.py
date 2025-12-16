from pyrogram import Client, filters, enums
import logging

import os
import datetime
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    ChatWriteForbidden,
    PeerIdInvalid,
    UserDeactivated
)




logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.command('id'))
async def show_id(client, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(f"<b>» ᴜꜱᴇʀ ɪᴅ - <code>{message.from_user.id}</code></b>")

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(f"<b>» ɢʀᴏᴜᴘ ɪᴅ - <code>{message.chat.id}</code></b>")

    elif chat_type == enums.ChatType.CHANNEL:
        await message.reply_text(f"<b>» ᴄʜᴀɴɴᴇʟ ɪᴅ - <code>{message.chat.id}</code></b>")




###-----_--------_----------_------###

@Client.on_callback_query(filters.regex("^mkick_"))
async def mkick_callback(client, query):
    data = query.data

    if data == "mkick_no":
        return await query.message.edit_text("<b>Operation cancelled.</b>")

    _, channel_id = data.split("|")
    channel_id = int(channel_id)

    start_time = datetime.datetime.now()
    log_file = f"mkick_log_{channel_id}_{start_time.strftime('%Y%m%d_%H%M%S')}.txt"

    def write_log(text):
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    await query.message.edit_text("<b>⏳ Processing started…</b>")
    write_log(f"Process started at {start_time}")
    write_log(f"Channel ID: {channel_id}")
    write_log("-" * 50)

    # Fetch channel info
    chat = await client.get_chat(channel_id)
    write_log(f"Channel Name: {chat.title}")

    # Fetch admins
    admin_ids = []
    async for admin in client.get_chat_members(
        channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        admin_ids.append(admin.user.id)

    write_log(f"Total Admins: {len(admin_ids)}")
    write_log("-" * 50)

    kicked = 0
    skipped = 0

    async for member in client.get_chat_members(channel_id):
        user = member.user
        if not user or user.id in admin_ids:
            continue

        write_log(f"Processing User ID: {user.id}")

        try:
            await client.send_message(
                user.id,
                f"आपको वैधता पूरी होने के कारण <b>{chat.title}</b> से हटाया जा रहा है,\n\n"
                "अगर आपको लगता है हमसे कोई गड़बड़ हुई है या आप पुनः चैनल में जुड़ना चाहते है "
                "तो इसी bot पर मैसेज कर सकते है।"
            )

            await asyncio.sleep(1)

            await client.ban_chat_member(channel_id, user.id)
            kicked += 1
            write_log("✔ Message sent & user kicked successfully")

        except UserIsBlocked:
            skipped += 1
            write_log("✖ FAILED: User has blocked the bot")

        except ChatWriteForbidden:
            skipped += 1
            write_log("✖ FAILED: Cannot send message (privacy restriction)")

        except UserDeactivated:
            skipped += 1
            write_log("✖ FAILED: User account deactivated")

        except PeerIdInvalid:
            skipped += 1
            write_log("✖ FAILED: Invalid peer ID")

        except FloodWait as e:
            write_log(f"⚠ FloodWait: Sleeping {e.value} seconds")
            await asyncio.sleep(e.value)

        except Exception as e:
            skipped += 1
            write_log(f"✖ FAILED: Unknown error → {str(e)}")

        write_log("-" * 30)
        await asyncio.sleep(1)

    end_time = datetime.datetime.now()
    write_log(f"Process completed at {end_time}")
    write_log(f"Total Kicked: {kicked}")
    write_log(f"Total Skipped: {skipped}")

    await query.message.edit_text(
        f"<b>✅ Process Completed</b>\n\n"
        f"Kicked: <code>{kicked}</code>\n"
        f"Skipped: <code>{skipped}</code>"
    )

    await client.send_document(
        chat_id=query.from_user.id,
        document=log_file,
        caption="<b>📄 MKICK Logs</b>"
    )

    os.remove(log_file)
    
