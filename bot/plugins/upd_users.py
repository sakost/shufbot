import asyncio

from kutana import Plugin

from bot.db import User, ChatUser
from bot.roles import chat_only, needed_admin_rights, ChatUserRoles

plugin = Plugin('Update users', 'обновляет информацию по пользователям в чате в базу данных')


@plugin.on_commands(['updusers', 'updchat', 'упдчат', 'упдюзеры', 'update-chat', 'update-users'])
@chat_only()
@needed_admin_rights
async def _(msg, ctx):
    await update_users(ctx)
    await ctx.reply('Информация об участниках беседы была обновлена')


async def update_users(ctx):
    resp = await ctx.request('messages.getConversationMembers', peer_id=ctx.chat.id)
    for member in resp['items']:
        user, _ = await ctx.mgr.get_or_create(User, id=member['member_id'])
        chat_user, _ = await ctx.mgr.get_or_create(ChatUser, user=user, chat=ctx.chat)
        if member.get('is_owner', False):
            chat_user.role = ChatUserRoles.CREATOR.value
        elif member.get('is_admin', False):
            chat_user.role = ChatUserRoles.ADMIN.value
        elif chat_user.role != ChatUserRoles.VIP_USER.value:
            chat_user.role = ChatUserRoles.USER.value
        await ctx.mgr.update(chat_user)
        await asyncio.sleep(0)
