from typing_extensions import override
from typing import Any, List, Tuple, Union, Literal, Optional

from nonebot.message import handle_event

from nonebot.adapters import Bot as BaseBot
from nonebot.adapters import Adapter as BaseAdapter

from .utils import log
from .config import BotInfo
from .event import Event, MessageEvent
from .model import Group, Member, Profile
from .message import Message, MessageSegment


def get_peer_data(event: Event, **kwargs: Any) -> Tuple[int, str]:
    if isinstance(event, MessageEvent):
        return event.chatType, event.peerUin or event.peerUid
    return kwargs["chatType"], kwargs["peerUin"]


class Bot(BaseBot):
    """
    Red 协议 Bot 适配。
    """

    @override
    def __init__(
        self, adapter: BaseAdapter, self_id: str, info: BotInfo, **kwargs: Any
    ):
        super().__init__(adapter, self_id)
        self.adapter: BaseAdapter = adapter
        self.info: BotInfo = info
        # 一些有关 Bot 的信息也可以在此定义和存储

    async def handle_event(self, event: Event):
        # 根据需要，对事件进行某些预处理，例如：
        # 检查事件是否和机器人有关操作，去除事件消息首尾的 @bot
        # 检查事件是否有回复消息，调用平台 API 获取原始消息的消息内容
        # 调用 handle_event 让 NoneBot 对事件进行处理
        # TODO: 见上
        await handle_event(self, event)

    async def send_message(
        self,
        chat_type: Literal["friend", "group"],
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageEvent:
        chat = 1 if chat_type == "friend" else 2
        peer = str(target)
        element_data = await Message(message).export(
            self.adapter, self.info, chat, peer
        )
        log("DEBUG", "Trying to send a message")
        resp = await self.call_api(
            "send_message",
            chat_type=chat,
            target=peer,
            elements=element_data,
        )
        return MessageEvent.parse_obj(resp)

    async def send_friend_message(
        self,
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageEvent:
        return await self.send_message("friend", target, message)

    async def send_group_message(
        self,
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageEvent:
        return await self.send_message("group", target, message)

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs: Any,
    ) -> MessageEvent:
        # 根据平台实现 Bot 回复事件的方法

        # 将消息处理为平台所需的格式后，调用发送消息接口进行发送，例如：
        chatType, peerUin = get_peer_data(event, **kwargs)
        element_data = await Message(message).export(
            self.adapter, self.info, chatType, peerUin
        )
        log("DEBUG", "Trying to send a message")
        resp = await self.call_api(
            "send_message",
            chat_type=chatType,
            target=peerUin,
            elements=element_data,
        )

        return MessageEvent.parse_obj(resp)

    async def get_self_profile(self) -> Profile:
        resp = await self.call_api("get_self_profile")
        return Profile.parse_obj(resp)

    async def get_friends(self) -> List[Profile]:
        resp = await self.call_api("get_friends")
        return [Profile.parse_obj(data) for data in resp]

    async def get_groups(self) -> List[Group]:
        resp = await self.call_api("get_groups")
        return [Group.parse_obj(data) for data in resp]

    async def mute_everyone(self, group: int, enable: bool = True):
        await self.call_api("mute_everyone", group=group, enable=enable)

    async def kick(
        self,
        group: int,
        *members: int,
        refuse_forever: bool = False,
        reason: Optional[str] = None,
    ):
        await self.call_api(
            "kick",
            group=group,
            members=list(members),
            refuse_forever=refuse_forever,
            reason=reason,
        )

    async def get_announcements(self, group: int) -> List[dict]:
        return await self.call_api("get_announcements", group=group)

    async def get_members(self, group: int, size: int = 20) -> List[Member]:
        resp = await self.call_api("get_members", group=group, size=size)
        return [Member.parse_obj(data) for data in resp]

    async def fetch_media(
        self,
        msg_id: str,
        chat_type: Literal["friend", "group"],
        target: Union[int, str],
        element_id: str,
        thumb_size: int = 0,
        download_type: int = 2,
    ) -> bytes:
        chat = 1 if chat_type == "friend" else 2
        peer = str(target)
        return await self.call_api(
            "fetch_media",
            msg_id=msg_id,
            chat_type=chat,
            target=peer,
            element_id=element_id,
            thumb_size=thumb_size,
            download_type=download_type,
        )

    async def upload(self, file: bytes) -> str:
        return await self.call_api("upload", file=file)

    async def recall_message(
        self,
        chat_type: Literal["friend", "group"],
        target: Union[int, str],
        *ids: str,
    ):
        chat = 1 if chat_type == "friend" else 2
        peer = str(target)
        await self.call_api(
            "recall_message",
            chat_type=chat,
            target=peer,
            msg_ids=list(ids),
        )

    async def recall_group_message(self, group: int, *ids: str):
        await self.recall_message("group", group, *ids)

    async def recall_friend_message(self, friend: int, *ids: str):
        await self.recall_message("friend", friend, *ids)

    async def get_history_messages(
        self,
        chat_type: Literal["friend", "group"],
        target: Union[int, str],
        offset: int = 0,
        count: int = 100,
    ):
        chat = 1 if chat_type == "friend" else 2
        peer = str(target)
        return await self.call_api(
            "get_history_messages",
            chat_type=chat,
            target=peer,
            offset=offset,
            count=count,
        )
