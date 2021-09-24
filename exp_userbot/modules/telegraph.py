# Copyright (c) 2021 Itz-fork

import os

from telegraph import Telegraph, upload_file
from pyrogram.types import Message

from exp_userbot import EXPUB, CMD_HELP
from exp_userbot.core.main_cmd import expub_on_cmd, e_or_r, expub_on_cf
from exp_userbot.helpers.pyrogram_help import get_arg, convert_to_image
from config import Config


# Help
CMD_HELP.update(
    {
        "telegraph": f"""
**Telegraph,**
  ✘ `tgm` - To Paste Images/Text to Telegra.ph
**Example:**
  ✘ `tgm`,
   ⤷ Reply to a message that contains text/image/mp4 file  = `{Config.CMD_PREFIX}tgm`
     Tip: While pasting text to telegra.ph you can send title with command
"""
    }
)

mod_file = os.path.basename(__file__)


# Telegraph client
telegraph = Telegraph()
telegraph.create_account(short_name="Exp-Userbot")

# Paste text to telegraph
async def paste_text_to_tgraph(title, text):
  try:
    expub_usr = await EXPUB.get_me()
    f_name = expub_usr.first_name
    u_name = expub_usr.username
    if title is None:
      title = f_name if f_name is not None else "By Exp Userbot"
    t_response = telegraph.create_page(title=title, html_content=text, author_name=f_name if f_name is not None else "Exp-Userbot", author_url=f"https://t.me/{u_name}" if u_name is not None else "https://github.com/KennedyProject/Exp-Userbot")
    return f"**Telegraph Link:** {t_response['url']}"
  except Exception as e:
    return f"**Error:** {e}"

# Upload image to telegraph
async def upload_to_tgraph(file):
  try:
    t_response = upload_file(file)
    return f"**Telegraph Link:** https://telegra.ph/{t_response[0]}"
  except Exception as e:
    return f"**Error:** {e}"


@expub_on_cmd(command="tgm", modlue=mod_file)
async def me_goin_oflin(_, message: Message):
    tgraph_msg = await e_or_r(expub_message=message, msg_text="`Processing...`")
    r_msg = message.reply_to_message
    arg_txt = get_arg(message)
    if r_msg:
        if r_msg.photo or r_msg.video or r_msg.video_note:
          r_content = await r_msg.download()
          up_to_tgraph = await upload_to_tgraph(r_content)
          await tgraph_msg.edit(up_to_tgraph)
        elif r_msg.sticker:
          r_content = await convert_to_image(message=r_msg, client=EXPUB)
          up_to_tgraph = await upload_to_tgraph(r_content)
          await tgraph_msg.edit(up_to_tgraph)
        elif r_msg.text:
          r_content = r_msg.text
          if arg_txt:
            t_title = arg_txt
          else:
            t_title = None
          t_pasted = await paste_text_to_tgraph(title=t_title, text=r_content)
          await tgraph_msg.edit(t_pasted)
        else:
          tgraph_msg.edit("`No Supported Media or Text to paste!`")
    else:
      return await tgraph_msg.edit("Reply to a message that contains `text`/`image` or `mp4 file`!")
