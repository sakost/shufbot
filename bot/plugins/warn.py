from bot.plugin import CustomPlugin as Plugin
from bot.db import ChatUser, User
from bot.roles import admin_role, needed_admin_rights, chat_only
from bot.utils import extract_users, get_names
from bot.plugins.kick import kick_users
plugin = Plugin('Варн', 'выдает предупреждение в беседе')


async def warn(ctx, user_ids, chat_id, role=-1):
    # -1 означает определять роль автоматически
    max_warns = ctx.chat.max_warns
    users_kicked = list()
    users_warned = list()
    if not isinstance(user_ids, list):
        user_ids = [user_ids]
    for i in user_ids:
        user, _ = await ctx.mgr.get_or_create(ChatUser, user_id=i, chat_id=chat_id)
        if user.role >= role or (user.role >= ctx.chat_user.role and role == -1):
            continue
        user.warns += 1
        if user.warns > max_warns:
            users_kicked.append(user)
            user.warns = 0
        else:
            users_warned.append(user)
        await ctx.mgr.update(user)
    await kick_users(ctx, [i.user_id for i in users_kicked], chat_id, ban=False)
    return users_kicked, users_warned


@plugin.on_commands(['варн', 'warn'])
@chat_only()
@admin_role
@needed_admin_rights
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    chat_id = ctx.chat.id
    if users:
        users_kicked, users_warned = await warn(ctx, users, chat_id)
        names_kicked = []
        names_warned = []
        if users_kicked:
            names_kicked = await get_names(ctx, users_kicked, "", True)
            await ctx.reply(f"{names_kicked} были кикнуты за превышение лимита в {ctx.chat.max_warns} варн(-а).")
        if users_warned:
            names_warned = await get_names(ctx, users_warned, "", True)
            await ctx.reply(f"{names_warned} был выдан варн.")
        if not names_kicked and not names_warned:
            await ctx.reply("Никому не был выдан варн.")
    else:
        await ctx.reply('Вы не указали ни одного пользователя')
