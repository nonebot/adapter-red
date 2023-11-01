import re
from copy import deepcopy
from typing import Any, Dict, Optional
from typing_extensions import override
from datetime import datetime, timedelta

from nonebot.utils import escape_tag
from pydantic.class_validators import root_validator

from nonebot.adapters import Event as BaseEvent

from .message import Message
from .api.model import Message as MessageModel
from .api.model import MsgType, ChatType, ReplyElement, ShutUpTarget


class Event(BaseEvent):
    @override
    def get_type(self) -> str:
        # 现阶段Red协议只有message事件
        return "event"

    @override
    def get_event_name(self) -> str:
        # 返回事件的名称，用于日志打印
        return "event"

    @override
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @override
    def get_message(self):
        raise ValueError("Event has no message!")

    @override
    def get_user_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def get_session_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def is_tome(self) -> bool:
        raise ValueError("Event has no context!")

    @classmethod
    def convert(cls, obj: Any):
        """将 Red API 返回的数据转换为对应的 Model 类

        子类可根据需要重写此方法
        """
        return cls.parse_obj(obj)


class MessageEvent(Event, MessageModel):
    """消息事件"""

    to_me: bool = False
    """
    :说明: 消息是否与机器人有关

    :类型: ``bool``
    """
    reply: Optional[ReplyElement] = None
    """
    :说明: 消息中提取的回复消息，内容为 ``get_msg`` API 返回结果

    :类型: ``Optional[ReplyElement]``
    """
    message: Message
    original_message: Message

    @override
    def get_type(self) -> str:
        return "message"

    @override
    def get_event_name(self) -> str:
        # 返回事件的名称，用于日志打印
        return "message"

    @override
    def get_message(self) -> Message:
        return self.message

    @root_validator(pre=True, allow_reuse=True)
    def check_message(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "elements" in values:
            values["message"] = Message.from_red_message(
                values["elements"],
                values["msgId"],
                values["chatType"],
                values["peerUin"] or values["peerUid"],
            )
            values["original_message"] = deepcopy(values["message"])
        return values

    @override
    def get_user_id(self) -> str:
        # 获取用户 ID 的方法，根据事件具体实现，如果事件没有用户 ID，则抛出异常
        if self.senderUin is None:
            raise ValueError("user_id doesn't exist.")
        return self.senderUin

    @override
    def get_session_id(self) -> str:
        # 获取事件会话 ID 的方法，根据事件具体实现，如果事件没有相关 ID，则抛出异常
        return f"{self.peerUin or self.peerUid}_{self.senderUin or self.senderUid}"

    @override
    def is_tome(self) -> bool:
        return self.to_me

    @property
    def scene(self) -> str:
        """群组或好友的id"""
        return self.peerUin or self.peerUid

    @property
    def is_group(self) -> bool:
        """是否为群组消息"""
        return self.chatType == ChatType.GROUP

    @property
    def is_private(self) -> bool:
        """是否为私聊消息"""
        return self.chatType == ChatType.FRIEND


class PrivateMessageEvent(MessageEvent):
    """好友消息事件"""

    @override
    def get_event_name(self) -> str:
        return "message.private"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from {self.sendNickName or self.senderUin or self.senderUid}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

    @property
    def user_id(self) -> str:
        """好友的id"""
        return self.peerUin or self.peerUid


class GroupMessageEvent(MessageEvent):
    @override
    def get_event_name(self) -> str:
        return "message.group"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Message from {self.sendMemberName or self.senderUin or self.senderUid} "
            f"in {self.peerName or self.peerUin or self.peerUid}: "
            f"{self.get_message()}"
        )
        return escape_tag(text)

    @property
    def group_id(self) -> str:
        """群组的id"""
        return self.peerUin or self.peerUid


class NoticeEvent(Event):
    msgId: str
    msgRandom: str
    msgSeq: str
    cntSeq: str
    chatType: ChatType
    msgType: MsgType
    subMsgType: int
    peerUid: str
    peerUin: Optional[str]

    @override
    def get_type(self) -> str:
        return "notice"

    @override
    def get_event_name(self) -> str:
        return "notice"

    @property
    def scene(self) -> str:
        """群组或好友的id"""
        return self.peerUin or self.peerUid

    class Config:
        extra = "ignore"


class GroupNameUpdateEvent(NoticeEvent):
    """群名变更事件"""

    currentName: str
    operatorUid: str
    operatorName: str

    @override
    def get_event_name(self) -> str:
        return "notice.group_name_update"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Group {self.peerUin or self.peerUid} name updated to {self.currentName}"
        )
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        # 获取用户 ID 的方法，根据事件具体实现，如果事件没有用户 ID，则抛出异常
        if self.operatorUid is None:
            raise ValueError("user_id doesn't exist.")
        return self.operatorUid

    @override
    def get_session_id(self) -> str:
        # 获取事件会话 ID 的方法，根据事件具体实现，如果事件没有相关 ID，则抛出异常
        return f"{self.peerUin or self.peerUid}_{self.operatorUid}"

    @classmethod
    @override
    def convert(cls, obj: Any):
        assert isinstance(obj, MessageModel)
        return cls(
            msgId=obj.msgId,
            msgRandom=obj.msgRandom,
            msgSeq=obj.msgSeq,
            cntSeq=obj.cntSeq,
            chatType=obj.chatType,
            msgType=obj.msgType,
            subMsgType=obj.subMsgType,
            peerUid=obj.peerUid,
            peerUin=obj.peerUin,
            currentName=obj.elements[0].grayTipElement.groupElement.groupName,  # type: ignore  # noqa: E501
            operatorUid=obj.elements[0].grayTipElement.groupElement.memberUin,  # type: ignore  # noqa: E501
            operatorName=obj.elements[0].grayTipElement.groupElement.memberNick,  # type: ignore  # noqa: E501
        )


