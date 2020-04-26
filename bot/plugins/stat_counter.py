import time

from kutana import HandlerResponse

from kutana import Plugin
from bot.db import User, ChatUser, Chat
from bot.roles import chat_only
from bot.utils import extract_users
from bot.plugins.manage_chat_roles import CHAT_USER_ROLES
from datetime import datetime

plugin = Plugin('Stat counter')

@chat_only
@plugin.on_any_message(priority=11)
async def _(msg, ctx):
    mgr = ctx.mgr
    chat = ctx.chat
    user = ctx.user
    chat_user = ctx.chat_user
    np = not chat_user.id == chat.last_user.id
    
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
        if type == "audio_message":
            chat_user.voice += 1
            user.voice += 1

    chat.last_user = chat_user

    await mgr.update(chat)
    await mgr.update(user)
    await mgr.update(chat_user)


@chat_only
@plugin.on_commands(['стат', 'stat'])
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    for i in users:
        user, _ = await ctx.mgr.get_or_create(ChatUser, id=i)
        stat = get_stat(i, ctx.mgr, ctx.chat.id)
        for role in CHAT_USER_ROLES:
            if role.value == ctx.chat_user.role:
                role_name = CHAT_USER_ROLES[role][0]
                break
        first_appeared = user.first_appeared.strptime("%D.%m.%Y")
        last_message = user.last_message.strptime("%D.%M.%Y в %H:%M")
        await ctx.reply(
            f"Статистика @id{i}:\n"
            f"👑 Роль: {role_name}\n"
            f"✉ Сообщений: {user.messages} ({user.messages_np})\n"
            f"🔣 Символов: {user.symbols} ({user.symbols_np})\n"
            f"💬 КПС: {user.messages_np / user.symbols_np}\n"
            f"🔈 Голосовых: {user.voice}\n"
            f"🏆 Активность: русское место\n"
            f"⌛ В чате с {first_appeared}\n"
            f"⏳ Последнее сообщение: {last_message}\n"
            f"⚠ Предупреждений: {user.warns} из {ctx.chat.max_warns}\n"
        )
