
# Copyright (c) 2021 Itz-fork
# Part of: Nexa-Userbot
# Credits: Developers Userbot
import os
from pyrogram.types import Message

from exp_userbot import EXPUB, HELP, CMD_HELP
from config import Config
from exp_userbot.helpers.pyrogram_help import get_arg
from exp_userbot.core.main_cmd import expub_on_cmd, e_or_r


# Help
HELP.update(
    {
        "**🧭 Userbot**": "`alive`, `installer`, `updater`",
        "**👨‍💻 Dev**": "`eval`",
        "**⚙️ Tools**": "`paste`, `short_url`, `search`, `pictools`, `extractor`, `megatools`, `arq`, `telegraph`",
        "**🗂 Utils**": "`stickers`, `owner`, `sudos`, `afk`, `globals`",
        "\n**Usage**": "`.help [module_name]`"
    }
)

mod_file = os.path.basename(__file__)

@expub_on_cmd(command="help", modlue=mod_file)
async def help(_, message: Message):
    args = get_arg(message)
    help_user_msg = await e_or_r(expub_message=message, msg_text="`Processing...`")
    if not args:
        text = "**Available Commands**\n\n"
        for key, value in HELP.items():
            text += f"{key}: {value}\n\n"
        await help_user_msg.edit(text)
        return
    else:
        module_help = CMD_HELP.get(args, False)
        if not module_help:
            await help_user_msg.edit("`Invalid Module Name!`")
            return
        else:
            await help_user_msg.edit(module_help)
