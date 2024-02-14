from enum import IntEnum
from datetime import datetime
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
    uid: Optional[str] = None
    name: Optional[str] = None
    uin: Optional[str] = None


class MemberAdd(BaseModel):
    showType: int
    otherAdd: Optional[OtherAdd] = None
    otherAddByOtherQRCode: Optional[Any] = None
    otherAddByYourQRCode: Optional[Any] = None
    youAddByOtherQRCode: Optional[Any] = None
    otherInviteOther: Optional[Any] = None
    otherInviteYou: Optional[Any] = None
    youInviteOther: Optional[Any] = None


class ShutUpTarget(BaseModel):
    uid: str = "undefined"
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
    groupName: Optional[str] = None
    memberUid: Optional[str] = None
    memberNick: Optional[str] = None
    memberRemark: Optional[str] = None
    adminUid: Optional[str] = None
    adminNick: Optional[str] = None
    adminRemark: Optional[str] = None
    createGroup: Optional[Any] = None
    memberAdd: Optional[MemberAdd] = None
    shutUp: Optional[ShutUp] = None
    memberUin: Optional[str] = None
    adminUin: Optional[str] = None


class XmlElement(BaseModel):
    busiType: Optional[str] = None
    busiId: Optional[str] = None
    c2cType: int
    serviceType: int
    ctrlFlag: int
    content: Optional[str] = None
    templId: Optional[str] = None
    seqId: Optional[str] = None
    templParam: Optional[Any] = None
    pbReserv: Optional[str] = None
    members: Optional[Any] = None


class TextElement(BaseModel):
    content: str
    atType: Optional[int] = None
    atUid: Optional[str] = None
    atTinyId: Optional[str] = None
    atNtUid: Optional[str] = None
    atNtUin: Optional[str] = None
    subElementType: Optional[int] = None
    atChannelId: Optional[str] = None
    atRoleId: Optional[str] = None
    atRoleColor: Optional[str] = None
    atRoleName: Optional[str] = None
    needNotify: Optional[str] = None


class PicElement(BaseModel):
    picSubType: Optional[int] = None
    fileName: str
    fileSize: str
    picWidth: Optional[int] = None
    picHeight: Optional[int] = None
    original: Optional[bool] = None
    md5HexStr: str
    sourcePath: str
    thumbPath: Optional[Any] = None
    transferStatus: Optional[int] = None
    progress: Optional[int] = None
    picType: Optional[int] = None
    invalidState: Optional[int] = None
    fileUuid: Optional[str] = None
    fileSubId: Optional[str] = None
    thumbFileSize: Optional[int] = None
    summary: Optional[str] = None
    emojiAd: Optional[EmojiAd] = None
    emojiMall: Optional[EmojiMall] = None
    emojiZplan: Optional[EmojiZplan] = None


class FaceElement(BaseModel):
    faceIndex: int
    faceText: Optional[str] = None
    """{None: normal, '/xxx': sticker, '': poke}"""
    faceType: int
    """{1: normal, 2: normal-extended, 3: sticker, 5: poke}"""
    packId: Optional[Any] = None
    stickerId: Optional[Any] = None
    sourceType: Optional[Any] = None
    stickerType: Optional[Any] = None
    resultId: Optional[Any] = None
    surpriseId: Optional[Any] = None
    randomType: Optional[Any] = None
    imageType: Optional[Any] = None
    pokeType: Optional[Any] = None
    spokeSummary: Optional[Any] = None
    doubleHit: Optional[Any] = None
    vaspokeId: Optional[Any] = None
    vaspokeName: Optional[Any] = None
    vaspokeMinver: Optional[Any] = None
    pokeStrength: Optional[Any] = None
    msgType: Optional[Any] = None
    faceBubbleCount: Optional[Any] = None
    pokeFlag: Optional[Any] = None


class FileElement(BaseModel):
    fileMd5: str
    fileName: str
    filePath: str
    fileSize: str
    picHeight: Optional[int] = None
    picWidth: Optional[int] = None
    picThumbPath: Optional[Any] = None
    expireTime: Optional[str] = None
    file10MMd5: Optional[str] = None
    fileSha: Optional[str] = None
    fileSha3: Optional[str] = None
    videoDuration: Optional[int] = None
    transferStatus: Optional[int] = None
    progress: Optional[int] = None
    invalidState: Optional[int] = None
    fileUuid: Optional[str] = None
    fileSubId: Optional[str] = None
    thumbFileSize: Optional[int] = None
    fileBizId: Optional[Any] = None
    thumbMd5: Optional[Any] = None
    folderId: Optional[Any] = None
    fileGroupIndex: Optional[int] = None
    fileTransType: Optional[Any] = None


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
    text: Optional[str] = None
    translateStatus: Optional[int] = None
    transferStatus: Optional[int] = None
    progress: Optional[int] = None
    playState: Optional[int] = None
    waveAmplitudes: Optional[List[int]] = None
    invalidState: Optional[int] = None
    fileSubId: Optional[str] = None
    fileBizId: Optional[Any] = None


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
    thumbPath: Optional[Any] = None
    transferStatus: Optional[int] = None
    progress: Optional[int] = None
    invalidState: Optional[int] = None
    fileUuid: Optional[str] = None
    fileSubId: Optional[str] = None
    fileBizId: Optional[Any] = None


