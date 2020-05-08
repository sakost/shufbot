from kutana import HandlerResponse

from bot.plugin import CustomPlugin as Plugin
from bot.utils import on_or_off, get_names
from bot.roles import ChatUserRoles, chat_only
import re
from bot.plugins.warn import warn

pattern = re.compile(r"(:?@all|@online|@everyone)", re.MULTILINE)
plugin = Plugin('Упоминания', 'Тогл упоминаний')


@plugin.on_commands(['mentionall', 'упомвсех'])
async def _(msg, ctx):
    if ctx.body:
        msg = ctx.body.lower()
        action = on_or_off(msg)
        ctx.chat.mention_all = bool(action)
        await ctx.mgr.update(ctx.chat)
    await ctx.reply(f'Кик за упоминания всех {"включен" if ctx.chat.mention_all else "выключен"}')


@plugin.on_any_message(priority=12)
@chat_only(reply=False)
async def _(msg, ctx):
    if ctx.chat.mention_all and pattern.search(msg.text) is not None:
        kicked, warned = await warn(
            ctx, ctx.user.id, ctx.chat.id, ChatUserRoles.VIP_USER.value)
        if kicked:
            names_kicked = await get_names(ctx, kicked, "", True, True)
            await ctx.reply(
                f"{names_kicked} были кикнуты за"
                f" превышение лимита в {ctx.chat.max_warns} варн(-а).")
        if warned:
            names_warned = await get_names(ctx, warned, "", True, True)
            await ctx.reply(
                f"{names_warned} был выдан варн за упоминание всех"
                " участников.")
        return
    return HandlerResponse.SKIPPED
