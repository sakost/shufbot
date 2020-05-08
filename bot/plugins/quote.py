from kutana import Plugin

from bot.utils import get_avatars_and_names, extract_messages
from PIL import Image, ImageColor
plugin = Plugin('Цитата', 'Создает цитату из сообщений')

BG_COLOR = "#191919"
CR_COLOR = "#494949"
FG_COLOR = "#ffffff"


def make_citate(users, messages):
    message = ""
    last_id = 0
    bg_rgb = ImageColor.getrgb(BG_COLOR)
    cr_rgb = ImageColor.getrgb(CR_COLOR)
    fg_rgb = ImageColor.getrgb(FG_COLOR)

    img = Image.new("RGB", (1000, 1000), bg_rgb)
    for i in messages:
        id = i["from_id"]
        msg = i["text"]
        if id != last_id:
            message += users[id]["name"] + ":\n"
        if msg:
            message += "> " + msg + "\n"
            last_id = i["from_id"]
    img.save("quote.png", "PNG")
    return message


@plugin.on_commands(['цит', 'quote'])
async def _(msg, ctx):
    messages = await extract_messages(msg, ctx)
    if not messages:
        await ctx.reply('Вы не указали сообщения для цитаты')
    user_ids = [i["from_id"] for i in messages]
    users = await get_avatars_and_names(ctx, user_ids)
    last_id = 0
    message = ""
    for i in messages:
        id = i["from_id"]
        msg = i["text"]
        if id != last_id:
            message += users[id]["name"] + ":\n"
        message += "> " + msg + "\n"
        last_id = i["from_id"]
    await ctx.reply(message)
