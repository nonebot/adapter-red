from typing import List, Any, Optional, Literal, Union
from typing_extensions import override

from nonebot.typing import overrides
from nonebot.adapters import Event as BaseEvent
from nonebot.utils import escape_tag

from .model import Element, RoleInfo
from .message import MessageSegment


class Event(BaseEvent):
    elements: List[Element]


    @overrides(BaseEvent)
    def get_type(self) -> str:
        # 现阶段Red协议只有message事件
        return "event"

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        # 返回事件的名称，用于日志打印
        return "event"

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @overrides(BaseEvent)
    def get_message(self):
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        raise ValueError("Event has no context!")

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        raise ValueError("Event has no context!")

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        return False


from .message import Message


class MessageEvent(Event):
    """消息事件"""
    chatType: Union[Literal[1], Literal[2]]
    msgId: str # Message Id
    msgRandom: str
    msgSeq: str
    cntSeq: str
    msgType: int
    subMsgType: int
    sendType: int
    senderUid: str
    peerUid: str # 群号
    channelId: str
    guildId: str
    guildCode: str
    fromUid: str
    fromAppid: str
    msgTime: str
    msgMeta: str
    sendStatus: int
    sendMemberName: str # Sender Name
    sendNickName: str # Sender Nickname
    guildName: str
    channelName: str
    records: List[Any]
    emojiLikesList: List[Any]
    commentCnt: str
    directMsgFlag: int
    directMsgMembers: List[Any]
    peerName: str # Group Name
    editable: bool
    avatarMeta: str
    avatarPendant: str
    feedId: str
    roleId: str
    timeStamp: str
    isImportMsg: bool
    atType: int
    roleType: int
    fromChannelRoleInfo: RoleInfo
    fromGuildRoleInfo: RoleInfo
    levelRoleInfo: RoleInfo
    recallTime: str
    isOnlineMsg: bool
    generalFlags: str
    clientSeq: str
    nameType: int
    avatarFlag: int
    senderUin: Optional[str]
    peerUin: Optional[str]

    @overrides(Event)
    def get_type(self) -> str:
        return "message"

    @overrides(Event)
    def get_event_name(self) -> str:
        # 返回事件的名称，用于日志打印
        return "message"

    @overrides(Event)
    def get_message(self):
        # 获取事件消息的方法，根据事件具体实现，如果事件非消息类型事件，则抛出异常
        content = Message()
        for element in self.elements:
            if element.textElement is not None:
                content += MessageSegment.text(element.textElement.content)
            if element.picElement is not None:
                content += MessageSegment.image(element.picElement.md5HexStr, element.picElement.fileSize, element.picElement.picHeight, element.picElement.picWidth, filename=element.picElement.fileName, source_path=element.picElement.sourcePath)
        return content
    
    @overrides(Event)
    def get_plaintext(self):
        content = ""
        for element in self.elements:
            if element.textElement is not None:
                content += element.textElement.content
            if element.picElement is not None:
                content += "[图片]"
        return content

    @overrides(Event)
    def get_user_id(self) -> str:
        # 获取用户 ID 的方法，根据事件具体实现，如果事件没有用户 ID，则抛出异常
        if self.senderUin is None:
            raise ValueError("user_id doesn't exist.")
        return self.senderUin

    @overrides(Event)
    def get_session_id(self) -> str:
        # 获取事件会话 ID 的方法，根据事件具体实现，如果事件没有相关 ID，则抛出异常
        return self.msgId


class PrivateMessageEvent(MessageEvent):
    '''好友消息事件'''
    chatType: Literal[1]
    

    @overrides(MessageEvent)
    def get_type(self) -> str:
        return "message.private"
    
    @overrides(MessageEvent)
    def get_event_description(self) -> str:
        text = "收到好友 {} 的消息: {}".format(self.senderUin, self.get_plaintext())
        return escape_tag(str(text))


class GroupMessageEvent(MessageEvent):
    chatType: Literal[2]


    @overrides(MessageEvent)
    def get_type(self) -> str:
        return "message.group"
    
    @overrides(MessageEvent)
    def get_event_description(self) -> str:
        text = "收到群 {} 内 {} 的消息: {}".format(self.peerName, self.sendMemberName, self.get_plaintext())
        return escape_tag(str(text))

