import asyncio
from collections import defaultdict

from bot.roles import chat_only, admin_role, needed_admin_rights
from bot.plugin import CustomPlugin as Plugin
from bot.plugins.kick import kick_users
from bot.utils import extract_users
from bot.db import Chat, User, ChatUser

plugin = Plugin('votekick', 'голосует за кик пользователя')

naive_cache = defaultdict(lambda: defaultdict(int))


@plugin.on_commands(['votekick', 'вотекик'])
@chat_only
@needed_admin_rights
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    if not users:
        await ctx.reply('Вы не указали пользователя, за которого нужно проголосовать/начать голосование для кика')
        return
    user_to_kick = await ctx.mgr.get_or_create(User, id=users[0])
    chat_user_to_kick = await ctx.mgr.get_or_create(ChatUser, user=user_to_kick, chat=ctx.chat)

    naive_cache[ctx.chat.id][user_to_kick.id] += 1
    if (count := naive_cache[ctx.chat.id][user_to_kick.id]) >= \
            (await ctx.mgr.execute(Chat.select().where(Chat.id == msg.receiver_id)))[0].max_votes:
        await ctx.reply(f'За кик [id{user_to_kick.id}|пользователя] проголосовало {count} человек\n'
                        'Пользователь подлежит кику за плохое поведение\n'
                        'Скажешь что-нибудь напоследок?')
        await kick_users(ctx, (user_to_kick, chat_user_to_kick), msg.receiver_id - 2 * 10 ** 9)
    elif naive_cache[ctx.chat.id][user_to_kick.id] == 1:
        await ctx.reply(f'Начато голосование за кик [id{user_to_kick.id}|пользователя]\n'
                        f'[id{ctx.user.id}|Другой пользователь] проголосовал за.\n'
                        '1 голос за кик\n'
                        f'Голосвание продлится примерно {ctx.config["votekick_time"]//60} мин.')
        await ctx.app.scheduler.spawn(
            clear_votes(
                ctx.backend,
                ctx.chat.id,
                user_to_kick.id,
                ctx.config['votekick_time']
            )
        )
    else:
        await ctx.reply(f'[id{ctx.user.id}|Пользователь] проголосовал за кик '
                        f'[id{user_to_kick.id}|другого пользователя].\n'
                        f'{count} голосов за кик')


async def clear_votes(backend, chat_id, user_id, sleep_time):
    await asyncio.sleep(sleep_time)
    del naive_cache[chat_id][user_id]
    await backend.send_message(chat_id, f"Голосоваиние за [id{user_id}|пользователя] прекращено")


@plugin.on_commands(['setvotekick', 'сетвк'])
@chat_only
@needed_admin_rights
@admin_role
async def _(msg, ctx):
    if not ctx.body:
        await ctx.reply('Укажите число голосов')
        return
    text: str = ctx.body
    arg, *_ = text.split(maxsplit=1)
    if not arg.isdigit():
        await ctx.reply('Укажите число голосов')
        return
    count = int(arg)
    ctx.chat.max_votes = count
    await ctx.mgr.update(ctx.chat)
    await ctx.reply('Количество голосов успешно обновлено')
