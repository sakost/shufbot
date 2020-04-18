import traceback

from kutana import Plugin

from bot.roles import admin_role

plugin = Plugin('Execute[admin]', description='выполняет укаазанную команду')


@plugin.on_commands(['exec', 'execute'])
@admin_role
async def _(msg, ctx):
    try:
        exec(ctx.body)
    except Exception as e:
        ctx.reply(f"Error occurred:\n{''.join(traceback.format_exc(e))}")
