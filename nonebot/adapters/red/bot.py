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
from .api.model import Message as MessageModel
from .event import Event, NoticeEvent, MessageEvent
from .api.model import Profile, ChatType, UploadResponse
from .message import Message, ForwardNode, MessageSegment, MediaMessageSegment


def _check_reply(bot: "Bot", event: MessageEvent) -> None:
    """检查消息中存在的回复，去除并赋值 `event.reply`, `event.to_me`。

    参数:
        bot: Bot 对象
        event: MessageEvent 对象
    """
    try:
        index = event.message.index("reply")
    except ValueError:
        return

    msg_seg = event.message[index]

    event.reply = msg_seg.data["_origin"]  # type: ignore

    # ensure string comparation
    if str(event.reply.senderUin) == str(bot.self_id) or str(
        event.reply.senderUid
    ) == str(bot.self_id):
        event.to_me = True

    del event.message[index]
    if len(event.message) > index and event.message[index].type == "at":
        del event.message[index]
    if len(event.message) > index and event.message[index].type == "text":
        event.message[index].data["text"] = event.message[index].data["text"].lstrip()
        if not event.message[index].data["text"]:
            del event.message[index]
    if not event.message:
        event.message.append(MessageSegment.text(""))


def _check_to_me(bot: "Bot", event: MessageEvent) -> None:
    """检查消息开头或结尾是否存在 @机器人，去除并赋值 `event.to_me`。

    参数:
        bot: Bot 对象
        event: MessageEvent 对象
    """
    if not isinstance(event, MessageEvent):
        return

    # ensure message not empty
    if not event.message:
        event.message.append(MessageSegment.text(""))

    if event.chatType == ChatType.FRIEND:
        event.to_me = True
    else:

        def _is_at_me_seg(segment: MessageSegment) -> bool:
            return segment.type == "at" and str(segment.data.get("user_id", "")) == str(
                bot.self_id
            )

        # check the first segment
        if _is_at_me_seg(event.message[0]):
            event.to_me = True
            event.message.pop(0)
            if event.message and event.message[0].type == "text":
                event.message[0].data["text"] = event.message[0].data["text"].lstrip()
                if not event.message[0].data["text"]:
                    del event.message[0]

        if not event.to_me:
            # check the last segment
            i = -1
            last_msg_seg = event.message[i]
            if (
                last_msg_seg.type == "text"
                and not last_msg_seg.data["text"].strip()
                and len(event.message) >= 2
            ):
                i -= 1
                last_msg_seg = event.message[i]

            if _is_at_me_seg(last_msg_seg):
                event.to_me = True
                del event.message[i:]

        if not event.message:
            event.message.append(MessageSegment.text(""))


def _check_nickname(bot: "Bot", event: MessageEvent) -> None:
    """检查消息开头是否存在昵称，去除并赋值 `event.to_me`。

    参数:
        bot: Bot 对象
        event: MessageEvent 对象
    """
    first_msg_seg = event.message[0]
    if first_msg_seg.type != "text":
        return

    nicknames = {re.escape(n) for n in bot.config.nickname}
    if not nicknames:
        return

    # check if the user is calling me with my nickname
    nickname_regex = "|".join(nicknames)
    first_text = first_msg_seg.data["text"]
    if m := re.search(rf"^({nickname_regex})([\s,，]*|$)", first_text, re.IGNORECASE):
        log("DEBUG", f"User is calling me {m[1]}")
        event.to_me = True
        first_msg_seg.data["text"] = first_text[m.end() :]


def get_peer_data(event: Event, **kwargs: Any) -> Tuple[int, str]:
    if isinstance(event, (MessageEvent, NoticeEvent)):
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
            _check_reply(self, event)
            _check_to_me(self, event)
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
        message = Message(message)
        if message.has("forward"):
            forward = message["forward", 0]
            return await self.send_fake_forward(
                forward.data["nodes"],
                chat_type,
                target,
            )
        element_data = await message.export(self)
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
        message = Message(message)
        if message.has("forward"):
            forward = message["forward", 0]
            return await self.send_fake_forward(
                forward.data["nodes"],
                ChatType(chatType),
                peerUin,
            )
        element_data = await message.export(self)
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
        return [Member.parse_obj(data["detail"]) for data in resp]

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
        offset_msg_id: Optional[str] = None,
        count: int = 100,
    ):
        """拉取历史消息

        参数:
            chat_type: 聊天类型，分为好友与群组
            target: 目标 id
            offset_msg_id: 从哪一条消息开始拉取，使用event.msgId
            count: 一次拉取多少消息
        """
        peer = str(target)
        return await self.call_api(
            "get_history_messages",
            chat_type=chat_type,
            target=peer,
            offset_msg_id=offset_msg_id,
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
            elems.append(await node.export(base_seq, self, int(src_peer)))
            base_seq += 1
        return await self.call_api(
            "send_fake_forward",
            chat_type=chat_type,
            target=peer,
            source_chat_type=source_chat_type or chat_type,
            source_target=src_peer,
            elements=elems,
        )

    async def send_group_forward(
        self,
        nodes: List[ForwardNode],
        group: Union[int, str],
        source_group: Optional[Union[int, str]] = None,
    ):
        """发送群组合并转发消息

        参数:
            nodes: 合并转发节点
            group: 群组 id
            source_group: 伪造的消息来源群组 id
        """
        return await self.send_fake_forward(
            nodes,
            ChatType.GROUP,
            group,
            source_chat_type=ChatType.GROUP,
            source_target=source_group,
        )
