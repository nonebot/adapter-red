from typing import Any, List, Optional

from pydantic import BaseModel


class RoleInfo(BaseModel):
    roleId: str
    name: str
    color: int


class EmojiAd(BaseModel):
    url: str
    desc: str


class EmojiMall(BaseModel):
    packageId: int
    emojiId: int


class EmojiZplan(BaseModel):
    actionId: int
    actionName: str
    actionType: int
    playerNumber: int
    peerUid: str
    bytesReserveInfo: str


class XMLElement(BaseModel):
    busiType: str
    busiId: str
    c2cType: int
    serviceType: int
    ctrlFlag: int
    content: str
    templId: str
    seqId: str
    templParam: Any
    pbReserv: str
    members: Any


class TextElement(BaseModel):
    content: str
    atType: Optional[int]
    atUid: Optional[str]
    atTinyId: Optional[str]
    atNtUid: Optional[str]
    atNtUin: Optional[str]
    subElementType: Optional[int]
    atChannelId: Optional[str]
    atRoleId: Optional[str]
    atRoleColor: Optional[str]
    atRoleName: Optional[str]
    needNotify: Optional[str]


class PicElement(BaseModel):
    picSubType: Optional[int]
    fileName: str
    fileSize: str
    picWidth: Optional[int]
    picHeight: Optional[int]
    original: Optional[bool]
    md5HexStr: str
    sourcePath: str
    thumbPath: Optional[Any]
    transferStatus: Optional[int]
    progress: Optional[int]
    picType: Optional[int]
    invalidState: Optional[int]
    fileUuid: Optional[str]
    fileSubId: Optional[str]
    thumbFileSize: Optional[int]
    summary: Optional[str]
    emojiAd: Optional[EmojiAd]
    emojiMall: Optional[EmojiMall]
    emojiZplan: Optional[EmojiZplan]


class Element(BaseModel):
    elementType: int
    elementId: Optional[str]
    extBufForUI: Optional[str]
    picElement: Optional[PicElement]
    textElement: Optional[TextElement]
    arkElement: Optional[dict]
    avRecordElement: Optional[dict]
    calendarElement: Optional[dict]
    faceElement: Optional[dict]
    fileElement: Optional[dict]
    giphyElement: Optional[dict]
    grayTipElement: Optional[dict]
    inlineKeyboardElement: Optional[dict]
    liveGiftElement: Optional[dict]
    markdownElement: Optional[dict]
    marketFaceElement: Optional[dict]
    multiForwardMsgElement: Optional[dict]
    pttElement: Optional[dict]
    replyElement: Optional[dict]
    structLongMsgElement: Optional[dict]
    textGiftElement: Optional[dict]
    videoElement: Optional[dict]
    walletElement: Optional[dict]
    yoloGameResultElement: Optional[dict]


class Message(BaseModel):
    msgId: str
    msgRandom: str
    msgSeq: str
    cntSeq: str
    chatType: int
    msgType: int
    subMsgType: int
    sendType: int
    senderUid: str
    senderUin: Optional[str]
    peerUid: str
    peerUin: Optional[str]
    channelId: str
    guildId: str
    guildCode: str
    fromUid: str
    fromAppid: str
    msgTime: str
    msgMeta: str
    sendStatus: int
    sendMemberName: str
    sendNickName: str
    guildName: str
    channelName: str
    elements: List[Element]
    records: List[Any]
    emojiLikesList: List[Any]
    commentCnt: str
    directMsgFlag: int
    directMsgMembers: List[Any]
    peerName: str
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
