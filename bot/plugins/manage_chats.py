from kutana import Plugin

from bot.roles import developer_global_role, ChatRoles

plugin = Plugin('Manage chats[develop]', 'Manage chats roles')

CHAT_LEVEL = {
    ChatRoles.NORMAL: ('обычный', 'norm', 'норм'),
    ChatRoles.IMPROVED: ('улучшенный', 'improved'),
    ChatRoles.DEVELOPER: ('разраб', 'dev'),
}


@plugin.on_commands(['set_chat_lvl', 'set_chat_level', 'сетчатлвл', 'сетчатлевел'])
@developer_global_role
async def _(msg, ctx):
    if hasattr(ctx, 'chat'):
        for lvl, lvl_names in CHAT_LEVEL.items():
            for name in lvl_names:
                if ctx.body.startswith(name):
                    ctx.chat.level = lvl.value
                    await ctx.mgr.update(ctx.chat)
                    await ctx.reply(f'Чату установлен уровень {name}')
                    return
        await ctx.reply('Неизвестный уровень чата. Доступные уровни: \n' + '\n'.join(
            f"{num}){', '.join(lvl_names)}" for num, lvl_names in enumerate(CHAT_LEVEL.values(), 1)
        ))
    await ctx.reply('Чат не является беседой')


@plugin.on_commands(['чатлвл', 'chat_lvl', 'чатлевел', 'chat_level'])
async def _(msg, ctx):
    if hasattr(ctx, 'chat'):
        await ctx.reply(f'Установлен уровень чата "{CHAT_LEVEL[ctx.chat.level][0]}"')
    else:
        await ctx.reply('Чат не является беседой')
