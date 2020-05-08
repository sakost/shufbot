import asyncio
import re

EXTRACT_USERS_MENTIONED = re.compile(r'\[id(\d*?)\|.*?\]', re.DOTALL)
EXTRACT_USERS_URLS = re.compile(
    r'(https?://)?(www\.)?vk\.com/(?P<username>[^\s]+)', re.DOTALL)


async def extract_users_urls(ctx):
    text = ctx.body
    users = []
    for user_match in EXTRACT_USERS_URLS.finditer(text):
        user = await ctx.resolve_screen_name(user_match.group('username'))
        if user.get('type', None) == 'user':
            users.append(user['object_id'])
    return users


async def extract_mentioned_users(ctx):
    text = ctx.body
    users = []
    for user_match in EXTRACT_USERS_MENTIONED.finditer(text):
        users.append(int(user_match.group(1)))
    return users


async def extract_users(msg, ctx):
    users = []
    raw_msg = msg.raw['object']['message']
    reply_msg = raw_msg.get('reply_message', None)
    fwd_messages = raw_msg.get('fwd_messages', [])

    if reply_msg is not None:
        users.append(reply_msg['from_id'])

    for fwd_msg in fwd_messages:
        users.append(fwd_msg['from_id'])
    # let other coroutines to work
    await asyncio.sleep(0)
    users.extend(await extract_mentioned_users(ctx))
    await asyncio.sleep(0)
    users.extend(await extract_users_urls(ctx))
    await asyncio.sleep(0)
    return users


async def get_users(ctx, user_ids, name_case="nom", fields=""):
    if isinstance(user_ids, list):
        user_ids = ','.join(map(str, user_ids))
    users = await ctx.request(
        'users.get',
        user_ids=user_ids,
        name_case=name_case,
        fields=fields)
    return users


async def get_groups(ctx, group_ids, fields=""):
    # if isinstance(group_ids, list):
    #     user_ids = ','.join(map(str, group_ids))
    users = await ctx.request(
        'groups.getById',
        group_ids=group_ids,
        fields=fields)
    return users


async def get_mentioned_text(user, text):
    if user.mention:
        if user.id > 0:
            return f"[id{user.id}|{text}]"
        else:
            return f"[public{user.id}|{text}]"
    else:
        return text


async def get_names(ctx, users, name_case='', chat=False, db=False):
    group_ids = list()
    user_ids = list()
    for i in users:
        if db:
            id = (i.user_id if chat else i.id)
        else:
            id = i
        if id > 0:
            user_ids.append(id)
        else:
            group_ids.append(id)
    users_vk = await get_users(ctx, user_ids, name_case)
    groups = await get_groups(ctx, group_ids)
    names = [f"{i['first_name']} {i['last_name']}" for i in users_vk]
    names += [f"{i['name']}" for i in groups]
    return ", ".join(names)


async def get_avatars_and_names(ctx, users, chat=False, db=False):
    group_ids = list()
    user_ids = list()
    for i in users:
        if db:
            id = (i.user_id if chat else i.id)
        else:
            id = i
        if id > 0:
            user_ids.append(str(id))
        else:
            group_ids.append(str(abs(id)))
    users_vk = await get_users(
        ctx, ','.join(user_ids), "", "photo_100,photo_200,photo_50")
    groups = await get_groups(
        ctx, ','.join(group_ids), "photo_100,photo_200,photo_50")
    users = {
        i["id"]: {"name": f"{i['first_name']} {i['last_name']}",
                  "avatar": {
                      "photo_50": i["photo_50"],
                      "photo_100": i["photo_100"],
                      "photo_200": i["photo_200"]}} for i in users_vk}
    groups = {
        -i["id"]: {"name": f"{i['name']}",
                   "avatar": {
                       "photo_50": i["photo_50"],
                       "photo_100": i["photo_100"],
                       "photo_200": i["photo_200"]}} for i in groups}
    users.update(groups)
    return users


async def extract_messages(msg, ctx):
    messages = []
    raw_msg = msg.raw['object']['message']
    reply_msg = raw_msg.get('reply_message', None)
    fwd_messages = raw_msg.get('fwd_messages', [])

    if reply_msg is not None:
        messages.append({
            "from_id": reply_msg['from_id'],
            "text": reply_msg["text"]})

    for fwd_msg in fwd_messages:
        messages.append({
            "from_id": fwd_msg['from_id'],
            "text": fwd_msg["text"]})

    return messages


COMMANDS = {
    'on': 1,
    'off': 0,
    'вкл': 1,
    'выкл': 0,
}


def on_or_off(text):
    for cmd in COMMANDS:
        if text.startswith(cmd):
            return COMMANDS[cmd]
