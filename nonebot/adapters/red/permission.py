from nonebot.permission import Permission

from .event import MessageEvent


async def _private(event: MessageEvent) -> bool:
    return event.is_private


async def _private_friend(event: MessageEvent) -> bool:
    return event.is_private and event.roleType == 0


async def _private_group(event: MessageEvent) -> bool:
    return event.is_private and event.roleType == 1


PRIVATE = Permission(_private)
""" 匹配任意私聊消息类型事件"""
PRIVATE_FRIEND: Permission = Permission(_private_friend)
"""匹配任意好友私聊消息类型事件"""
PRIVATE_GROUP: Permission = Permission(_private_group)
"""匹配任意群临时私聊消息类型事件"""


async def _group(event: MessageEvent) -> bool:
    return event.is_group


async def _group_member(event: MessageEvent) -> bool:
    return event.is_group and event.roleType == 2


async def _group_admin(event: MessageEvent) -> bool:
    return event.is_group and event.roleType == 3


async def _group_owner(event: MessageEvent) -> bool:
    return event.is_group and event.roleType == 4


GROUP: Permission = Permission(_group)
"""匹配任意群聊消息类型事件"""
GROUP_MEMBER: Permission = Permission(_group_member)
"""匹配任意群员群聊消息类型事件"""
GROUP_ADMIN: Permission = Permission(_group_admin)
"""匹配任意群管理员群聊消息类型事件"""
GROUP_OWNER: Permission = Permission(_group_owner)
"""匹配任意群主群聊消息类型事件"""

__all__ = [
    "PRIVATE",
    "PRIVATE_FRIEND",
    "PRIVATE_GROUP",
    "GROUP",
    "GROUP_MEMBER",
    "GROUP_ADMIN",
    "GROUP_OWNER",
]
