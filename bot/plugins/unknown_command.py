from kutana import Plugin

plugin = Plugin('Unknown command')


@plugin.on_any_unprocessed_message()
async def _(msg, ctx):
    print('prosto pidor')
    if ctx.with_prefix:
        await ctx.reply('Неизвестная команда')
