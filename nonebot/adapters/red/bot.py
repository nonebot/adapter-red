import re
import random
from datetime import timedelta
from typing_extensions import override
from typing import Any, List, Tuple, Union, Optional

from nonebot.message import handle_event

from nonebot.adapters import Bot as BaseBot
from nonebot.adapters import Adapter as BaseAdapter
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .utils import log
from .config import BotInfo
from .api.model import Group, Member
from .event import Event, MessageEvent
from .api.model import Message as MessageModel
from .api.model import Profile, ChatType, UploadResponse
from .message import Message, ForwardNode, MessageSegment, MediaMessageSegment


def _check_at_me(bot: "Bot", event: MessageEvent) -> None:
    if event.chatType == ChatType.FRIEND:
        event.to_me = True
    else:
        first_element = event.elements[0]
        if (
            first_element.elementType == 1
            and first_element.textElement
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
                and second_element.textElement
                and second_element.textElement.atType == 0
                and not second_element.textElement.content.strip()
            ):
                event.elements.pop(0)

        if not event.to_me:
            i = -1
            last_element = event.elements[i]
            if (
                last_element.elementType == 1
                and last_element.textElement
                and last_element.textElement.atType == 0
                and not last_element.textElement.content.strip()
                and len(event.elements) >= 1
            ):
                # 处理at后的空格
                i -= 1
                last_element = event.elements[i]

            if (
                last_element.elementType == 1
                and last_element.textElement
                and last_element.textElement.atType == 2
                and last_element.textElement.atNtUin == bot.self_id
            ):
                event.to_me = True
                event.elements.pop(i)


