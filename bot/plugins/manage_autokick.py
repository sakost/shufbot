from kutana import Message, HandlerResponse

from bot.roles import admin_role, needed_admin_rights
from bot.plugin import CustomPlugin as Plugin
from bot.router import AnyMessageRouterCustom
from bot.plugins.kick import kick_users

plugin = Plugin('Autokick', 'Автокик вышедших')


@plugin.on_commands(['автокик', 'autokick'])
@admin_role
async def _(msg, ctx):
    commands = {
        'on': 1,
        'off': 0,
        'вкл': 1,
        'выкл': 0,
    }
    if ctx.body:
        msg = ctx.body.lower()
        for cmd in commands:
            if msg.startswith(cmd):
                action = commands[cmd]
                ctx.chat.kick_left = bool(action)
                await ctx.mgr.update(ctx.chat)
                break
    await ctx.reply(f'Автокик {"включен" if ctx.chat.kick_left else "выключен"}')


@plugin.on_router(AnyMessageRouterCustom)
@needed_admin_rights
async def _(msg: Message, ctx):
    if not hasattr(ctx, 'chat'):
        return HandlerResponse.SKIPPED
    if not ctx.chat.kick_left:
        return HandlerResponse.SKIPPED
    if (action := msg.raw['object']['message'].get('action', {'type': None}))['type'] != 'chat_kick_user':
        return HandlerResponse.SKIPPED
    if action['member_id'] != msg.sender_id:
        return HandlerResponse.SKIPPED

    await kick_users(ctx, [msg.sender_id], msg.receiver_id-2*10**9)

