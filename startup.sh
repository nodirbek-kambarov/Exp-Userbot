echo "
RUNNING THE

       ███████╗██╗  ██╗██████╗ 
       ██╔════╝╚██╗██╔╝██╔══██╗
       █████╗   ╚███╔╝ ██████╔╝
       ██╔══╝   ██╔██╗ ██╔═══╝ 
       ███████╗██╔╝ ██╗██║     
       ╚══════╝╚═╝  ╚═╝╚═╝    
             TELEGRAM USERBOT

Copyright (c) 2021 KennedyProject
"

start_expub () {
    if [[ -z "$PYRO_STR_SESSION" ]]
    then
	    echo "Please add Pyrogram String Session"
    else
	    python3 -m exp_userbot
    fi
  }

_install_expub () {
    start_expub
  }

_install_expub
