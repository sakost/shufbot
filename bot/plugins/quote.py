from kutana import Plugin

# from bot.utils import get_avatares_and_names, extract_mesasges
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
    messages = await extract_mesasges(msg, ctx)
    if not messages:
        await ctx.reply('Вы не указали сообщения для цитаты')
    user_ids = [i["from_id"] for i in messages]
    users = await get_avatares_and_names(ctx, user_ids)
    import json
    json.dump(
        {"users": users,
         "messages": messages
         }, open("quote.json", "w"), indent=4, sort_keys=True)
    print(make_citate(users, messages))

if __name__ == "__main__":
    import json
    data = json.load(open("quote.json", "r"))
    messages = data.get("messages")
    users = data.get("users")
    print(make_citate(users, messages))
