import io
import sys
import traceback
import contextlib

from kutana import Plugin

from bot.roles import developer_global_role

plugin = Plugin('Execute[admin]', description='выполняет укаазанную команду')


@plugin.on_commands(['exec', 'execute'])
@developer_global_role
async def _(msg, ctx):
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(
                "async def __ex(msg, ctx): " + ctx.body,
            )
            await locals()['__ex'](msg, ctx)
    except Exception as e:
        await ctx.reply(f"Error occurred:\n{''.join(traceback.format_exception_only(*sys.exc_info()[:2]))}")
    finally:
        out_text = output.getvalue()
        if out_text:
            await ctx.reply(f"Command output:\n{}")
        output.close()
