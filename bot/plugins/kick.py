from kutana import Plugin

from bot.roles import admin_role, needed_admin_rights
from bot.utils import extract_users
from bot.db import ChatUser, User

plugin = Plugin('Kick', 'кикает пользователя из беседы')


@plugin.on_commands(['бан', 'ban', 'кик', 'kick'])
@needed_admin_rights
@admin_role
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    if users:
        await kick_users(ctx, users, msg.receiver_id - 2*10**9)
    else:
        await ctx.reply('Вы не указали ни одного пользователя')


async def kick_users(ctx, users, chat_id):
    async with ctx.mgr.atomic():
        for user_id in users:
            if isinstance(user_id, ChatUser):
                chat_user = user_id
            else:
                user, _ = await ctx.mgr.get_or_create(User, id=user_id)
                chat_user, _ = await ctx.mgr.get_or_create(ChatUser, user=user, chat=ctx.chat)
            chat_user.banned = True
            chat_user.banned_until = -1
            await ctx.mgr.update(chat_user)
            await ctx.request('messages.removeChatUser', chat_id=chat_id, member_id=chat_user.user.get_id)
