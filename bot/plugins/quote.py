from kutana import Plugin, Attachment

from bot.utils import get_avatars_and_names, extract_messages, download_images
from PIL import Image, ImageColor, ImageDraw, ImageFont
from io import BytesIO

import re
import asyncio

plugin = Plugin('Цитата', 'Создает цитату из сообщений')

COPYRIGHT = "Цитата сделана vk.com/shufbot"

EMOJI_PATTERN = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)


def wrap(x, text, border, font, width=1000, max_width=1000, auto_expand=False):
    lines = []
    line = []
    words = text.split(" ")
    if len(words) > 80 and not auto_expand:
        width += 260
    for word in words:
        line_words = line + [word]
        new_line = ' '.join(line_words)
        size = font.getsize(new_line)
        if x + size[0] <= (width + border):
            line.append(word)
        else:
            if size[0] > width and auto_expand:
                if size[0] < max_width:
                    width = size[0]
                else:
                    width = 1000
            if len(line_words) == 1:
                tword = ""
                n = 0
                size = (0, 0)
                while x + size[0] <= width + border:
                    tword += word[n]
                    size = font.getsize(tword)
                    n += 1
                length = len(word)
                n = len(tword) - 1
                tlines = [[word[i:i+n]] for i in range(
                    0, length, n)]
                lines += tlines[:-1]
                word = tlines[-1][0]
                line = []
            lines.append(line)
            line = [word]
    if line:
        lines.append(line)
    lines = [' '.join(line) for line in lines if line]
    return '\n'.join(lines), width


async def get_actions(users, messages, x, width, name_font,
                      text_font, text_border=-40,
                      name_border=-40, fixed_id=None,
                      extend=False, max_width=1000):
    actions = list()
    if fixed_id:
        id = fixed_id
    else:
        id = 0
    avatars = set()
    wrapped_names = dict()
    t_msg = list()
    expanded = False
    if fixed_id:
        name, _expanded = wrap(
            x, users[id]["name"], name_border, name_font, width)
        wrapped_names.setdefault(id, name)
        actions.append({"avatar": users[id]["avatar"],
                        "name": name,
                        "type": "title"})
        avatars.add(users[id]["avatar"]["photo_100"])

    for msg in messages:
        clean_msg = EMOJI_PATTERN.sub('', msg["text"])
        if clean_msg:
            if msg["from_id"] != id and not fixed_id:
                wrapped_msg, _expanded = wrap(x, "\n".join(t_msg),
                                              text_border, text_font,
                                              width, max_width,
                                              extend)
                if _expanded:
                    expanded = _expanded
                if id != 0:
                    actions.append({"type": "message",
                                    "message": "\n".join(wrap)})
                id = msg["from_id"]
                t_msg = list()
                if wrapped_names.get(id):
                    name = wrapped_names[id]
                else:
                    name, _expanded = wrap(
                        x, users[id]["name"], name_border, name_font, width)
                    wrapped_names.setdefault(id, name)
                actions.append({"avatar": users[id]["avatar"],
                                "name": name,
                                "type": "title"})
                avatars.add(users[id]["avatar"]["photo_100"])

            t_msg.append(msg["text"])

    wrapped_msg, _expanded = wrap(x, "\n".join(t_msg),
                                  text_border, text_font,
                                  width, max_width, extend)
    if _expanded:
        expanded = _expanded
    actions.append({"type": "message",
                    "message": wrapped_msg})
    if not actions:
        return False
    return actions, expanded, avatars


def get_mono_quote(xy, actions, quote, draw,
                   fg_rgb, cr_rgb, name_font, text_font,
                   line_indent, real_draw=True):
    x, y = xy
    for i in actions:
        if i["type"] == "title":
            name = i["name"]
            line = name.splitlines()[0]
            size = draw.multiline_textsize(line, name_font)
            if real_draw:
                draw.multiline_text((x, quote.height - size[1]), name,
                                    fg_rgb, name_font)
            x += 2
            size = draw.multiline_textsize(name, name_font)
            y += size[1] + 42
        elif i["type"] == "message":
            size = draw.multiline_textsize(i["message"],
                                           text_font, spacing=line_indent)
            if real_draw:
                draw.multiline_text(
                    (x, y), i["message"], font=text_font,
                    fill=fg_rgb, spacing=line_indent)
            y += size[1] + 34
    size = draw.multiline_textsize(COPYRIGHT, text_font)
    draw.multiline_text((x, y), COPYRIGHT, cr_rgb, text_font)
    y += 80 + size[1]
    return y


