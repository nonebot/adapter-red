from io import BytesIO
from pathlib import Path
from base64 import b64encode
from typing import Type, Iterable, List, Union
from typing_extensions import override

from nonebot import get_bot

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .model import Element, TextElement, PicElement



class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @override(BaseMessageSegment)
    def get_message_class(cls) -> Type["Message"]:
        # 返回适配器的 Message 类型本身
        return Message

    @override(BaseMessageSegment)
    def __str__(self) -> str:
        # 返回该消息段的纯文本表现形式，通常在日志中展示
        if self.is_text():
            return escape_tag(self.data.get("text", ""))
        return str(self.data.dict())

    @override(BaseMessageSegment)
    def is_text(self) -> bool:
        # 判断该消息段是否为纯文本
        return self.type == "text"
#
#     @staticmethod
#     def text(text: str) -> "MessageSegment":
#         return MessageSegment("text",
#             Element(
#                 elementType=1,
#                 textElement=TextElement(content=text)
#             )
#         )
#
#     @staticmethod
#     def at(text: str, user_id: str) -> "MessageSegment":
#         return MessageSegment("at",
#             Element(
#                 elementType=1,
#                 textElement=TextElement(
#                     content=text,
#                     atType=2,
#                     atNtUid=user_id
#                 )
#             )
#         )
#
#     @staticmethod
#     def reply(message_seq: str, message_id: str, sender_id: str) -> "MessageSegment":
#         return MessageSegment("reply",
#             Element(
#                 elementType=7,
#                 replyElement={
#                     "replayMsgSeq": message_seq,
#                     "sourceMsgIdInRecords": message_id,
#                     "senderUid": sender_id
#                 }
#             )
#         )
#
#     @staticmethod
#     def face(face_index: int, face_type: int):
#         return MessageSegment("face",
#             Element(
#                 elementType=6,
#                 faceElement={
#                     "faceIndex": face_index,
#                     "faceType": face_type
#                 }
#             )
#         )
#
#     @staticmethod
#     def image(md5_hex: str, file_size: int, height: int = None, width: int = None, *, filename: str, source_path: str):
#         return MessageSegment("image",
#             Element(
#                 elementType=2,
#                 picElement=PicElement(
#                     md5HexStr=md5_hex,
#                     fileSize=file_size,
#                     picHeight=height,
#                     picWidth=width,
#                     fileName=filename,
#                     sourcePath=source_path
#                 )
#             )
#         )
        

class Message(BaseMessage[MessageSegment]):
    @classmethod
    @override(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        # 返回适配器的 MessageSegment 类型本身
        return MessageSegment
    
    @classmethod
    @override(BaseMessage)
    def get_elements(cls) -> List[Element]:
        return [msg_seg.data for msg_seg in cls]

    @staticmethod
    @override(BaseMessage)
    def _construct(data: List[Element]) -> Iterable[MessageSegment]:
        # 实现从字符串中构造消息数组，如无字符串嵌入格式可直接返回文本类型 MessageSegment
        result = []
        for element in data:
            if isinstance(element, TextElement):
                if hasattr(element, "atNtUid"):
                    result.append(MessageSegment.at(element.content, element.atNtUid))
                elif element.replyElement is not None:
                    result.append(MessageSegment.reply(element.replyElement["replayMsgSeq"], element.replyElement["sourceMsgIdInRecords"], element.replyElement["senderUid"]))
                else:
                    result.append(MessageSegment.text(element.content))
            if isinstance(element, PicElement):
                result.append(MessageSegment.image(element.picElement.sourcePath))
            if element.faceElement is not None:
                result.append(MessageSegment.face(element.faceElement["faceIndex"], element.faceElement["faceType"]))
        return result