import time

from kutana import HandlerResponse

from bot.plugin import CustomPlugin as Plugin
from bot.db import User, ChatUser, Chat
from bot.roles import chat_only
from bot.utils import extract_users, get_users
from bot.plugins.manage_chat_roles import CHAT_USER_ROLES
from datetime import datetime

plugin = Plugin('Stat counter')

@plugin.on_any_message(priority=11)
@chat_only
async def _(msg, ctx):
    mgr = ctx.mgr
    if ctx.user.id < 0:
        return HandlerResponse.SKIPPED
    chat = ctx.chat
    user = ctx.user #, _ = await ctx.mgr.get_or_create(User, id=ctx.user.id)
    chat_user = ctx.chat_user # , _ = await ctx.mgr.get_or_create(ChatUser, user_id=ctx.user.id)
    np = chat.last_user_id != user.id
    message_len = len(msg.text)

    if np:
        user.messages_np += 1
        user.symbols_np += message_len
        chat_user.messages_np += 1
        chat_user.symbols_np += message_len
    
    user.messages += 1
    user.symbols += message_len
    chat_user.messages += 1
    chat_user.symbols += message_len
    chat_user.last_message = datetime.now()
    if len(msg.attachments) > 0:
        type = msg.attachments[0].type
        if type == "voice":
            chat_user.voice += 1
            user.voice += 1
    chat.last_user = user

    await mgr.update(chat)
    await mgr.update(user)
    await mgr.update(chat_user)
    return HandlerResponse.SKIPPED


@plugin.on_commands(['статчат', 'statchat'])
@chat_only
async def _(msg, ctx):
    mgr = ctx.mgr
    users = await mgr.execute(
        ChatUser.select().where(
            (ChatUser.user_id > 0) & (ChatUser.chat_id == ctx.chat.id)
            ).order_by(
                -ChatUser.messages_np
                ).limit(10))
    message = ""
    template = "{}. [id{}|{} {}] - {} ({})\n"
    users_data = await get_users(ctx, [i.user_id for i in users])
    for i in range(len(users)):
        user = users[i]
        message += template.format(
            i + 1,
            user.user_id,
            users_data[i].get('first_name'),
            users_data[i].get('last_name'),
            user.messages,
            user.messages_np)
    await ctx.reply(message, disable_mentions=True)


@plugin.on_commands(['стат', 'stat'])
@chat_only
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    if not users:
        id = ctx.user.id
    else:
        id = users[0]
    user, _ = await ctx.mgr.get_or_create(ChatUser, user_id=id, chat_id=ctx.chat.id)
    for role in CHAT_USER_ROLES:
        if role.value == ctx.chat_user.role:
            role_name = CHAT_USER_ROLES[role][0]
            break
    first_appeared = user.first_appeared.strftime("%d.%m.%Y")
    last_message = user.last_message.strftime("%d.%m.%Y в %H:%M")
    await ctx.reply(
        f"Статистика @id{id}:\n"
        f"👑 Роль: {role_name}\n"
        f"✉ Сообщений: {user.messages} ({user.messages_np})\n"
        f"🔣 Символов: {user.symbols} ({user.symbols_np})\n" +
        (f"🔈 Голосовых: {user.voice}\n" if user.voice else "") +
        f"🏆 Активность: русское место\n" +
        (f"💬 КПС: " + (f"{user.symbols_np / user.messages_np}\n"\
            if user.messages_np else "0.0\n"))
        + f"⌛ В чате с {first_appeared}\n"
        f"⏳ Последнее сообщение: {last_message}\n"
        f"⚠ Предупреждений: {user.warns} из {ctx.chat.max_warns}\n"
    )


@plugin.on_commands(['глстат', 'glstat', "global"])
@chat_only
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    if not users:
        id = ctx.user.id
    else:
        id = users[0]
    user, _ = await ctx.mgr.get_or_create(ChatUser, user_id=id)
    await ctx.reply(
        f"Глобальная статистика @id{id}:\n"
        f"✉ Сообщений: {user.messages} ({user.messages_np})\n"
        f"🔣 Символов: {user.symbols} ({user.symbols_np})\n"
        f"🔈 Голосовых: {user.voice}\n" +
        (f"💬 КПС: " + (f"{user.symbols_np / user.messages_np}\n"\
            if user.messages_np else "0.0\n"))
    )
