import logging
import asyncio
import os

from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.errors.exceptions.bad_request_400 import MessageIdInvalid

from exp_userbot.core.expub_database.expub_db_conf import get_log_channel
from exp_userbot.core.expub_database.expub_db_sudos import get_sudos
from exp_userbot import EXPUB
from config import Config


# ================= MAIN ================= #
# Log channel id
log_cid_loop = asyncio.get_event_loop()
LOG_CHANNEL_ID = log_cid_loop.run_until_complete(get_log_channel())

# Sudo users
sudos = log_cid_loop.run_until_complete(get_sudos())
sudos.append("me")
SUDO_IDS = sudos

def add_handler(x_wrapper, expub_filter):
    EXPUB.add_handler(MessageHandler(x_wrapper, filters=expub_filter), group=0)


async def e_or_r(expub_message, msg_text, parse_mode="md", disable_web_page_preview=True):
    message = expub_message
    le_sudos = SUDO_IDS
    if not message:
        return await message.edit(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    if not message.from_user:
        return await message.edit(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    if message.from_user.id in SUDO_IDS:
        if message.reply_to_message:
            return await message.reply_to_message.reply_text(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
        else:
            return await message.reply_text(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    else:
        return await message.edit(msg_text, parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)



def expub_on_cmd(
    command,
    modlue,
    admins_only: bool = False,
    only_pm: bool = False,
    only_groups: bool = False,
    no_sudos: bool = False
):
    if no_sudos:
        expub_filter = (filters.me & filters.command(command, Config.CMD_PREFIX) & ~filters.via_bot & ~filters.forwarded)
    else:
        expub_filter = (filters.user(SUDO_IDS) & filters.command(command, Config.CMD_PREFIX) & ~filters.via_bot & ~filters.forwarded)
    def decorate_expub(func):
        async def x_wrapper(client, message):
            expub_chat_type = message.chat.type
            if only_groups and expub_chat_type != "supergroup":
                await message.edit("`Is this even a group?`")
                return
            if only_pm and expub_chat_type != "private":
                await message.edit("`Yo, this command is only for PM!`")
                return
            try:
                await func(client, message)
            except MessageIdInvalid:
                logging.warning("Don't delete message while processing. It may crash the bot!")
            except BaseException as e:
                logging.error(f"\nModule - {modlue} | Command: {command}")
                error_text = f"""
**#ERROR**
**Module:** `{modlue}`
**Command:** `{Config.CMD_PREFIX + command}`
**Traceback:**
`{e}`
Forward this to @kenbotsupport
"""
                if len(error_text) > 4000:
                    file = open("error_expub.txt", "w+")
                    file.write(error_text)
                    file.close()
                    await EXPUB.send_document(LOG_CHANNEL_ID, "error_expub.txt", caption="`Error of Exp Userbot`")
                    os.remove("error_expub.txt")
                else:
                    await EXPUB.send_message(chat_id=LOG_CHANNEL_ID, text=error_text)
        add_handler(x_wrapper, expub_filter)
        return x_wrapper
    return decorate_expub


# Custom filter handling (Credits: Friday Userbot)
def expub_on_cf(custom_filters):
    def decorate_expub_cf(func):
        async def x_wrapper_cf(client, message):
            try:
                await func(client, message)
            except MessageIdInvalid:
                logging.warning("Don't delete message while processing. It may crash the bot!")
            except BaseException as e:
                logging.error(f"\nModule - {func.__module__} | Command: (Noting, Custom Filter)")
                error_text = f"""
**#ERROR**
**Module:** `{func.__module__}`
**Command:** `(Noting, Custom Filter)`
**Traceback:**
`{e}`
Forward this to @kenbotsupport
"""
                if len(error_text) > 4000:
                    file = open("error_expub.txt", "w+")
                    file.write(error_text)
                    file.close()
                    await EXPUB.send_document(LOG_CHANNEL_ID, "error_expub.txt", caption="`Error of Exp Userbot`")
                    os.remove("error_expub.txt")
                else:
                    await EXPUB.send_message(chat_id=LOG_CHANNEL_ID, text=error_text)
            message.continue_propagation()
        EXPUB.add_handler(MessageHandler(x_wrapper_cf, filters=custom_filters), group=0)
        return x_wrapper_cf
    return decorate_expub_cf
