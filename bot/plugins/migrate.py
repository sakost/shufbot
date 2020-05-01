import asyncio

from kutana import Plugin

from bot.roles import developer_global_role
from bot.plugins.restart import restart_command
from bot.db import database as db
plugin = Plugin('Update bot[develop]')

@plugin.on_commands(['мигр', 'migr', 'migrate', 'миграция', 'мигрируй'])
@developer_global_role
async def _(msg, ctx):
    with ctx.mgr.allow_sync():
        db.evolve()
    await restart_command(msg, ctx)
