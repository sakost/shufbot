from bot.db import ChatUser, User
from bot.roles import admin_role, needed_admin_rights, chat_only
from bot.utils import extract_users
from bot.plugin import CustomPlugin as Plugin

plugin = Plugin('Kick', 'кикает пользователя из беседы')


@plugin.on_commands(['бан', 'ban'])
@chat_only()
@admin_role
@needed_admin_rights
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    if users:
        await kick_users(ctx, users, msg.receiver_id - 2 * 10 ** 9)
    else:
        await ctx.reply('Вы не указали ни одного пользователя')


@plugin.on_commands(['кик', 'kick'])
@chat_only()
@admin_role
@needed_admin_rights
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    if users:
        await kick_users(ctx, users, msg.receiver_id - 2 * 10 ** 9, ban=False)
    else:
        await ctx.reply('Вы не указали ни одного пользователя')


async def kick_users(ctx, users, chat_id, ban=True):
    async with ctx.mgr.atomic():
        for user_id in users:
            if isinstance(user_id, tuple):
                chat_user = user_id[1]
                user = user_id[0]
            else:
                user, _ = await ctx.mgr.get_or_create(User, id=user_id)
                chat_user, _ = await ctx.mgr.get_or_create(ChatUser, user=user, chat=ctx.chat)
            await ctx.request('messages.removeChatUser', chat_id=chat_id, member_id=user.id)
            if ban:
                chat_user.banned = True
                chat_user.banned_until = -1
                await ctx.mgr.update(chat_user)