async def make_mono_quote(users, messages):
    name_font = ImageFont.truetype("assets/Roboto-Bold.ttf",
                                   size=80,
                                   encoding="unic")
    text_font = ImageFont.truetype("assets/Roboto-Regular.ttf", size=45,
                                   encoding="unic")

    bg_rgb = ImageColor.getrgb("#191919")
    cr_rgb = ImageColor.getrgb("#494949")
    fg_rgb = ImageColor.getrgb("#ffffff")

    width = 1000
    line_indent = 15
    x = 80
    y = 96
    id = messages[0]["from_id"]

    quote = Image.open("assets/quotes.jpg").convert("RGB")
    actions, expanded, _ = await get_actions(
        users, messages, x, width, name_font, text_font,
        -80, -(quote.width + 80), id)
    if not actions:
        return False

    if expanded != width:
        width = expanded
        line_indent = 20
    draw = ImageDraw.ImageDraw(Image.new("RGB", (1000, 1000)))
    height = get_mono_quote((x, y), actions, quote, draw,
                            fg_rgb, cr_rgb, name_font, text_font, line_indent,
                            False)

    img = Image.new("RGB", (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)
    img.paste(quote, (img.width - quote.width - 80, 0))
    draw = ImageDraw.Draw(img)
    get_mono_quote((x, y), actions, quote, draw,
                   fg_rgb, cr_rgb, name_font, text_font, line_indent,
                   True)
    file = BytesIO()
    img.save(file, "PNG")
    file.seek(0)
    return file


async def make_alternate_quote(users, messages):
    name_font = ImageFont.truetype("assets/Roboto-Bold.ttf",
                                   size=34,
                                   encoding="unic")
    text_font = ImageFont.truetype("assets/Roboto-Regular.ttf", size=36,
                                   encoding="unic")

    width = 600
    line_indent = 12
    x = 40 + 100 + 26
    y = 40

    actions = list()
    id = 0
    expanded = False
    avatars = set()
    wrapped_names = dict()
    t_msg = list()
    for msg in messages:
        t = EMOJI_PATTERN.sub('', msg["text"])
        if t:
            if msg["from_id"] != id:
                if id != 0:
                    actions.append({"type": "message",
                                    "message": "\n".join(t_msg)})
                t_msg = list()
                id = msg["from_id"]
                if wrapped_names.get(id):
                    name = wrapped_names[id]
                else:
                    name, _ = wrap(
                        x, users[id]["name"], -40, name_font)
                    wrapped_names.setdefault(id, name)
                actions.append({"avatar": users[id]["avatar"],
                                "name": name,
                                "type": "title"})
                avatars.add(users[id]["avatar"]["photo_100"])
            t, _expanded = wrap(x, msg["text"], -40, text_font)
            if _expanded:
                expanded = _expanded
            t_msg.append(t)

    actions.append({"type": "message",
                    "message": "\n".join(t_msg)})
    if not actions:
        return False

    avatars = await download_images(avatars)
    if expanded:
        width = expanded

    bg_rgb = ImageColor.getrgb("#ffffff")
    fg_rgb = ImageColor.getrgb("#000000")
    n_rgb = ImageColor.getrgb("#466383")

    img = Image.new("RGBA", (width, 1000), bg_rgb)
    draw = ImageDraw.Draw(img)
    x = 40
    start = True
    for i in actions:
        if i.get("type") == "title":
            x = 40
            if not start:
                y += 20
            else:
                start = False
            ava = Image.open(BytesIO(avatars[i["avatar"]["photo_100"]]))
            mask = Image.open(open("assets/mask.png", "rb")).convert("RGBA")
            img.paste(ava, (x, y))
            img.alpha_composite(mask, (x, y))
            x += ava.width + 25
            y += 7
            size = draw.multiline_textsize(i["name"], name_font)
            draw.multiline_text((x, y), i["name"], font=name_font, fill=n_rgb)
            y += size[1] + 12
        elif i.get("type") == "message":
            x = 40 + 100 + 25
            size = draw.multiline_textsize(i["message"], font=text_font,
                                           spacing=line_indent)
            draw.multiline_text((x, y), i["message"],
                                font=text_font, fill=fg_rgb,
                                spacing=line_indent)
            y += size[1]
    file = BytesIO()
    img.save(file, "PNG")
    file.seek(0)
    return file


@plugin.on_commands(['цит', 'quote'])
async def _(msg, ctx):
    messages = await extract_messages(msg, ctx)
    if not messages:
        await ctx.reply('Вы не указали сообщения для цитаты')
    else:
        user_ids = [i["from_id"] for i in messages]
        users = await get_avatars_and_names(ctx, user_ids)
        await asyncio.sleep(0)  # заставляем роботать другие процессы
        file = await make_mono_quote(users, messages)
        if not file:
            await ctx.reply("Текста не найдено")
            return
        attach = Attachment.new(file)
        attachment = await ctx.backend.upload_attachment(
            attach, peer_id=msg.receiver_id)
        message = ""
        await ctx.reply(message, attachments=attachment)


@plugin.on_commands(['альтцит', 'altquote'])
async def _(msg, ctx):
    messages = await extract_messages(msg, ctx)
    if not messages:
        await ctx.reply('Вы не указали сообщения для цитаты')
    else:
        user_ids = [i["from_id"] for i in messages]
        await asyncio.sleep(0)  # заставляем роботать другие процессы
        users = await get_avatars_and_names(ctx, user_ids)
        file = await make_alternate_quote(users, messages)
        if not file:
            await ctx.reply("Текста не найдено")
            return
        attach = Attachment.new(file)
        attachment = await ctx.backend.upload_attachment(
            attach, peer_id=msg.receiver_id)
        message = ""
        await ctx.reply(message, attachments=attachment)
