# Copyright (c) 2021 Itz-fork

import os
import shutil

from pyrogram.types import Message
from py_extract import Video_tools

from exp_userbot import EXPUB, CMD_HELP
from exp_userbot.core.main_cmd import expub_on_cmd, e_or_r
from config import Config

CMD_HELP.update(
    {
        "extractor": f"""
**Extractor**
  ✘ `eud` - To Extract all audios from a video
**Example:**
  ✘ `eud`
   ⤷ Reply to a video file with audio = `{Config.CMD_PREFIX}eud` (Reply to a video file)
"""
    }
)

mod_file = os.path.basename(__file__)


@expub_on_cmd(command="eud", modlue=mod_file)
async def extract_all_aud(_, message: Message):
    replied_msg = message.reply_to_message
    ext_text = await e_or_r(expub_message=message, msg_text="`Processing...`")
    ext_out_path = os.getcwd() + "/" + "ExpUB/py_extract/audios"
    if not replied_msg:
        await ext_text.edit("`Please reply to a valid video file!`")
        return
    if not replied_msg.video:
        await ext_text.edit("`Please reply to a valid video file!`")
        return
    if os.path.exists(ext_out_path):
        await ext_text.edit("`Already one process is going on. Please wait till it finish!`")
        return
    replied_video = replied_msg.video
    try:
        await ext_text.edit("`Downloading...`")
        ext_video = await EXPUB.download_media(message=replied_video)
        await ext_text.edit("`Extracting Audio(s)...`")
        exted_aud = Video_tools.extract_all_audio(input_file=ext_video, output_path=ext_out_path)
        await ext_text.edit("`Uploading...`")
        for exp_aud in exted_aud:
            await message.reply_audio(audio=exp_aud, caption=f"`Extracted by` {(await EXPUB.get_me()).mention}")
        await ext_text.edit("`Extracting Finished!`")
        shutil.rmtree(ext_out_path)
    except Exception as e:
        await ext_text.edit(f"**Error:** `{e}`")
