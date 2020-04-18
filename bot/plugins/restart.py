import os
import sys

from kutana import Plugin

from bot.roles import admin_role

plugin = Plugin('Restart', 'restart bot')


@plugin.on_commands(['рестарт', 'restart'])
@admin_role
async def _(msg, ctx):
    await ctx.reply('Перезагружаюсь...')
    os.execl(sys.executable, f'"{sys.executable}"', *sys.argv)

