from kutana import Plugin, Attachment

from bot.utils import get_avatars_and_names, extract_messages
from PIL import Image, ImageColor, ImageDraw, ImageFont
from random import randint
import re

plugin = Plugin('Цитата', 'Создает цитату из сообщений')

BG_COLOR = "#191919"
CR_COLOR = "#494949"
FG_COLOR = "#ffffff"
WIDTH = 1000
FONT_SIZE = 45
NAME_FONT_SIZE = 80
INDENT = 80
COPYRIGHT = "Цитата сделана vk.com/shufbot"
name_font = ImageFont.truetype("assets/Roboto-Bold.ttf",
                               size=NAME_FONT_SIZE,
                               encoding="unic")
text_font = ImageFont.truetype("assets/Roboto-Regular.ttf", size=FONT_SIZE,
                               encoding="unic")
EMOJI_PATTERN = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)


def wrap(x, text, borderx, font):
    lines = []
    line = []
    words = text.split()
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
    return '\n'.join(lines)


def make_mono_quote(users, message):
    x = INDENT
    y = 96

    id = message["from_id"]
    msg = EMOJI_PATTERN.sub('', message["text"])
    if not msg:
        return False
    msg = wrap(x, msg, WIDTH - INDENT, text_font)
    quote = Image.open("assets/quotes.jpg").convert("RGB")
    name = wrap(x, users[id]["name"], WIDTH - quote.width, name_font)

    bg_rgb = ImageColor.getrgb(BG_COLOR)
    cr_rgb = ImageColor.getrgb(CR_COLOR)
    fg_rgb = ImageColor.getrgb(FG_COLOR)

    img = Image.new("RGB", (WIDTH, 1000), bg_rgb)
    draw = ImageDraw.Draw(img)

    name_size = draw.multiline_textsize(name, name_font)
    line_name_size = draw.multiline_textsize(name.splitlines()[0], name_font)
    text_size = draw.multiline_textsize(msg, text_font)
    copyright_size = draw.multiline_textsize(COPYRIGHT, text_font)
    height = y + name_size[1] + text_size[1]\
        + copyright_size[1] + INDENT + 42+34

    img = Image.new("RGB", (WIDTH, height), bg_rgb)
    img.paste(quote, (img.width - quote.width - 80, 0))
    draw = ImageDraw.Draw(img)

    draw.multiline_text(
        (x, quote.height - line_name_size[1]),
        name, font=name_font, fill=fg_rgb)
    y += name_size[1] + 42
    x += 2
    draw.multiline_text((x, y), msg, font=text_font, fill=fg_rgb)
    y += text_size[1] + 34
    draw.multiline_text((x, y), COPYRIGHT, font=text_font, fill=cr_rgb)
    filename = f"quotes/monoQuote{randint(0, 9999999)}.png"
    img.save(filename, "PNG")
    return filename


@plugin.on_commands(['цит', 'quote'])
async def _(msg, ctx):
    messages = await extract_messages(msg, ctx)
    if not messages:
        await ctx.reply('Вы не указали сообщения для цитаты')
    user_ids = [i["from_id"] for i in messages]
    users = await get_avatars_and_names(ctx, user_ids)
    if len(messages) == 1:
        filename = make_mono_quote(users, messages[0])
        if not filename:
            await ctx.reply("Текста не найдено")
            return
        attach = Attachment.new(open(filename, "rb"))
        attachment = await ctx.backend.upload_attachment(
            attach, peer_id=ctx.chat.id + 2*10**9)
    message = "Сделал цитату."
    await ctx.reply(message, attachments=attachment)
