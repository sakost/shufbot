from bot.plugin import CustomPlugin as Plugin
from bot.roles import admin_role, chat_only
from bot.utils import on_or_off

plugin = Plugin('Упоминания', 'Тогл упоминаний')

@chat_only()
@admin_role
@plugin.on_commands(['упоминания', 'mentions', "упом", "setmention"])
async def _(msg, ctx):
    if ctx.body:
        msg = ctx.body.lower()
        action = on_or_off(msg)
        if action is not None:
            ctx.chat.mention = bool(action)
            await ctx.mgr.update(ctx.chat)
    await ctx.reply(f'Упоминания бота в беседе {"включены" if ctx.chat.mention else "выключены"}')
