from peewee_async import Manager

from bot.plugin import CustomPlugin as Plugin
from bot.db import User
from bot.roles import owner_global_role, UserRoles
from bot.utils import extract_users

plugin = Plugin('Add developers[develop]')


async def make_dev(mgr: Manager, users):
    added = []
    async with mgr.atomic():
        for user_id in users:
            user, created = await mgr.get_or_create(User, id=user_id)
            if user.role < UserRoles.DEVELOPER.value:
                user.role = UserRoles.DEVELOPER.value
                await mgr.update(user)
                added.append(user_id)
    return added


async def del_dev(mgr: Manager, users):
    deleted = []
    for user_id in users:
        user, created = await mgr.get_or_create(User, id=user_id)
        if user.role > UserRoles.USER.value:
            user.role = UserRoles.USER.value
            await mgr.update(user)
            deleted.append(user_id)
    return deleted


@plugin.on_commands(['add_dev'])
@owner_global_role
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    users = await make_dev(ctx.config['db_manager'], users)
    if len(users) != 0:
        await ctx.reply(', '.join(f"https://vk.com/id{u}" for u in users) + ' добавлены в категорию "разработчики"')
    else:
        await ctx.reply('Добавлять некого..')


@plugin.on_commands(['make_user', 'del_dev'])
@owner_global_role
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    users = await del_dev(ctx.config['db_manager'], users)
    if len(users) != 0:
        await ctx.reply(', '.join(f"https://vk.com/id{u}" for u in users) + ' добавлен в категорию "пользователи"')
    else:
        if ctx.command == 'make_user':
            await ctx.reply('Добавлять некого..')
        else:
            await ctx.reply('Удалять некого..')
