from enum import IntEnum
from typing import Any, List, Optional

from pydantic import BaseModel


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
    curTime: int
    duration: int
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


class FaceElement(BaseModel):
    faceIndex: int
    faceText: Optional[str]
    """{None: normal, '/xxx': sticker, '': poke}"""
    faceType: int
    """{1: normal, 2: normal-extended, 3: sticker, 5: poke}"""
    packId: Optional[Any]
    stickerId: Optional[Any]
    sourceType: Optional[Any]
    stickerType: Optional[Any]
    resultId: Optional[Any]
    surpriseId: Optional[Any]
    randomType: Optional[Any]
    imageType: Optional[Any]
    pokeType: Optional[Any]
    spokeSummary: Optional[Any]
    doubleHit: Optional[Any]
    vaspokeId: Optional[Any]
    vaspokeName: Optional[Any]
    vaspokeMinver: Optional[Any]
    pokeStrength: Optional[Any]
    msgType: Optional[Any]
    faceBubbleCount: Optional[Any]
    pokeFlag: Optional[Any]


class FileElement(BaseModel):
    fileMd5: str
    fileName: str
    filePath: str
    fileSize: str
    picHeight: Optional[int]
    picWidth: Optional[int]
    picThumbPath: Optional[Any]
    expireTime: Optional[str]
    file10MMd5: Optional[str]
    fileSha: Optional[str]
    fileSha3: Optional[str]
    videoDuration: Optional[int]
    transferStatus: Optional[int]
    progress: Optional[int]
    invalidState: Optional[int]
    fileUuid: Optional[str]
    fileSubId: Optional[str]
    thumbFileSize: Optional[int]
    fileBizId: Optional[Any]
    thumbMd5: Optional[Any]
    folderId: Optional[Any]
    fileGroupIndex: Optional[int]
    fileTransType: Optional[Any]


class PttElement(BaseModel):
    fileName: str
    filePath: str
    md5HexStr: str
    fileSize: str
    duration: int
    formatType: int
    voiceType: int
    voiceChangeType: int
    canConvert2Text: bool
    fileId: int
    fileUuid: str
    text: Optional[str]
    translateStatus: Optional[int]
    transferStatus: Optional[int]
    progress: Optional[int]
    playState: Optional[int]
    waveAmplitudes: Optional[List[int]]
    invalidState: Optional[int]
    fileSubId: Optional[str]
    fileBizId: Optional[Any]


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
    thumbPath: Optional[Any]
    transferStatus: Optional[int]
    progress: Optional[int]
    invalidState: Optional[int]
    fileUuid: Optional[str]
    fileSubId: Optional[str]
    fileBizId: Optional[Any]


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


class MsgType(IntEnum):
    normal = 2
    may_file = 3
    system = 5
    voice = 6
    video = 7
    value8 = 8
    reply = 9
    wallet = 10
    ark = 11
    may_market = 17


class Message(BaseModel):
    msgId: str
    msgRandom: str
    msgSeq: str
    cntSeq: str
    chatType: ChatType
    msgType: MsgType
    subMsgType: int
    sendType: int
    senderUid: Optional[str]
    senderUin: Optional[str]  # TODO: 等待 chronocat 0.0.43 修复
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
    avatarPendant: Optional[str]
    feedId: Optional[str]
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
    nameType: Optional[int]
    avatarFlag: Optional[int]


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


class ImageInfo(BaseModel):
    width: int
    height: int
    type: str
    mime: str
    wUnits: str
    hUnits: str


class UploadResponse(BaseModel):
    md5: str
    imageInfo: Optional[ImageInfo]
    fileSize: int
    filePath: str
    ntFilePath: str
