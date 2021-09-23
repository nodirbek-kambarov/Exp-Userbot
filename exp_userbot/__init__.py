# Thanks to Itz-fork

import sys
import time
import time

from pyrogram import Client
from config import Config

# Helps
HELP = {}
CMD_HELP = {}
EXPUB_VERSION = "v0.0.0.1"

StartTime = time.time()

EXPUB = Client(
    api_hash=Config.API_HASH,
    api_id=Config.APP_ID,
    session_name=Config.PYRO_STR_SESSION
)
