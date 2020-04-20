import time

from kutana import Message, HandlerResponse

from bot.db import ChatUser, User
from bot.plugin import CustomPlugin as Plugin
from bot.plugins.kick import kick_users
from bot.roles import admin_role, needed_admin_rights, ChatUserRoles
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
        await ctx.send_message(ctx.config['owner_id'], 'pass1')
        return HandlerResponse.SKIPPED

    # not action message OR not appropriate type of action
    if (action := msg.raw['object']['message'].get('action', {'type': ''}))['type'] != 'chat_kick_user' and \
            not action['type'].startswith('chat_invite_user'):
        await ctx.send_message(ctx.config['owner_id'], 'pass2')
        return HandlerResponse.SKIPPED

    # banned user invited to chat
    if action['type'].startswith('chat_invite_user'):
        user_added, _ = await ctx.mgr.get_or_create(User, id=action['member_id'])
        chat_user_added, _ = await ctx.mgr.get_or_create(ChatUser, user=user_added, chat=ctx.chat)
        if not chat_user_added.banned:
            await ctx.send_message(ctx.config['owner_id'], 'pass3')
            return HandlerResponse.SKIPPED
        if (chat_user_added.banned_until == -1 or chat_user_added.banned_until > time.time())\
                and ctx.chat_user.role < ChatUserRoles.ADMIN:
            await ctx.send_message(ctx.config['owner_id'], 'ban')
            return await kick_users(ctx, [chat_user_added], msg.receiver_id - 2 * 10 ** 9)
        else:
            chat_user_added.banned = False
            chat_user_added.banned_until = 0
            await ctx.mgr.update(chat_user_added)
            await ctx.reply(f'[id{chat_user_added.user.get_id}|Пользователь] разбанен', disable_mentions=1)
            return
    if not ctx.chat.kick_left:
        return HandlerResponse.SKIPPED

    # somebody kicked user
    if action['member_id'] != msg.sender_id:
        return HandlerResponse.SKIPPED

    await kick_users(ctx, [ctx.chat_user], msg.receiver_id - 2 * 10 ** 9)
