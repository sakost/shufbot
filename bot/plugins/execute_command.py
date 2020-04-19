import sys
import traceback

from kutana import Plugin

from bot.roles import developer_global_role

plugin = Plugin('Execute[admin]', description='выполняет укаазанную команду')


@plugin.on_commands(['exec', 'execute'])
@developer_global_role
async def _(msg, ctx):
    try:
        exec(
            "async def __ex(msg, ctx): " + ctx.body,
        )
        await locals()['__ex'](msg, ctx)
    except Exception as e:
        await ctx.reply(f"Error occurred:\n{''.join(traceback.format_exception_only(*sys.exc_info()[:2]))}")
