from bot.plugin import CustomPlugin as Plugin
plugin = Plugin('Unknown command')


@plugin.on_any_unprocessed_message()
async def _(msg, ctx):
    if ctx.with_prefix:
        await ctx.reply('Неизвестная команда')
