import json
from io import BytesIO
from pathlib import Path
from typing_extensions import override
from typing import TYPE_CHECKING, List, Type, Union, Iterable, Optional

from nonebot.exception import NetworkError
from nonebot.internal.driver import Request

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .model import Element
from .utils import log

if TYPE_CHECKING:
    from .adapter import Adapter


async def _handle_image(
    adapter: "Adapter", data: dict, chat_type: int, peer_uin: str
) -> bytes:
    path = Path(data["path"])
    if path.exists():
        with path.open("rb") as f:
            return f.read()
    resp = await adapter.request(
        Request(
            "GET", f"https://gchat.qpic.cn/gchatpic_new/0/0-0-{data['md5'].upper()}/0"
        )
    )
    if resp.status_code == 200:
        return resp.content
    resp1 = await adapter.request(
        Request(
            "POST",
            adapter.api_base / "message" / "fetchRichMedia",
            json={
                "msgId": data["_msg_id"],
                "chatType": chat_type,
                "peerUid": peer_uin,
                "elementId": data["id"],
                "thumbSize": 0,
                "downloadType": 2,
            },
        )
    )
    if resp1.status_code == 200:
        return resp1.content
    raise NetworkError("red", resp1)


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
    def image(file: Union[Path, BytesIO, bytes]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MessageSegment("image", {"file": file})

    @staticmethod
    def file(file: Union[Path, BytesIO, bytes]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MessageSegment("file", {"file": file})

    @staticmethod
    def voice(file: Union[Path, BytesIO, bytes]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MessageSegment("voice", {"file": file})

    @staticmethod
    def video(file: Union[Path, BytesIO, bytes]) -> "MessageSegment":
        if isinstance(file, Path):
            file = file.read_bytes()
        elif isinstance(file, BytesIO):
            file = file.getvalue()
        return MessageSegment("video", {"file": file})

    @staticmethod
    def face(face_id: str) -> "MessageSegment":
        return MessageSegment("face", {"face_id": face_id})

    @staticmethod
    def reply(message_id: str, message_seq: str, sender_uid: str) -> "MessageSegment":
        return MessageSegment(
            "reply",
            {"msg_id": message_id, "msg_seq": message_seq, "sender_uid": sender_uid},
        )

    @staticmethod
    def ark(data: str) -> "MessageSegment":
        return MessageSegment("ark", {"data": data})

    @staticmethod
    def market_face(
        package_id: str,
        emoji_id: str,
        face_name: str,
        key: str,
        face_path: str
    ) -> "MessageSegment":
        log("WARNING", "market_face only can be received!")
        return MessageSegment(
            "market_face",
            {
                "package_id": package_id,
                "emoji_id": emoji_id,
                "face_name": face_name,
                "key": key,
                "face_path": face_path,
            },
        )

    @staticmethod
    def forward_msg(xml: str, id: str, file_name: str) -> "MessageSegment":
        log("WARNING", "forward_msg only can be received!")
        return MessageSegment(
            "forward_msg",
            {"xml": xml, "id": id, "name": file_name},
        )

class Message(BaseMessage[MessageSegment]):
    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        # 返回适配器的 MessageSegment 类型本身
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield MessageSegment.text(msg)

    @classmethod
    def from_red_message(
        cls, message: List[Element], msg_id: Optional[str] = None
    ) -> "Message":
        msg = Message()
        for element in message:
            if element.elementType == 1:
                if TYPE_CHECKING:
                    assert element.textElement
                text = element.textElement
                if not text.atType:
                    msg.append(MessageSegment.text(text.content))
                elif text.atType == 1:
                    msg.append(MessageSegment.at_all())
                elif text.atType == 2:
                    msg.append(MessageSegment.at(text.atNtUin or text.atNtUid))
            if element.elementType == 2:
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
                            "_msg_id": msg_id,
                        },
                    )
                )
            if element.elementType == 3:
                if TYPE_CHECKING:
                    assert element.fileElement
                file = element.fileElement
                msg.append(
                    MessageSegment(
                        "file",
                        {
                            "id": element.elementId,
                            "md5": file.fileMd5,
                            "name": file.fileName,
                            "size": file.fileSize,
                            "uuid": file.fileUuid,
                            "_msg_id": msg_id,
                        },
                    )
                )
            if element.elementType == 4:
                if TYPE_CHECKING:
                    assert element.pttElement
                ptt = element.pttElement
                msg.append(
                    MessageSegment(
                        "voice",
                        {
                            "id": element.elementId,
                            "name": ptt.fileName,
                            "path": ptt.filePath,
                            "md5": ptt.md5HexStr,
                            "type": ptt.voiceChangeType,
                            "can_convert_to_text": ptt.canConvert2Text,
                            "text": ptt.text,
                            "wave_amplitudes": ptt.waveAmplitudes,
                            "uuid": ptt.fileUuid,
                            "_msg_id": msg_id,
                        },
                    )
                )
            if element.elementType == 5:
                if TYPE_CHECKING:
                    assert element.videoElement
                video = element.videoElement
                msg.append(
                    MessageSegment(
                        "video",
                        {
                            "filePath": video.filePath,
                            "fileName": video.fileName,
                            "videoMd5": video.videoMd5,
                            "thumbMd5": video.thumbMd5,
                            "fileTime": video.fileTime,
                            "thumbSize": video.thumbSize,
                            "fileFormat": video.fileFormat,
                            "fileSize": video.fileSize,
                            "thumbWidth": video.thumbWidth,
                            "thumbHeight": video.thumbHeight,
                            "busiType": video.busiType,
                            "subBusiType": video.subBusiType,
                            "thumbPath": video.thumbPath,
                            "transferStatus": video.transferStatus,
                            "progress": video.progress,
                            "invalidState": video.invalidState,
                            "fileUuid": video.fileUuid,
                            "fileSubId": video.fileSubId,
                            "fileBizId": video.fileBizId,
                        }
                    )
                )
            if element.elementType == 6:
                if TYPE_CHECKING:
                    assert element.faceElement
                face = element.faceElement
                msg.append(MessageSegment.face(face.faceIndex))
            if element.elementType == 7:
                if TYPE_CHECKING:
                    assert element.replyElement
                reply = element.replyElement
                msg.append(
                    MessageSegment(
                        "reply",
                        {
                            "msg_id": reply.sourceMsgIdInRecords,
                            "msg_seq": reply.replayMsgSeq,
                            "sender_uid": reply.senderUid,
                        },
                    )
                )
            if element.elementType == 10:
                if TYPE_CHECKING:
                    assert element.arkElement
                ark = element.arkElement
                msg.append(MessageSegment.ark(ark.bytesData))
            if element.elementType == 11:
                if TYPE_CHECKING:
                    assert element.marketFaceElement
                market_face = element.marketFaceElement
                msg.append(
                    MessageSegment(
                        "market_face",
                        {
                            "package_id": market_face.emojiPackageId,
                            "face_name": market_face.faceName,
                            "emoji_id": market_face.emojiId,
                            "key": market_face.key,
                            "static_path": market_face.staticFacePath,
                            "dynamic_path": market_face.dynamicFacePath,
                        }
                    )
                )
            if element.elementType == 16:
                if TYPE_CHECKING:
                    assert element.multiForwardMsgElement
                forward_msg = element.multiForwardMsgElement
                msg.append(
                    MessageSegment(
                        "forward_msg",
                        {
                            "xml": forward_msg.xmlContent,
                            "id": forward_msg.resId,
                            "name": forward_msg.fileName,
                        }
                    )
                )
        return msg

    async def export(
        self, adapter: "Adapter", chat_type: int, peer_uin: str
    ) -> List[dict]:
        res = []
        for seg in self:
            if seg.type == "text":
                res.append(
                    {"elementType": 1, "textElement": {"content": seg.data["text"]}}
                )
            elif seg.type == "at":
                res.append(
                    {
                        "elementType": 1,
                        "textElement": {"atType": 2, "atNtUin": seg.data["user_id"]},
                    }
                )
            elif seg.type == "at_all":
                res.append({"elementType": 1, "textElement": {"atType": 1}})
            elif seg.type == "image":
                data = (
                    seg.data["file"]
                    if seg.data.get("file")
                    else await _handle_image(adapter, seg.data, chat_type, peer_uin)
                )
                resp: dict = json.loads(
                    (
                        await adapter.request(
                            Request(
                                "POST",
                                adapter.api_base / "upload",
                                headers={
                                    "Authorization":
                                    f"Bearer {adapter.platform_config.token}",
                                },
                                files={"file_image": ("file_image", data)},
                            )
                        )
                    ).content
                )
                res.append(
                    {
                        "elementType": 2,
                        "picElement": {
                            "original": True,
                            "md5HexStr": resp["md5"],
                            "picWidth": resp["imageInfo"]["width"],
                            "picHeight": resp["imageInfo"]["height"],
                            "fileSize": resp["fileSize"],
                            "sourcePath": resp["ntFilePath"],
                        },
                    }
                )
            elif seg.type == "file":
                raise NotImplementedError("Unsupported MessageSegment type: "
                                          f"{seg.type}")
            elif seg.type == "voice":
                raise NotImplementedError("Unsupported MessageSegment type: "
                                          f"{seg.type}")
            elif seg.type == "video":
                raise NotImplementedError("Unsupported MessageSegment type: "
                                          f"{seg.type}")
            elif seg.type == "face":
                res.append(
                    {
                        "elementType": 6,
                        "faceElement": {"faceIndex": seg.data["face_id"]},
                    }
                )
            elif seg.type == "reply":
                res.append(
                    {
                        "elementType": 7,
                        "replyElement": {
                            "sourceMsgIdInRecords": seg.data["msg_id"],
                            "replayMsgSeq": seg.data["msg_seq"],
                            "senderUid": seg.data["sender_uid"],
                        },
                    }
                )
            elif seg.type == "ark":
                res.append(
                    {"elementType": 10, "arkElement": {"bytesData": seg.data["data"]}}
                )
            elif seg.type == "market_face":
                raise NotImplementedError("Unsupported MessageSegment type: "
                                          f"{seg.type}")
            elif seg.type == "forward_msg":
                raise NotImplementedError("Unsupported MessageSegment type: "
                                          f"{seg.type}")
        return res
