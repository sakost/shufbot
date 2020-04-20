from kutana import Plugin

from bot.roles import admin_role, ChatUserRoles, chat_only
from bot.utils import extract_users
from bot.db import ChatUser, User


CHAT_USER_ROLES = {
    ChatUserRoles.USER: ('пользователь', 'юзер', 'user'),
    ChatUserRoles.VIP_USER: ('vip-пользователь', 'vip', 'vip-user'),
    ChatUserRoles.ADMIN: ('администратор', 'admin', 'админ'),
    ChatUserRoles.CREATOR: ('создатель', 'creator', 'креатор'),
}

plugin = Plugin('Manage chat users[develop]', 'Manage chat users roles')


@plugin.on_commands(['set_role', 'сетроль'])
@admin_role
@chat_only
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    for lvl, lvl_names in CHAT_USER_ROLES.items():
        if lvl == ChatUserRoles.ADMIN and ctx.chat_user.role < ChatUserRoles.CREATOR.value:
            break
        for name in lvl_names:
            if ctx.body.startswith(name):
                async with ctx.mgr.atomic():
                    for user_id in users:
                        user, _ = await ctx.mgr.get_or_create(User, id=user_id)
                        chat_user, _ = await ctx.mgr.get_or_create(ChatUser, user=user, chat=ctx.chat)
                        chat_user.role = lvl.value
                        await ctx.mgr.update(chat_user)
                await ctx.reply(f'Пользователям установлен уровень доступа {name}')
                return
    await ctx.reply('Неизвестный уровень доступа для пользователя. Доступные уровни: \n' + '\n'.join(
        f"{num}){', '.join(lvl_names)}" for num, lvl_names in
        enumerate(list(CHAT_USER_ROLES.values())[:-1-bool(ctx.chat_user.role != ChatUserRoles.CREATOR.value)], 1)
    ))


@plugin.on_commands(['роль', 'role'])
@chat_only
async def _(msg, ctx):
    for role in CHAT_USER_ROLES:
        if role.value == ctx.chat_user.role:
            role_name = CHAT_USER_ROLES[role][0]
            await ctx.reply(f'У пользователя установлена роль "{role_name}"')
            break
