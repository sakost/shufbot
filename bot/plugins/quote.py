from kutana import Plugin, Attachment

from bot.utils import get_avatars_and_names, extract_messages
from PIL import Image, ImageColor, ImageDraw, ImageFont
from random import randint
import re
import os

plugin = Plugin('Цитата', 'Создает цитату из сообщений')

BG_COLOR = "#191919"
CR_COLOR = "#494949"
FG_COLOR = "#ffffff"
WIDTH = 1000
FONT_SIZE = 45
NAME_FONT_SIZE = 80
INDENT = 80
COPYRIGHT = "Цитата сделана vk.com/shufbot"
LINE_INDENT = 15

name_font = ImageFont.truetype("assets/Roboto-Bold.ttf",
                               size=NAME_FONT_SIZE,
                               encoding="unic")
text_font = ImageFont.truetype("assets/Roboto-Regular.ttf", size=FONT_SIZE,
                               encoding="unic")
EMOJI_PATTERN = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)


def wrap(x, text, borderx, font):
    lines = []
    line = []
    expanded = False
    words = text.split(" ")
    if len(words) > 80:
        expanded = True
        borderx += 260
    for word in words:
        line_words = line + [word]
        new_line = ' '.join(line_words)
        size = font.getsize(new_line)
        if x + size[0] <= borderx:
            line.append(word)
        else:
            if len(line_words) == 1:
                tword = ""
                n = 0
                size = (0, 0)
                while x + size[0] <= borderx:
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
    return '\n'.join(lines), expanded


def make_mono_quote(users, messages):
    width = WIDTH
    line_indent = LINE_INDENT
    x = INDENT
    y = 96
    id = messages[0]["from_id"]
    msg = list()
    for i in messages:
        if i["from_id"] == id:
            t = EMOJI_PATTERN.sub('', i["text"])
            if t:
                msg.append(t)
    if not msg:
        return False
    msg = "\n".join(msg)
    msg, expanded = wrap(x, msg, WIDTH - INDENT, text_font)
    quote = Image.open("assets/quotes.jpg").convert("RGB")
    name, _ = wrap(x, users[id]["name"], WIDTH - quote.width - 80, name_font)

    if expanded:
        width += 260
        line_indent = 20
    bg_rgb = ImageColor.getrgb(BG_COLOR)
    cr_rgb = ImageColor.getrgb(CR_COLOR)
    fg_rgb = ImageColor.getrgb(FG_COLOR)

    img = Image.new("RGB", (width, 1000), bg_rgb)
    draw = ImageDraw.Draw(img)

    name_size = draw.multiline_textsize(name, name_font)
    line_name_size = draw.multiline_textsize(
        name.splitlines()[0], name_font)
    text_size = draw.multiline_textsize(msg, text_font, spacing=line_indent)
    copyright_size = draw.multiline_textsize(COPYRIGHT, text_font)
    height = y + name_size[1] + text_size[1]\
        + copyright_size[1] + INDENT + 42 + 34 + 2

    img = Image.new("RGB", (width, height), bg_rgb)
    img.paste(quote, (img.width - quote.width - 80, 0))
    draw = ImageDraw.Draw(img)

    draw.multiline_text(
        (x, quote.height - line_name_size[1]),
        name, font=name_font, fill=fg_rgb)
    y += name_size[1] + 42
    x += 2
    draw.multiline_text(
        (x, y), msg, font=text_font, fill=fg_rgb, spacing=line_indent)
    y += text_size[1] + 34
    draw.multiline_text((x, y), COPYRIGHT, font=text_font, fill=cr_rgb)
    filename = f"quotes/monoQuote{randint(0, 9999999)}.png"
    if not os.path.exists("quotes"):
        os.mkdir("quotes")
    img.save(filename, "PNG")
    return filename


@plugin.on_commands(['цит', 'quote'])
async def _(msg, ctx):
    messages = await extract_messages(msg, ctx)
    if not messages:
        await ctx.reply('Вы не указали сообщения для цитаты')
    else:
        user_ids = [i["from_id"] for i in messages]
        users = await get_avatars_and_names(ctx, user_ids)
        filename = make_mono_quote(users, messages)
        if not filename:
            await ctx.reply("Текста не найдено")
            return
        attach = Attachment.new(open(filename, "rb"))
        attachment = await ctx.backend.upload_attachment(
            attach, peer_id=msg.receiver_id)
        os.remove(filename)
        message = ""
        await ctx.reply(message, attachments=attachment)
