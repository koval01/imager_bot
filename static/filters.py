from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from static import config
from content.manager import Manager
from utils.moderator import CheckModerator


class IsOwnerFilter(BoundFilter):
    """
    Custom filter "is_owner".
    """
    key = "is_owner"

    def __init__(self, is_owner):
        self.is_owner = is_owner
    
    async def check(self, message: types.Message):
        return message.from_user.id == config.BOT_OWNER


class IsModeratorFilter(BoundFilter):
    """
    Custom filter "is_moderator".
    """
    key = "is_moderator"

    def __init__(self, is_moderator):
        self.is_moderator = is_moderator

    async def check(self, message: types.Message):
        return await CheckModerator(message).get or \
               (message.from_user.id == config.BOT_OWNER)


class IsBannedFilter(BoundFilter):
    """
    Custom filter "is_banned".
    """
    key = "is_banned"

    def __init__(self, is_banned):
        self.is_banned = is_banned

    async def check(self, message: types.Message):
        return await Manager(message=message).check_ban


class IsFullBannedFilter(BoundFilter):
    """
    Custom filter "is_full_banned".
    """
    key = "is_full_banned"

    def __init__(self, is_full_banned):
        self.is_full_banned = is_full_banned

    async def check(self, message: types.Message):
        return await Manager(message=message).check_full_ban