legacy_invite_message = re.compile(
    r'jp="(\d+)".*jp="(\d+)"', re.DOTALL | re.MULTILINE | re.IGNORECASE
)


class MemberAddEvent(NoticeEvent):
    """群成员增加事件"""

    memberUid: str
    operatorUid: str
    memberName: Optional[str]

    @override
    def get_event_name(self) -> str:
        return "notice.member_add"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Member {f'{self.memberName}({self.memberUid})' if self.memberName else self.memberUid} added to "  # noqa: E501
            f"{self.peerUin or self.peerUid}"
        )
        return escape_tag(text)

    @override
    def get_user_id(self) -> str:
        return self.memberUid

    @override
    def get_session_id(self) -> str:
        # 获取事件会话 ID 的方法，根据事件具体实现，如果事件没有相关 ID，则抛出异常
        return f"{self.peerUin or self.peerUid}_{self.memberUid}"

    @classmethod
    @override
    def convert(cls, obj: Any):
        assert isinstance(obj, MessageModel)
        params = {
            "msgId": obj.msgId,
            "msgRandom": obj.msgRandom,
            "msgSeq": obj.msgSeq,
            "cntSeq": obj.cntSeq,
            "chatType": obj.chatType,
            "msgType": obj.msgType,
            "subMsgType": obj.subMsgType,
            "peerUid": obj.peerUid,
            "peerUin": obj.peerUin,
        }
        if obj.elements[0].grayTipElement and obj.elements[0].grayTipElement.xmlElement and obj.elements[0].grayTipElement.xmlElement.content:  # type: ignore  # noqa: E501
            # fmt: off
            if not (mat := legacy_invite_message.search(obj.elements[0].grayTipElement.xmlElement.content)):  # type: ignore  # noqa: E501
                raise ValueError("Invalid legacy invite message.")
            # fmt: on
            params["operatorUid"] = mat[1]
            params["memberUid"] = mat[2]
        else:
            params["memberUid"] = obj.elements[0].grayTipElement.groupElement.memberUin  # type: ignore  # noqa: E501
            params["operatorUid"] = obj.elements[0].grayTipElement.groupElement.adminUin  # type: ignore  # noqa: E501
            params["memberName"] = obj.elements[0].grayTipElement.groupElement.memberNick  # type: ignore  # noqa: E501
        return cls(**params)


class MemberMuteEvent(NoticeEvent):
    """群成员禁言相关事件"""

    start: datetime
    duration: timedelta
    operator: ShutUpTarget
    member: ShutUpTarget

    @override
    def get_user_id(self) -> str:
        return self.member.uin or self.member.uid

    @override
    def get_session_id(self) -> str:
        # 获取事件会话 ID 的方法，根据事件具体实现，如果事件没有相关 ID，则抛出异常
        return f"{self.peerUin or self.peerUid}_{self.member.uin or self.member.uid}"

    @classmethod
    @override
    def convert(cls, obj: Any):
        assert isinstance(obj, MessageModel)
        # fmt: off
        params = {
            "msgId": obj.msgId,
            "msgRandom": obj.msgRandom,
            "msgSeq": obj.msgSeq,
            "cntSeq": obj.cntSeq,
            "chatType": obj.chatType,
            "msgType": obj.msgType,
            "subMsgType": obj.subMsgType,
            "peerUid": obj.peerUid,
            "peerUin": obj.peerUin,
            "start": datetime.fromtimestamp(
                obj.elements[0].grayTipElement.groupElement.shutUp.curTime  # type: ignore  # noqa: E501
            ),
            "duration": timedelta(
                seconds=obj.elements[0].grayTipElement.groupElement.shutUp.duration  # type: ignore  # noqa: E501
            ),
            "operator": obj.elements[0].grayTipElement.groupElement.shutUp.admin,  # type: ignore  # noqa: E501
            "member": obj.elements[0].grayTipElement.groupElement.shutUp.member, # type: ignore  # noqa: E501
        }
        # fmt: on
        if params["duration"].total_seconds() < 1:
            return MemberUnmuteEvent(**params)
        return MemberMutedEvent(**params)


class MemberMutedEvent(MemberMuteEvent):
    """群成员被禁言事件"""

    @override
    def get_event_name(self) -> str:
        return "notice.member_muted"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Member {self.member.uin or self.member.uid} muted in "
            f"{self.peerUin or self.peerUid} for {self.duration}"
        )
        return escape_tag(text)


class MemberUnmuteEvent(MemberMuteEvent):
    """群成员被解除禁言事件"""

    @override
    def get_event_name(self) -> str:
        return "notice.member_unmute"

    @override
    def get_event_description(self) -> str:
        text = (
            f"Member {self.member.uin or self.member.uid} unmute in "
            f"{self.peerUin or self.peerUid}"
        )
        return escape_tag(text)
