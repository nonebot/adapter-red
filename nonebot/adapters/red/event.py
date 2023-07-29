from typing import List, Any, Optional, Literal, Union
from typing_extensions import override

from nonebot.adapters import Event as BaseEvent
from nonebot.utils import escape_tag

from .model import Element, RoleInfo, Message as MessageModel
from .message import MessageSegment, Message


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
        return False





class MessageEvent(Event, MessageModel):
    """消息事件"""

    @override
    def get_type(self) -> str:
        return "message"

    @override
    def get_event_name(self) -> str:
        # 返回事件的名称，用于日志打印
        return "message"

    @override
    def get_message(self) -> Message:
        # 获取事件消息的方法，根据事件具体实现，如果事件非消息类型事件，则抛出异常
        return Message.from_red_message(self.elements)

    @override
    def get_user_id(self) -> str:
        # 获取用户 ID 的方法，根据事件具体实现，如果事件没有用户 ID，则抛出异常
        if self.senderUin is None:
            raise ValueError("user_id doesn't exist.")
        return self.senderUin

    @override
    def get_session_id(self) -> str:
        # 获取事件会话 ID 的方法，根据事件具体实现，如果事件没有相关 ID，则抛出异常
        return self.msgId


class PrivateMessageEvent(MessageEvent):
    """好友消息事件"""
    chatType: Literal[1]
    

    @override
    def get_type(self) -> str:
        return "message.private"
    
    @override
    def get_event_description(self) -> str:
        text = f"收到好友 {self.senderUin} 的消息: {self.get_plaintext()}"
        return escape_tag(str(text))


class GroupMessageEvent(MessageEvent):
    chatType: Literal[2]


    @override
    def get_type(self) -> str:
        return "message.group"
    
    @override
    def get_event_description(self) -> str:
        text = f"收到群 {self.peerName} 内 {self.sendMemberName} 的消息: {self.get_plaintext()}"
        return escape_tag(str(text))
