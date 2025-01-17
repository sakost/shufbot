import datetime

import peewee
from peewee_async import MySQLDatabase
import peeweedbevolve

database = MySQLDatabase(None)


class User(peewee.Model):
    id = peewee.IntegerField(unique=True, null=False)
    role = peewee.IntegerField(default=0)
    messages = peewee.IntegerField(default=0)
    messages_np = peewee.IntegerField(default=0)
    symbols = peewee.IntegerField(default=0)
    symbols_np = peewee.IntegerField(default=0)
    voice = peewee.IntegerField(default=0)
    first_used = peewee.DateTimeField(default=datetime.datetime.now)
    mention = peewee.BooleanField(default=True)

    class Meta:
        database = database


class Chat(peewee.Model):
    admin = peewee.BooleanField(default=False)
    kick_left = peewee.BooleanField(default=False)
    kick_groups = peewee.BooleanField(default=False)
    kick_link = peewee.BooleanField(default=True)
    max_warns = peewee.IntegerField(default=3)
    max_votes = peewee.IntegerField(default=5)
    level = peewee.IntegerField(default=0)
    mention_all = peewee.BooleanField(default=False)
    mention = peewee.BooleanField(default=False)
    last_user = peewee.ForeignKeyField(User, null=True)
    voice = peewee.IntegerField(default=0)
    messages = peewee.IntegerField(default=0)
    messages_np = peewee.IntegerField(default=0)
    symbols = peewee.IntegerField(default=0)
    symbols_np = peewee.IntegerField(default=0)
    enabled_mailing = peewee.BooleanField(default=True)

    class Meta:
        database = database


class ChatUser(peewee.Model):
    id = peewee.PrimaryKeyField()
    user = peewee.ForeignKeyField(User, backref='chats', null=False, index=True)
    role = peewee.IntegerField(default=0)
    chat = peewee.ForeignKeyField(Chat, backref="users", null=False, index=True)
    banned = peewee.BooleanField(default=False)
    muted = peewee.BooleanField(default=False)
    muted_until = peewee.IntegerField(default=0)
    banned_until = peewee.IntegerField(default=0)
    warns = peewee.IntegerField(default=0)
    messages = peewee.IntegerField(default=0)
    messages_np = peewee.IntegerField(default=0)
    symbols = peewee.IntegerField(default=0)
    symbols_np = peewee.IntegerField(default=0)
    voice = peewee.IntegerField(default=0)
    first_appeared = peewee.DateTimeField(default=datetime.datetime.now)
    last_message = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = database


models = [User, Chat, ChatUser]