def _check_reply_me(bot: "Bot", event: MessageEvent) -> None:
    first_element = event.elements[0]
    if (
        first_element.elementType == 7
        and first_element.replyElement
        and (
            first_element.replyElement.senderUin == bot.self_id
            or first_element.replyElement.senderUid == bot.self_id
        )
    ):
        event.to_me = True
        event.reply = event.elements.pop(0)


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
            _check_reply_me(self, event)
            _check_nickname(self, event)

        await handle_event(self, event)

    async def send_message(
        self,
        chat_type: ChatType,
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageModel:
        """依据聊天类型与目标 id 发送消息

        参数:
            chat_type: 聊天类型，分为好友与群组
            target: 目标 id
            message: 发送的消息
        """
        element_data = await Message(message).export(self)
        resp = await self.call_api(
            "send_message",
            chat_type=chat_type,
            target=str(target),
            elements=element_data,
        )
        return MessageModel.parse_obj(resp)

    async def send_friend_message(
        self,
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageModel:
        """发送好友消息

        参数:
            target: 好友 id
            message: 发送的消息
        """
        return await self.send_message(ChatType.FRIEND, target, message)

    async def send_group_message(
        self,
        target: Union[int, str],
        message: Union[str, Message, MessageSegment],
    ) -> MessageModel:
        """发送群组消息

        参数:
            target: 群组 id
            message: 发送的消息
        """
        return await self.send_message(ChatType.GROUP, target, message)

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs: Any,
    ) -> MessageModel:
        """依据收到的事件发送消息

        参数:
            event: 收到的事件
            message: 发送的消息
        """
        chatType, peerUin = get_peer_data(event, **kwargs)
        element_data = await Message(message).export(self)
        resp = await self.call_api(
            "send_message",
            chat_type=chatType,
            target=peerUin,
            elements=element_data,
        )
        return MessageModel.parse_obj(resp)

    async def get_self_profile(self) -> Profile:
        """获取登录账号自己的资料"""
        resp = await self.call_api("get_self_profile")
        return Profile.parse_obj(resp)

    async def get_friends(self) -> List[Profile]:
        """获取登录账号所有好友的资料"""
        resp = await self.call_api("get_friends")
        return [Profile.parse_obj(data) for data in resp]

    async def get_groups(self) -> List[Group]:
        """获取登录账号所有群组的资料"""
        resp = await self.call_api("get_groups")
        return [Group.parse_obj(data) for data in resp]

    async def mute_member(
        self, group: int, *members: int, duration: Union[int, timedelta] = 60
    ):
        """禁言群成员

        禁言时间会自动限制在 60s 至 30天内

        参数:
            group: 群号
            *members: 禁言目标的 id
            duration: 禁言时间
        """
        if isinstance(duration, timedelta):
            duration = int(duration.total_seconds())
        duration = max(60, min(2592000, duration))
        await self.call_api(
            "mute_member", group=group, members=list(members), duration=duration
        )

    async def unmute_member(self, group: int, *members: int):
        """解除群成员禁言

        参数:
            group: 群号
            *members: 禁言目标的 id
        """
        await self.call_api("unmute_member", group=group, members=list(members))

    async def mute_everyone(self, group: int):
        """开启全体禁言

        参数:
            group: 群号
        """
        await self.call_api("mute_everyone", group=group)

    async def unmute_everyone(self, group: int):
        """关闭全体禁言

        参数:
            group: 群号
        """
        await self.call_api("unmute_everyone", group=group)

    async def kick(
        self,
        group: int,
        *members: int,
        refuse_forever: bool = False,
        reason: Optional[str] = None,
    ):
        """移除群成员

        参数:
            group: 群号
            *members: 要移除的群成员账号
            refuse_forever: 是否不再接受群成员的入群申请
            reason: 移除理由
        """
        await self.call_api(
            "kick",
            group=group,
            members=list(members),
            refuse_forever=refuse_forever,
            reason=reason,
        )

    async def get_announcements(self, group: int) -> List[dict]:
        """拉取群公告

        参数:
            group: 群号
        """
        return await self.call_api("get_announcements", group=group)

    async def get_members(self, group: int, size: int = 20) -> List[Member]:
        """获取指定群组内的成员资料

        参数:
            group: 群号
            size: 拉取多少个成员资料
        """
        resp = await self.call_api("get_members", group=group, size=size)
        return [Member.parse_obj(data) for data in resp]

    async def fetch(self, ms: BaseMessageSegment):
        """获取媒体消息段的二进制数据

        参数:
            ms: 消息段
        """
        if not isinstance(ms, MediaMessageSegment):
            raise ValueError(f"{ms} do not support to fetch data")
        return await ms.download(self)

    async def fetch_media(
        self,
        msg_id: str,
        chat_type: ChatType,
        target: Union[int, str],
        element_id: str,
        thumb_size: int = 0,
        download_type: int = 2,
    ) -> bytes:
        """获取媒体消息的二进制数据

        注意：此接口不推荐直接使用

        若需要获取媒体数据，你可以使用 `bot.fetch(MessageSegment)` 接口，
        或 `ms.download(Bot)` 接口

        参数:
            msg_id: 媒体消息的消息 id
            chat_type: 媒体消息的聊天类型
            target: 媒体消息的聊天对象 id
            element_id: 媒体消息中媒体元素的 id
        """
        log("WARING", "This API is not suggest for user usage")
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

    async def upload(self, file: bytes) -> UploadResponse:
        """上传资源

        注意：此接口不推荐直接使用

        参数:
            file: 上传的资源数据
        """
        log("WARING", "This API is not suggest for user usage")
        return UploadResponse.parse_obj(await self.call_api("upload", file=file))

    async def recall_message(
        self,
        chat_type: ChatType,
        target: Union[int, str],
        *ids: str,
    ):
        """撤回消息

        参数:
            chat_type: 聊天类型，分为好友与群组
            target: 目标 id
            *ids: 要撤回的消息 id
        """
        peer = str(target)
        await self.call_api(
            "recall_message",
            chat_type=chat_type,
            target=peer,
            msg_ids=list(ids),
        )

    async def recall_group_message(self, group: int, *ids: str):
        """撤回群组消息

        参数:
            target: 群组 id
            *ids: 要撤回的消息 id
        """
        await self.recall_message(ChatType.GROUP, group, *ids)

    async def recall_friend_message(self, friend: int, *ids: str):
        """撤回好友消息

        参数:
            target: 好友 id
            *ids: 要撤回的消息 id
        """
        await self.recall_message(ChatType.FRIEND, friend, *ids)

    async def get_history_messages(
        self,
        chat_type: ChatType,
        target: Union[int, str],
        offset: int = 0,
        count: int = 100,
    ):
        """拉取历史消息

        参数:
            chat_type: 聊天类型，分为好友与群组
            target: 目标 id
            offset: 从最近一条消息算起，选择从第几条消息开始拉取
            count: 一次拉取多少消息
        """
        peer = str(target)
        return await self.call_api(
            "get_history_messages",
            chat_type=chat_type,
            target=peer,
            offset=offset,
            count=count,
        )

    async def send_fake_forward(
        self,
        nodes: List[ForwardNode],
        chat_type: ChatType,
        target: Union[int, str],
        source_chat_type: Optional[ChatType] = None,
        source_target: Optional[Union[int, str]] = None,
    ):
        """发送伪造合并转发消息

        参数:
            nodes: 合并转发节点
            chat_type: 聊天类型，分为好友与群组
            target: 目标 id
            source_chat_type: 伪造的消息来源聊天类型，分为好友与群组
            source_target: 伪造的消息来源聊天对象 id
        """
        if not nodes:
            raise ValueError("nodes cannot be empty")
        peer = str(target)
        src_peer = str(source_target or target)
        base_seq = random.randint(0, 65535)
        elems = []
        for node in nodes:
            elems.append(await node.export(base_seq, self))
            base_seq += 1
        await self.call_api(
            "send_fake_forward",
            chat_type=chat_type,
            target=peer,
            source_chat_type=source_chat_type or chat_type,
            source_target=src_peer,
            elements=elems,
        )
