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
        return CheckModerator.get or (message.from_user.id == config.BOT_OWNER)


class IsBannedFilter(BoundFilter):
    """
    Custom filter "is_banned".
    """
    key = "is_banned"

    def __init__(self, is_banned):
        self.is_banned = is_banned

    async def check(self, message: types.Message):
        return Manager(user_id=message.from_user.id).check_ban


class IsAdminFilter(BoundFilter):
    """
    Filter that checks for admin rights existence
    """
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() == self.is_admin


class MemberCanRestrictFilter(BoundFilter):
    """
    Filter that checks member ability for restricting
    """
    key = 'member_can_restrict'

    def __init__(self, member_can_restrict: bool):
        self.member_can_restrict = member_can_restrict

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)

        # I don't know why, but telegram thinks, if member is chat creator, he cant restrict member
        return (member.is_chat_creator() or member.can_restrict_members) == self.member_can_restrict
