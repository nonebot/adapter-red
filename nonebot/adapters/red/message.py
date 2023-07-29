from io import BytesIO
from pathlib import Path
from base64 import b64encode
from typing import Type, Iterable, List, Union, TYPE_CHECKING
from typing_extensions import override

from nonebot import get_bot

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .model import Element, TextElement, PicElement



class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        # 返回适配器的 Message 类型本身
        return Message

    @override
    def __str__(self) -> str:
        # 返回该消息段的纯文本表现形式，通常在日志中展示
        return self.data["text"] if self.is_text() else f"[{self.type}: {self.data}]"

    @override
    def is_text(self) -> bool:
        # 判断该消息段是否为纯文本
        return self.type == "text"

    @staticmethod
    def text(text: str) -> "MessageSegment":
        return MessageSegment("text", {"text": text})

    @staticmethod
    def at(user_id: str) -> "MessageSegment":
        return MessageSegment("at", {"user_id": user_id})

    @staticmethod
    def at_all() -> "MessageSegment":
        return MessageSegment("at_all")

    @staticmethod
    def face(face_id: str) -> "MessageSegment":
        return MessageSegment("face", {"face_id": face_id})

    @staticmethod
    def image(file: Union[Path, BytesIO]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MessageSegment("image", {"file": file})

    @staticmethod
    def reply(message_id: str, message_seq: str) -> "MessageSegment":
        return MessageSegment("reply", {"msg_id": message_id, "msg_seq": message_seq})

    @staticmethod
    def ark(data: str) -> "MessageSegment":
        return MessageSegment("ark", {"data": data})

class Message(BaseMessage[MessageSegment]):
    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        # 返回适配器的 MessageSegment 类型本身
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        # 实现从字符串中构造消息数组，如无字符串嵌入格式可直接返回文本类型 MessageSegment
        yield MessageSegment.text(msg)

    @classmethod
    def from_red_message(cls, message: List[Element]) -> "Message":
        msg = Message()
        for element in message:
            if element.elementId == 1:
                if TYPE_CHECKING:
                    assert element.textElement
                text = element.textElement
                if not text.atType:
                    msg.append(MessageSegment.text(text.content))
                elif text.atType == 1:
                    msg.append(MessageSegment.at_all())
                elif text.atType == 2:
                    msg.append(MessageSegment.at(text.atNtUin or text.atNtUid))
            if element.elementId == 2:
                if TYPE_CHECKING:
                    assert element.picElement
                pic = element.picElement
                msg.append(
                    MessageSegment(
                        "image",
                        {
                            "md5": pic.md5HexStr,
                            "size": pic.fileSize,
                            "id": element.elementId,
                            "uuid": pic.fileUuid,
                            "path": pic.sourcePath,
                            "width": pic.picWidth,
                            "height": pic.picHeight,
                        }
                    )
                )
            if element.elementId == 6:
                if TYPE_CHECKING:
                    assert element.faceElement
                face = element.faceElement
                msg.append(MessageSegment.face(face["faceIndex"]))
            if element.elementId == 7:
                if TYPE_CHECKING:
                    assert element.replyElement
                reply = element.replyElement
                msg.append(MessageSegment(
                    "reply",
                    {
                        "msg_id": reply["sourceMsgIdInRecords"],
                        "msg_seq": reply["replayMsgSeq"]
                    }
                ))
            if element.elementId == 10:
                if TYPE_CHECKING:
                    assert element.arkElement
                ark = element.arkElement
                msg.append(MessageSegment.ark(ark["bytesData"]))
        return msg

    async def export(self) -> List[dict]:
        res = []
        for seg in self:
            if seg.type == "text":
                res.append({"elementType": 1, "textElement": {"content": seg.data['text']}})
            elif seg.type == "at":
                res.append({"elementType": 1, "textElement": {"atType": 2, "atNtUin": seg.data['user_id']}})
            elif seg.type == "at_all":
                res.append({"elementType": 1, "textElement": {"atType": 1}})
            elif seg.type == "image":
                # TODO: 上传图片数据然后搓结构体
                # 需要拉取bytes数据, 并且这里得用formdata
                # data = await self.account.staff.fetch_resource(element.resource)
                # resp = await self.account.websocket_client.call_http(
                #     "multipart",
                #     "api/upload",
                #     {
                #         "file": {
                #             "value": data,
                #             "content_type": None,
                #             "filename": "file_image",
                #         }
                #     },
                # )
                # return {
                #     "elementType": 2,
                #     "picElement": {
                #         "original": True,
                #         "md5HexStr": resp["md5"],
                #         "picWidth": resp["imageInfo"]["width"],
                #         "picHeight": resp["imageInfo"]["height"],
                #         "fileSize": resp["fileSize"],
                #         "sourcePath": resp["ntFilePath"],
                #     },
                # }
                ...
            elif seg.type == "face":
                res.append({"elementType": 6, "faceElement": {"faceIndex": seg.data["face_id"]}})
            elif seg.type == "reply":
                res.append(
                    {
                        "elementType": 7,
                        "replyElement": {
                            "sourceMsgIdInRecords": seg.data["msg_id"],
                            "replayMsgSeq": seg.data["msg_seq"]
                        }
                    }
                )
        return res