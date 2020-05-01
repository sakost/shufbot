from bot.plugin import CustomPlugin as Plugin

plugin = Plugin('Упоминания', 'Тогл упоминаний')

COMMANDS = {
    'on': 1,
    'off': 0,
    'вкл': 1,
    'выкл': 0,
}


@plugin.on_commands(['упоминания', 'mentions', "упом", "setmention"])
async def _(msg, ctx):
    if ctx.body:
        msg = ctx.body.lower()
        for cmd in COMMANDS:
            if msg.startswith(cmd):
                action = COMMANDS[cmd]
                ctx.user.mention = bool(action)
                await ctx.mgr.update(ctx.user)
                break
    await ctx.reply(f'Упоминания {"включены" if ctx.user.mention else "выключены"}')
