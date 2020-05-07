from bot.plugin import CustomPlugin as Plugin
from bot.utils import on_or_off

plugin = Plugin('Упоминания', 'Тогл упоминаний')


@plugin.on_commands(['упоминания', 'mentions', "упом", "setmention"])
async def _(msg, ctx):
    if ctx.body:
        msg = ctx.body.lower()
        action = on_or_off(msg)
        if action is not None:
            ctx.user.mention = bool(action)
            await ctx.mgr.update(ctx.user)
    await ctx.reply(f'Упоминания {"включены" if ctx.user.mention else "выключены"}')
