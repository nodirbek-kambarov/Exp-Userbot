import asyncio

from pyrogram import idle
from exp_userbot import EXPUB
from exp_userbot.modules import *
from exp_userbot.core.startup_checks import check_or_set_log_channel, check_arq_api
from exp_userbot.core.expub_database.expub_db_conf import get_log_channel
from config import Config


async def main_startup():
    print("""
|| Exp Userbot ||
Copyright (c) 2021 KennedyProject
"""
    )
    await EXPUB.start()
    await check_or_set_log_channel()
    await check_arq_api()
    log_channel_id = await get_log_channel()
    await EXPUB.send_message(chat_id=log_channel_id, text="`Exp Userbot is started Successfully!`")
    await idle()

loop = asyncio.get_event_loop()
loop.run_until_complete(main_startup())