class ReplyElement(BaseModel):
    replayMsgId: Optional[str] = None
    replayMsgSeq: str
    replyMsgTime: Optional[str] = None
    sourceMsgIdInRecords: str
    sourceMsgTextElems: Optional[Any] = None
    senderUid: Optional[str] = None
    senderUidStr: Optional[str] = None
    senderUin: Optional[str] = None


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
    subElementType: Optional[int] = None
    revokeElement: Optional[dict] = None
    proclamationElement: Optional[dict] = None
    emojiReplyElement: Optional[dict] = None
    groupElement: Optional[GroupElement] = None
    buddyElement: Optional[dict] = None
    feedMsgElement: Optional[dict] = None
    essenceElement: Optional[dict] = None
    groupNotifyElement: Optional[dict] = None
    buddyNotifyElement: Optional[dict] = None
    xmlElement: Optional[XmlElement] = None
    fileReceiptElement: Optional[dict] = None
    localGrayTipElement: Optional[dict] = None
    blockGrayTipElement: Optional[dict] = None
    aioOpGrayTipElement: Optional[dict] = None
    jsonGrayTipElement: Optional[dict] = None


class Element(BaseModel):
    elementType: int
    elementId: Optional[str] = None
    extBufForUI: Optional[str] = None
    picElement: Optional[PicElement] = None
    textElement: Optional[TextElement] = None
    arkElement: Optional[ArkElement] = None
    avRecordElement: Optional[dict] = None
    calendarElement: Optional[dict] = None
    faceElement: Optional[FaceElement] = None
    fileElement: Optional[FileElement] = None
    giphyElement: Optional[dict] = None
    grayTipElement: Optional[GrayTipElement] = None
    inlineKeyboardElement: Optional[dict] = None
    liveGiftElement: Optional[dict] = None
    markdownElement: Optional[dict] = None
    marketFaceElement: Optional[MarketFaceElement] = None
    multiForwardMsgElement: Optional[MultiForwardMsgElement] = None
    pttElement: Optional[PttElement] = None
    replyElement: Optional[ReplyElement] = None
    structLongMsgElement: Optional[dict] = None
    textGiftElement: Optional[dict] = None
    videoElement: Optional[VideoElement] = None
    walletElement: Optional[dict] = None
    yoloGameResultElement: Optional[dict] = None


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
    senderUid: str = "undefined"
    senderUin: str = "-1"
    peerUid: str = "undefined"
    peerUin: str = "-1"
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
    records: List["Message"]
    emojiLikesList: List[Any]
    commentCnt: str
    directMsgFlag: int
    directMsgMembers: List[Any]
    peerName: str
    editable: bool
    avatarMeta: str
    avatarPendant: Optional[str] = None
    feedId: Optional[str] = None
    roleId: str
    timeStamp: str
    isImportMsg: bool
    atType: int
    roleType: Optional[int] = None
    fromChannelRoleInfo: RoleInfo
    fromGuildRoleInfo: RoleInfo
    levelRoleInfo: RoleInfo
    recallTime: str
    isOnlineMsg: bool
    generalFlags: str
    clientSeq: str
    nameType: Optional[int] = None
    avatarFlag: Optional[int] = None

    @property
    def time(self):
        return datetime.fromtimestamp(int(self.msgTime))


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
    extStatus: Optional[int] = None
    categoryId: int
    onlyChat: bool
    qzoneNotWatch: bool
    qzoneNotWatched: bool
    vipFlag: Optional[bool] = None
    yearVipFlag: Optional[bool] = None
    svipFlag: Optional[bool] = None
    vipLevel: Optional[int] = None


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
    type: Optional[str] = None
    mime: Optional[str] = None
    wUnits: Optional[str] = None
    hUnits: Optional[str] = None


class UploadResponse(BaseModel):
    md5: str
    imageInfo: Optional[ImageInfo] = None
    fileSize: int
    filePath: str
    ntFilePath: str
