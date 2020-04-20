import time

from kutana import Message, HandlerResponse

from bot.plugin import CustomPlugin as Plugin
from bot.plugins.kick import kick_users
from bot.roles import admin_role, needed_admin_rights
from bot.router import AnyMessageRouterCustom

plugin = Plugin('Autokick', 'Автокик вышедших')

COMMANDS = {
    'on': 1,
    'off': 0,
    'вкл': 1,
    'выкл': 0,
}


@plugin.on_commands(['автокик', 'autokick'])
@admin_role
async def _(msg, ctx):
    if ctx.body:
        msg = ctx.body.lower()
        for cmd in COMMANDS:
            if msg.startswith(cmd):
                action = COMMANDS[cmd]
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

    # not action message OR not appropriate type of action
    if (action := msg.raw['object']['message'].get('action', {'type': ''}))['type'] != 'chat_kick_user' and \
            not action['type'].startswith('chat_invite_user'):
        return HandlerResponse.SKIPPED

    # banned user invited to chat
    if ctx.user.banned and action['type'].startswith('chat_invite_user'):
        if ctx.user.banned_until == -1 or ctx.user.banned_until > time.time():
            return await kick_users(ctx, [msg.sender_id], msg.receiver_id - 2 * 10 ** 9)
        else:
            ctx.user.banned = False
            ctx.user.banned_until = 0
            await ctx.mgr.update(ctx.user)
            return

    # somebody kicked user
    if action['member_id'] != msg.sender_id:
        return HandlerResponse.SKIPPED

    await kick_users(ctx, [msg.sender_id], msg.receiver_id - 2 * 10 ** 9)
