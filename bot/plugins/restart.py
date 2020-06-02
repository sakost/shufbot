import os
import sys
import time

from kutana import Context

from bot.plugin import CustomPlugin as Plugin
from bot.roles import developer_global_role
from bot.utils import get_users

plugin = Plugin('Manage process', '(re)start bot')


@plugin.on_start()
async def _(app):
    if len(sys.argv) == 5 and sys.argv[1] == '--restarted':
        for backend in app.get_backends():
            if backend.get_identity() == 'vkontakte':
                elapsed_time = time.time() - float(sys.argv[2])
                chat_id = int(sys.argv[3])
                user_id = int(sys.argv[4])
                user = (await get_users(backend, user_id, 'ins'))[0]
                user_name = user['first_name'] + ' ' + user['last_name']
                await backend.send_message(chat_id,
                                           f"Бот был перезапущен [id{user_id}|{user_name}] за {elapsed_time:.2f} сек",
                                           disable_mentions=1)


@plugin.on_commands(['рестарт', 'restart'])
@developer_global_role
async def restart_command(msg, ctx: Context):
    await ctx.reply('Перезагружаюсь...')
    os.execl(sys.executable,
             sys.executable,
             sys.argv[0],
             "--restarted",
             str(time.time()),
             str(msg.receiver_id),
             str(msg.sender_id))
