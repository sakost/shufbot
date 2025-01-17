import asyncio

from kutana import Plugin

from bot.plugins.restart import restart_command
from bot.roles import developer_global_role

plugin = Plugin('Update bot[develop]')


@plugin.on_commands(['упд', 'upd', 'обнови', 'update', 'upgrade'])
@developer_global_role
async def _(msg, ctx):
    proc = await asyncio.create_subprocess_shell('git pull',
                                                 shell=True,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE,
                                                 stdin=asyncio.subprocess.PIPE,
                                                 loop=ctx.app.get_loop()
                                                 )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0 and stderr:
        await ctx.reply('Во время обновления произошла ошибка:\n' + stderr.decode())
    if stdout:
        await ctx.reply(stdout.decode())
    await restart_command(msg, ctx)
