import re
from datetime import timedelta
from typing_extensions import override
from typing import Any, List, Tuple, Union, Optional

from nonebot.message import handle_event

from nonebot.adapters import Bot as BaseBot
from nonebot.adapters import Adapter as BaseAdapter

from .config import BotInfo
from .api.model import Group, Member
from .event import Event, MessageEvent
from .api.model import Profile, ChatType
from .message import Message, MessageSegment
from .api.model import Message as MessageModel


def _check_at_me(bot: "Bot", event: MessageEvent) -> None:
    if event.chatType == ChatType.FRIEND:
        event.to_me = True
    else:
        first_element = event.elements[0]
        if (
            first_element.elementType == 1
            and first_element.textElement.atType == 2
            and first_element.textElement.atNtUin == bot.self_id
        ):
            event.to_me = True
            event.elements.pop(0)

        # 处理at后的空格
        if len(event.elements) >= 1:
            second_element = event.elements[0]
            if (
                second_element.elementType == 1
                and second_element.textElement.atType == 0
                and not second_element.textElement.content.strip()
            ):
                event.elements.pop(0)

        if not event.to_me:
            i = -1
            last_element = event.elements[i]
            if (
                last_element.elementType == 1
                and last_element.textElement.atType == 0
                and not last_element.textElement.content.strip()
                and len(event.elements) >= 1
            ):
                # 处理at后的空格
                i -= 1
                last_element = event.elements[i]

            if (
                last_element.elementType == 1
                and last_element.textElement.atType == 2
                and last_element.textElement.atNtUin == bot.self_id
            ):
                event.to_me = True
                event.elements.pop(i)


def _check_nickname(bot: "Bot", event: MessageEvent) -> None:
    element = event.elements[0]
    if element.elementType != 1:
        return

    nicknames = {re.escape(n) for n in bot.config.nickname}
    if not nicknames:
        return

    nickname_regex = "|".join(nicknames)
    if element.textElement is not None and element.textElement.content:
        if m := re.search(
            rf"^({nickname_regex})([\s,，]*|$)",
            element.textElement.content,
            re.IGNORECASE,
        ):
            event.to_me = True
            element.textElement.content = element.textElement.content[m.end() :]


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
        # TODO: 检查事件是否有回复消息，调用平台 API 获取原始消息的消息内容
        if isinstance(event, MessageEvent):
            _check_at_me(self, event)
            _check_nickname(self, event)

        await handle_event(self, event)

    async def send_message(
        self,
        chat_type: ChatType,
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageModel:
        peer = str(target)
        element_data = await Message(message).export(
            self.adapter, self.info, chat_type, peer
        )
        resp = await self.call_api(
            "send_message",
            chat_type=chat_type,
            target=peer,
            elements=element_data,
        )
        return MessageModel.parse_obj(resp)

    async def send_friend_message(
        self,
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageModel:
        return await self.send_message(ChatType.FRIEND, target, message)

    async def send_group_message(
        self,
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageModel:
        return await self.send_message(ChatType.GROUP, target, message)

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs: Any,
    ) -> MessageModel:
        chatType, peerUin = get_peer_data(event, **kwargs)
        element_data = await Message(message).export(
            self.adapter, self.info, chatType, peerUin
        )
        resp = await self.call_api(
            "send_message",
            chat_type=chatType,
            target=peerUin,
            elements=element_data,
        )
        return MessageModel.parse_obj(resp)

    async def get_self_profile(self) -> Profile:
        resp = await self.call_api("get_self_profile")
        return Profile.parse_obj(resp)

    async def get_friends(self) -> List[Profile]:
        resp = await self.call_api("get_friends")
        return [Profile.parse_obj(data) for data in resp]

    async def get_groups(self) -> List[Group]:
        resp = await self.call_api("get_groups")
        return [Group.parse_obj(data) for data in resp]

    async def mute_member(
        self, group: int, *members: int, duration: Union[int, timedelta] = 60
    ):
        if isinstance(duration, timedelta):
            duration = int(duration.total_seconds())
        duration = max(60, min(2592000, duration))
        await self.call_api(
            "mute_member", group=group, members=list(members), duration=duration
        )

    async def unmute_member(self, group: int, *members: int):
        await self.call_api("unmute_member", group=group, members=list(members))

    async def mute_everyone(self, group: int):
        await self.call_api("mute_everyone", group=group)

    async def unmute_everyone(self, group: int):
        await self.call_api("unmute_everyone", group=group)

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
        chat_type: ChatType,
        target: Union[int, str],
        element_id: str,
        thumb_size: int = 0,
        download_type: int = 2,
    ) -> bytes:
        peer = str(target)
        return await self.call_api(
            "fetch_media",
            msg_id=msg_id,
            chat_type=chat_type,
            target=peer,
            element_id=element_id,
            thumb_size=thumb_size,
            download_type=download_type,
        )

    async def upload(self, file: bytes) -> str:
        return await self.call_api("upload", file=file)

    async def recall_message(
        self,
        chat_type: ChatType,
        target: Union[int, str],
        *ids: str,
    ):
        peer = str(target)
        await self.call_api(
            "recall_message",
            chat_type=chat_type,
            target=peer,
            msg_ids=list(ids),
        )

    async def recall_group_message(self, group: int, *ids: str):
        await self.recall_message(ChatType.GROUP, group, *ids)

    async def recall_friend_message(self, friend: int, *ids: str):
        await self.recall_message(ChatType.FRIEND, friend, *ids)

    async def get_history_messages(
        self,
        chat_type: ChatType,
        target: Union[int, str],
        offset: int = 0,
        count: int = 100,
    ):
        peer = str(target)
        return await self.call_api(
            "get_history_messages",
            chat_type=chat_type,
            target=peer,
            offset=offset,
            count=count,
        )
