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


class FileElement(BaseModel):
    fileMd5: str
    fileName: str
    fileSize: str
    fileUuid: str


class PttElement(BaseModel):
    fileName: str
    filePath: str
    md5HexStr: str
    voiceChangeType: int
    """{0: normal, 1: magic}"""
    canConvert2Text: bool
    text: Optional[str]
    """原文中这里的`text`比其它属性多缩进了一格，请根据`canConvert2Text`来判断`text`的存在与否"""
    waveAmplitudes: Any
    fileUuid: str


class FaceElement(BaseModel):
    faceIndex: str
    faceText: Optional[str]
    """{None: normal, '/xxx': sticker, '': poke}"""
    faceType: int
    """{1: normal, 2: normal-extended, 3: sticker, 5: poke}"""
    packId: Optional[str]
    """{None: other, '1': sticker}"""
    stickerId: Optional[str]
    """{None: other, 'xxx': sticker}"""
    sourceType: Optional[int]
    """{None: other, 1: sticker}"""
    stickerType: Optional[int]
    """{None: other, 1: sticker}"""
    randomType: Optional[int]
    """{None: other, 1: sticker}"""
    pokeType: Optional[int]
    """{None: other, xxx: poke}"""
    spokeSummary: Optional[str]
    """{None: other, '': poke}"""
    doubleHit: Optional[int]
    """{None: other, xxx: poke}"""
    vaspokeId: Optional[int]
    """{None: other, xxx: poke}"""
    vaspokeName: Optional[str]
    """{None: other, 'xxx': poke}"""


class ReplyElement(BaseModel):
    replayMsgId: Optional[str]
    replayMsgSeq: str
    replyMsgTime: Optional[str]
    sourceMsgIdInRecords: str
    sourceMsgTextElems: Optional[Any]
    senderUid: Optional[str]
    senderUidStr: Optional[str]
    senderUin: Optional[str]


class ArkElement(BaseModel):
    bytesData: str
    """application/json"""


class Element(BaseModel):
    elementType: int
    elementId: Optional[str]
    extBufForUI: Optional[str]
    picElement: Optional[PicElement]
    textElement: Optional[TextElement]
    arkElement: Optional[ArkElement]
    avRecordElement: Optional[dict]
    calendarElement: Optional[dict]
    faceElement: Optional[FaceElement]
    fileElement: Optional[FileElement]
    giphyElement: Optional[dict]
    grayTipElement: Optional[dict]
    inlineKeyboardElement: Optional[dict]
    liveGiftElement: Optional[dict]
    markdownElement: Optional[dict]
    marketFaceElement: Optional[dict]
    multiForwardMsgElement: Optional[dict]
    pttElement: Optional[PttElement]
    replyElement: Optional[ReplyElement]
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
