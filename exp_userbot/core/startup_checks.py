import asyncio
from pyrogram.errors import YouBlockedUser
from exp_userbot import EXPUB
from exp_userbot.core.expub_database.expub_db_conf import set_log_channel, get_log_channel, set_arq_key, get_arq_key
from config import Config

# Log Channel Checker
async def check_or_set_log_channel():
    try:
        log_channel_id = await get_log_channel()
        if log_channel_id:
            return [True, log_channel_id]
        else:
            log_channel = await EXPUB.create_channel(title="Exp Userbot Logs", description="Logs of your Exp Userbot")
            welcome_to_expub = f"""
EXP USERBOT IS RUNNING

If you don't know how to use this Userbot please send `{Config.CMD_PREFIX}help` in any chat.

**Group support : @kenbotsupport**
**~ Exp Userbot [Authors](https://t.me/xgothboi)**"""
            log_channel_id = log_channel.id
            await set_log_channel(log_channel_id)
            await EXPUB.send_message(chat_id=log_channel_id, text=welcome_to_expub, disable_web_page_preview=True)
            return [True, log_channel_id]
    except Exception as e:
        print(f"Error \n\n{e} \n\nPlease check all variables and try again! \nReport this with logs at @kenbotsupport if the problem persists!")
        exit()


# ARQ API KEY Checker
async def check_arq_api():
    try:
        try:
            await EXPUB.send_message("ARQRobot", "/start")
        except YouBlockedUser:
            await EXPUB.unblock_user("ARQRobot")
            await asyncio.sleep(0.2)
            await EXPUB.send_message("ARQRobot", "/start")
        await asyncio.sleep(0.5)
        await EXPUB.send_message("ARQRobot", "/get_key")
        get_h = (await EXPUB.get_history("ARQRobot", 1))[0]
        g_history = get_h.text
        if "X-API-KEY:" not in g_history:
            expub_user = await EXPUB.get_me()
            arq_acc_name = expub_user.first_name if expub_user.first_name else f"Unknown_{expub_user.id}"
            await asyncio.sleep(0.4)
            await EXPUB.send_message("ARQRobot", f"{arq_acc_name}")
            await asyncio.sleep(0.3)
            gib_history = (await EXPUB.get_history("ARQRobot", 1))[0]
            g_history = gib_history.text
            arq_api_key = g_history.replace("X-API-KEY: ", "")
        else:
            arq_api_key = g_history.replace("X-API-KEY: ", "")
        is_arqed = await get_arq_key()
        if is_arqed is None:
            await set_arq_key(arq_api_key)
        else:
            pass
    except Exception as e:
        print(f"Error \n\n{e} \n\nThere was a problem while obtaining ARQ API KEY. However you can set it manually. Send, \n{Config.CMD_PREFIX}setvar ARQ_API_KEY your_api_key_here")
