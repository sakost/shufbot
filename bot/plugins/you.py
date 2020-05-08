from bot.plugin import CustomPlugin as Plugin


plugin = Plugin('You', 'ты')


@plugin.on_commands(['ты', 'you'])
async def _(ctx,  msg):
    await ctx.reply('Сам такой')
