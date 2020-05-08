from bot.plugin import CustomPlugin as Plugin


plugin = Plugin('You', 'ты')


@plugin.on_commands(['ты', 'you'])
async def _(msg, ctx):
    await ctx.reply('Сам такой')
