import time

from kutana import HandlerResponse

from bot.roles import needed_admin_rights, ChatUserRoles
from bot.plugin import CustomPlugin
from bot.db import User, ChatUser
from bot.plugins.kick import kick_users
from bot.plugins.reg_date import get_registration_date, format_registration_date

plugin = CustomPlugin('Hello message')


@plugin.on_message_action('chat_invite_user')
@plugin.on_message_action('chat_invite_user_by_link')
@needed_admin_rights
async def _(msg, ctx):
    if not hasattr(ctx, 'chat'):
        return HandlerResponse.SKIPPED
    if ctx.action_type == 'chat_invite_user':
        if ctx.action['member_id'] == -int(ctx.backend.group_id):
            ctx.send_message(ctx.config['owner_id'], 'aloha')
            return
        user_added, _ = await ctx.mgr.get_or_create(User, id=ctx.action['member_id'])
    else:
        user_added, _ = await ctx.mgr.get_or_create(User, id=msg.sender_id)
    chat_user_added, _ = await ctx.mgr.get_or_create(ChatUser, user=user_added, chat=ctx.chat)
    user_time, user_date = format_registration_date(await get_registration_date(user_added.id))
    hello_message = "Привет! Я Шаф(еш), и я бот-администратор бесед.\n" \
                    "Помощь по боту - https://vk.com/@shufbot-help\n" \
                    f"Твоя дата регистрации: {user_date}"
    if not chat_user_added.banned:
        await ctx.reply(hello_message)
        return
    if (chat_user_added.banned_until == -1 or chat_user_added.banned_until > time.time()) \
            and ctx.chat_user.role < ChatUserRoles.ADMIN:
        return await kick_users(ctx, [(user_added, chat_user_added)], msg.receiver_id - 2 * 10 ** 9)
    else:
        chat_user_added.banned = False
        chat_user_added.banned_until = 0
        await ctx.mgr.update(chat_user_added)
        await ctx.reply(hello_message)
        await ctx.reply(f'[id{user_added.id}|Пользователь] разбанен', disable_mentions=1)
        return
