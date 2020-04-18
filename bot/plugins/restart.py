import os
import sys
import time

from kutana import Plugin, Context

from bot.roles import admin_role

plugin = Plugin('Restart', 'restart bot')


@plugin.on_start()
async def _(app):
    if len(sys.argv) == 5 and sys.argv[1] == '--restarted':
        for backend in app.get_backends():
            if backend.get_identity() == 'vkontakte':
                elapsed_time = time.time() - int(sys.argv[2])
                chat_id = int(sys.argv[3])
                user_id = int(sys.argv[4])
                user = (await backend.request('users.get', user_ids=user_id, name_case='ins'))[0]
                user_name = user['first_name'] + ' ' + user['last_name']
                await backend.send_message(chat_id,
                                           f"Бот был перезапущен [id{user_id}|{user_name}] за {elapsed_time:.2} сек")


@plugin.on_commands(['рестарт', 'restart'])
@admin_role
async def _(msg, ctx: Context):
    await ctx.reply('Перезагружаюсь...')
    os.execl(sys.executable, sys.executable,
             sys.argv[0], "--restarted", str(int(time.time())), ctx.user_uid[:-len(ctx.backend.get_identity())],
             str(msg.raw['object']['message']['from_id']))
