import heroku3
import asyncio
import sys
import os

from os import environ, execle, path, remove
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from exp_userbot import EXPUB, CMD_HELP
from config import Config
from exp_userbot.helpers.pyrogram_help import get_arg
from exp_userbot.core.main_cmd import expub_on_cmd, e_or_r


# Help
CMD_HELP.update(
    {
        "updater": """
**Updater**
  ✘ `update` - To Updater Your Userbot
  ✘ `restart` - To Restart Your Userbot (Heroku Only)
  ✘ `logs` - To Get Logs of Your Userbot (Heroku Only)
"""
    }
)

mod_file = os.path.basename(__file__)

UPSTREAM_REPO_URL = "https://github.com/KennedyProject/Exp-Userbot"
requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "requirements.txt"
)


async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "On %d/%m/%y at %H:%M:%S"
    for c in repo.iter_commits(diff, max_count=10):
        ch_log += f"**#{c.count()}** : {c.committed_datetime.strftime(d_form)} : [{c.summary}]({UPSTREAM_REPO_URL.rstrip('/')}/commit/{c}) by `{c.author}`\n"
    return ch_log


async def updateme_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


async def deploy(event, repo, ups_rem, ac_br, txt):
    if HEROKU_API_KEY is not None:
        import heroku3
        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if HEROKU_APP_NAME is None:
            await event.edit(
                '`[HEROKU]: Harap Siapkan Variabel` **HEROKU_APP_NAME** `'
                ' untuk dapat deploy perubahan terbaru dari 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓`'
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await event.edit(
                f'{txt}\n`Kredensial Heroku tidak valid untuk deploy KEN-UBOT dyno.`'
            )
            return repo.__del__()
        await event.edit('`[HEROKU]:'
                         '\nSedang MengUpdate 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓, Mohon Menunggu 5-7 Menit`'
                         )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@")
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/main", force=True)
        except GitCommandError as error:
            await event.edit(f'{txt}\n`Terjadi Kesalahan Di Log:\n{error}`')
            return repo.__del__()
        build = app.builds(order_by="created_at", sort="desc")[0]
        if build.status == "failed":
            await event.edit(
                "`Build Gagal!\n" "Dibatalkan atau ada beberapa kesalahan...`"
            )
            await asyncio.sleep(5)
            return await event.delete()
        else:
            await event.edit("`KEN-UBOT Berhasil Di Deploy!\n" "Restarting, Mohon Tunggu Sebentar.....`")
            await asyncio.sleep(15)
            await event.delete()
    else:
        await event.edit('`[HEROKU]:'
                         '\nHarap Siapkan Variabel` **HEROKU_API_KEY** `.`'
                         )
        await asyncio.sleep(10)
        await event.delete()
    return


async def update(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await update_requirements()
    await event.edit('**𝐊𝐄𝐍-𝐔𝐁𝐎𝐓** `Berhasil Di Update!`')
    await asyncio.sleep(1)
    await event.edit('**𝐊𝐄𝐍-𝐔𝐁𝐎𝐓** `Di Restart....`')
    await asyncio.sleep(1)
    await event.edit('`Mohon Menunggu Beberapa Detik.`')
    await asyncio.sleep(10)
    await event.delete()

    # Spin a new instance of bot
    args = [sys.executable, "-m", "exp-userbot"]
    execle(sys.executable, *args, environ)
    return


@expub_on_cmd(command="update", modlue=mod_file)
async def upstream(event):
    "For .update command, check if the bot is up to date, update if specified"
    await event.edit("`Mengecek Pembaruan, Silakan Menunggu....`")
    conf = event.pattern_match.group(1)
    off_repo = UPSTREAM_REPO_URL
    force_update = False
    try:
        txt = "`Mohon Maaf, Pembaruan Tidak Dapat Di Lanjutkan Karna "
        txt += "Beberapa Masalah Terjadi`\n\n**LOGTRACE:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f'{txt}\n`Directory {error} Tidak Dapat Di Temukan`')
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f'{txt}\n`Gagal Awal! {error}`')
        return repo.__del__()
    except InvalidGitRepositoryError as error:
        if conf is None:
            return await event.edit(
                f"`Sayangnya, Directory {error} Tampaknya Bukan Dari Repo."
                "\nTapi Kita Bisa Memperbarui Paksa Userbot Menggunakan .update now.`"
            )
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        force_update = True
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)

    ac_br = repo.active_branch.name
    if ac_br != UPSTREAM_REPO_BRANCH:
        await event.edit(
            '**[UPDATER]:**\n'
            f'`Looks like you are using your own custom branch ({ac_br}). '
            'in that case, Updater is unable to identify '
            'which branch is to be merged. '
            'please checkout to any official branch`')
        return repo.__del__()
    try:
        repo.create_remote('upstream', off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote('upstream')
    ups_rem.fetch(ac_br)

    changelog = await gen_chlog(repo, f'HEAD..upstream/{ac_br}')

    if changelog == '' and force_update is False:
        await event.edit(
            f'\n☄️ 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓 Sudah Versi Terbaru\n')
        await asyncio.sleep(15)
        await event.delete()
        return repo.__del__()

    if conf is None and force_update is False:
        changelog_str = f'**Pembaruan Untuk 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓 :\n\n➣ Pembaruan Data :**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await event.edit("`Changelog Terlalu Besar, Lihat File Untuk Melihatnya.`")
            file = open("output.txt", "w+")
            file.write(changelog_str)
            file.close()
            await event.client.send_file(
                event.chat_id,
                "output.txt",
                reply_to=event.id,
            )
            remove("output.txt")
        else:
            await event.edit(changelog_str)
        return await event.respond('**Perintah Untuk Update, Sebagai Berikut.**\n Command: >`.update now`\n Command: >`.update deploy`\n\n__Untuk Meng Update Fitur 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓.__')

    if force_update:
        await event.edit(
            '`Sinkronisasi Paksa Ke Kode Userbot Stabil Terbaru, Harap Tunggu .....`')
    else:
        await event.edit('` Proses Update 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓, Loading....1%`')
        await event.edit('` Proses Update 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓, Loading....20%`')
        await event.edit('` Proses Update 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓, Loading....35%`')
        await event.edit('` Proses Update 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓, Loading....77%`')
        await event.edit('` Proses Update 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓, Updating...90%`')
        await event.edit('` Proses Update 𝐊𝐄𝐍-𝐔𝐁𝐎𝐓, Mohon Tunggu Sebentar....100%`')
    if conf == "now":
        await update(event, repo, ups_rem, ac_br)
        await asyncio.sleep(10)
        await event.delete()
    elif conf == "deploy":
        await deploy(event, repo, ups_rem, ac_br, txt)
        await asyncio.sleep(10)
        await event.delete()
    return

# Userbot restart module
async def restart_expub():
    if Config.HEROKU_API_KEY is not None:
        heroku_conn = heroku3.from_key(Config.HEROKU_API_KEY)
        server = heroku_conn.app(Config.HEROKU_APP_NAME)
        server.restart()
    else:
        args = [sys.executable, "-m" "exp_userbot"]
        execle(sys.executable, *args, environ)
        exit()

@expub_on_cmd(command="restart", modlue=mod_file)
async def restart(client, message):
    restart_msg = await e_or_r(expub_message=message, msg_text="`Processing...`")
    await restart_msg.edit("`Exp-Userbot is restarting! Please wait...`")
    try:
        await restart_expub()
    except Exception as e:
        await restart_msg.edit(f"**Error:** `{e}`")
