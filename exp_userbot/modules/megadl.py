# Copyright (c) 2021 Itz-fork

import os
import subprocess
import shutil

from pyrogram import filters
from pyrogram.types import Message
from functools import partial
from asyncio import get_running_loop
from fsplit.filesplit import Filesplit

from exp_userbot import EXPUB, CMD_HELP
from exp_userbot.helpers.up_to_tg import guess_and_send
from exp_userbot.core.main_cmd import expub_on_cmd, e_or_r
from config import Config


# Help
CMD_HELP.update(
    {
        "megatools": f"""
**Megatools,**
  ✘ `megadl` - To Download Files / Folder from Mega.nz
**Example:**
  ✘ `megadl`
   ⤷ Send with command = `{Config.CMD_PREFIX}megadl https://mega.nz/file/#43445234` (Link is fake tho)
**Both files and folders are supported**
"""
    }
)

mod_file = os.path.basename(__file__)

# Download path
megadir = "./ExpUb/Megatools"

# Run bash cmd in python
def exp_mega_runner(command):
    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    shell_ouput = run.stdout.read()[:-1].decode("utf-8")
    return shell_ouput

# Splitting large files
def split_files(input_file, out_base_path):
    exp_fs = Filesplit()
    split_file = input_file
    split_fsize = 2040108421
    out_path = out_base_path
    exp_fs.split(file=split_file, split_size=split_fsize, output_dir=out_path)

@expub_on_cmd(command="megadl", modlue=mod_file)
async def megatoolsdl(_, message: Message):
    megatools_msg = await e_or_r(expub_message=message, msg_text="`Processing...`")
    url = message.text
    cli_user_id = str(message.from_user.id)
    cli_download_path = megadir + "/" + cli_user_id
    if len(message.command) < 2:
        await megatools_msg.edit("`Please send a valid mega.nz link to download!`")
        return
    # Mega url to download
    cli_url = url.split(None, 1)[1]
    # Checking if sent message has a vaild mega.nz url
    if "https://mega.nz/" not in url:
        await megatools_msg.edit("`Please send a valid mega.nz link to download!`")
        return
    # Checking if there is a ongoing task for the user
    if os.path.isdir(cli_download_path):
        await megatools_msg.edit("`Already One Process is Going On. Please wait until it's finished!`")
        return
    else:
        os.makedirs(cli_download_path)
    await megatools_msg.edit(f"`Starting to download file / folder from mega.nz!` \n\nThis may take sometime. Depends on your file / folder size.")
    megacmd = f"megadl --limit-speed 0 --path {cli_download_path} {cli_url}"
    loop = get_running_loop()
    await loop.run_in_executor(None, partial(exp_mega_runner, megacmd))
    expub_path_f = f"{os.getcwd()}/ExpUb/Megatools/{str(message.from_user.id)}"
    folder_f = [val for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(expub_path_f)] for val in sublist]
    print(folder_f)
    await megatools_msg.edit("`Downloading Finished! Trying to upload now`")
    try:
        for exp_m in folder_f:
            file_size = os.stat(exp_m).st_size
            if file_size > 2040108421:
                split_out_dir = expub_path_f + "splitted_files"
                await megatools_msg.edit("`Large File Detected, Trying to split it!`")
                loop = get_running_loop()
                await loop.run_in_executor(None, partial(split_files(input_file=exp_m, out_base_path=split_out_dir)))
                await megatools_msg.edit("`Splitting Finished! Uploading Now...`")
                for splitted_f in split_out_dir:
                    await EXPUB.send_document(chat_id=message.chat.id, document=splitted_f, caption=f"`Uploaded by` {(await EXPUB.get_me()).mention}")
            else:
                chat_id = message.chat.id
                await guess_and_send(input_file=exp_m, chat_id=chat_id, thumb_path=expub_path_f)
        await megatools_msg.edit("`Uploading Finished!`")
    except Exception as e:
        await megatools_msg.edit(f"**Error:** `{e}`")
    try:
        shutil.rmtree(expub_path_f)
    except Exception as e:
        await megatools_msg.edit(f"**Error:** `{e}`")
