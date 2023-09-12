from typing import Any, List, Optional

from pydantic import BaseModel

from enum import IntEnum


class ChatType(IntEnum):
    FRIEND = 1
    GROUP = 2


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


class OtherAdd(BaseModel):
    uid: Optional[str]
    name: Optional[str]
    uin: Optional[str]

class MemberAdd(BaseModel):
    showType: int
    otherAdd: Optional[OtherAdd]
    otherAddByOtherQRCode: Optional[Any]
    otherAddByYourQRCode: Optional[Any]
    youAddByOtherQRCode: Optional[Any]
    otherInviteOther: Optional[Any]
    otherInviteYou: Optional[Any]
    youInviteOther: Optional[Any]

class ShutUpTarget(BaseModel):
    uid: str
    card: str
    name: str
    role: int
    uin: str

class ShutUp(BaseModel):
    curTime: str
    duration: str
    admin: ShutUpTarget
    member: ShutUpTarget


class GroupElement(BaseModel):
    type: int
    role: int
    groupName: Optional[str]
    memberUid: Optional[str]
    memberNick: Optional[str]
    memberRemark: Optional[str]
    adminUid: Optional[str]
    adminNick: Optional[str]
    adminRemark: Optional[str]
    createGroup: Optional[Any]
    memberAdd: Optional[MemberAdd]
    shutUp: Optional[ShutUp]
    memberUin: Optional[str]
    adminUin: Optional[str]


class XmlElement(BaseModel):
    busiType: Optional[str]
    busiId: Optional[str]
    c2cType: int
    serviceType: int
    ctrlFlag: int
    content: Optional[str]
    templId: Optional[str]
    seqId: Optional[str]
    templParam: Optional[Any]
    pbReserv: Optional[str]
    members: Optional[Any]


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


class MarketFaceElement(BaseModel):
    itemType: int
    faceInfo: int
    emojiPackageId: str
    subType: int
    faceName: str
    emojiId: str
    key: str
    staticFacePath: str
    dynamicFacePath: str


class MultiForwardMsgElement(BaseModel):
    xmlContent: str
    resId: str
    fileName: str


class VideoElement(BaseModel):
    filePath: str
    fileName: str
    videoMd5: str
    thumbMd5: str
    fileTime: int
    thumbSize: int
    fileFormat: int
    fileSize: str
    thumbWidth: int
    thumbHeight: int
    busiType: int
    subBusiType: int
    thumbPath: dict
    """不清楚为什么是dict，这是收到的数据: {}"""
    transferStatus: int
    progress: int
    invalidState: int
    fileUuid: str
    fileSubId: str
    fileBizId: Optional[str]


class GrayTipElement(BaseModel):
    subElementType: Optional[int]
    revokeElement: Optional[dict]
    proclamationElement: Optional[dict]
    emojiReplyElement: Optional[dict]
    groupElement: Optional[GroupElement]
    buddyElement: Optional[dict]
    feedMsgElement: Optional[dict]
    essenceElement: Optional[dict]
    groupNotifyElement: Optional[dict]
    buddyNotifyElement: Optional[dict]
    xmlElement: Optional[XmlElement]
    fileReceiptElement: Optional[dict]
    localGrayTipElement: Optional[dict]
    blockGrayTipElement: Optional[dict]
    aioOpGrayTipElement: Optional[dict]
    jsonGrayTipElement: Optional[dict]


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
    grayTipElement: Optional[GrayTipElement]
    inlineKeyboardElement: Optional[dict]
    liveGiftElement: Optional[dict]
    markdownElement: Optional[dict]
    marketFaceElement: Optional[MarketFaceElement]
    multiForwardMsgElement: Optional[MultiForwardMsgElement]
    pttElement: Optional[PttElement]
    replyElement: Optional[ReplyElement]
    structLongMsgElement: Optional[dict]
    textGiftElement: Optional[dict]
    videoElement: Optional[VideoElement]
    walletElement: Optional[dict]
    yoloGameResultElement: Optional[dict]


class Message(BaseModel):
    msgId: str
    msgRandom: str
    msgSeq: str
    cntSeq: str
    chatType: ChatType
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
    roleType: Optional[int]
    fromChannelRoleInfo: RoleInfo
    fromGuildRoleInfo: RoleInfo
    levelRoleInfo: RoleInfo
    recallTime: str
    isOnlineMsg: bool
    generalFlags: str
    clientSeq: str
    nameType: int
    avatarFlag: int


class Profile(BaseModel):
    uid: str
    qid: str
    uin: str
    nick: str
    remark: str
    longNick: str
    avatarUrl: str
    birthday_year: int
    birthday_month: int
    birthday_day: int
    sex: int
    topTime: str
    isBlock: bool
    isMsgDisturb: bool
    isSpecialCareOpen: bool
    isSpecialCareZone: bool
    ringId: str
    status: int
    extStatus: int
    categoryId: int
    onlyChat: bool
    qzoneNotWatch: bool
    qzoneNotWatched: bool
    vipFlag: bool
    yearVipFlag: bool
    svipFlag: bool
    vipLevel: int


class Member(BaseModel):
    uid: str
    qid: str
    uin: str
    nick: str
    remark: str
    cardType: int
    cardName: str
    role: int
    avatarPath: str
    shutUpTime: int
    isDelete: bool


class Group(BaseModel):
    groupCode: str
    maxMember: int
    memberCount: int
    groupName: str
    groupStatus: int
    memberRole: int
    isTop: bool
    toppedTimestamp: str
    privilegeFlag: int
    isConf: bool
    hasModifyConfGroupFace: bool
    hasModifyConfGroupName: bool
    remarkName: str
    avatarUrl: str
    hasMemo: bool
    groupShutupExpireTime: str
    personShutupExpireTime: str
    discussToGroupUin: str
    discussToGroupMaxMsgSeq: int
    discussToGroupTime: int
