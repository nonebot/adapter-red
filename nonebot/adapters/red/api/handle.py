from typing import Any, Dict, Tuple, Callable


def _send_message(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "message/send",
        "POST",
        {
            "peer": {
                "chatType": data["chat_type"],
                "peerUin": data["target"],
                "guildId": None,
            },
            "elements": data["elements"],
        },
    )


def _get_self_profile(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return "getSelfProfile", "GET", {}


def _get_friends(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return "bot/friends", "GET", {}


def _get_groups(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return "bot/groups", "GET", {}


def _mute_member(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "group/muteMember",
        "POST",
        {
            "group": data["group"],
            "memList": [
                {"uin": i, "timeStamp": data["duration"]} for i in data["members"]
            ],
        },
    )


def _unmute_member(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "group/muteMember",
        "POST",
        {
            "group": data["group"],
            "memList": [{"uin": i, "timeStamp": 0} for i in data["members"]],
        },
    )


def _mute_everyone(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "group/muteEveryone",
        "POST",
        {"group": data["group"], "enable": True},
    )


def _unmute_everyone(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "group/muteEveryone",
        "POST",
        {"group": data["group"], "enable": False},
    )


def _kick(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "group/kick",
        "POST",
        {
            "uidList": data["members"],
            "group": data["group"],
            "refuseForever": data["refuse_forever"],
            "reason": data["reason"],
        },
    )


def _get_announcements(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return "group/getAnnouncements", "POST", {"group": data["group"]}


def _get_members(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "group/getMemberList",
        "POST",
        {"group": data["group"], "size": data["size"]},
    )


def _fetch_media(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "message/fetchRichMedia",
        "POST",
        {
            "msgId": data["msg_id"],
            "chatType": data["chat_type"],
            "peerUid": data["target"],
            "elementId": data["element_id"],
            "thumbSize": data["thumb_size"],
            "downloadType": data["download_type"],
        },
    )


def _upload(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return "upload", "POST", data["file"]


def _recall_message(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "message/recall",
        "POST",
        {
            "msgIds": data["msg_ids"],
            "peer": {
                "chatType": data["chat_type"],
                "peerUin": data["target"],
                "guildId": None,
            },
        },
    )


def _get_history_messages(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "message/getHistory",
        "POST",
        {
            "peer": {
                "chatType": data["chat_type"],
                "peerUin": data["target"],
                "guildId": None,
            },
            "offsetMsgId": data["offset_msg_id"],
            "count": data["count"],
        },
    )


def _send_fake_forward(data: Dict[str, Any]) -> Tuple[str, str, dict]:
    return (
        "message/unsafeSendForward",
        "POST",
        {
            "dstContact": {
                "chatType": data["chat_type"],
                "peerUin": data["target"],
                "guildId": None,
            },
            "srcContact": {
                "chatType": data["source_chat_type"],
                "peerUin": data["source_target"],
                "guildId": None,
            },
            "msgElements": data["elements"],
        },
    )


HANDLERS: Dict[str, Callable[[Dict[str, Any]], Tuple[str, str, dict]]] = {
    "send_message": _send_message,
    "get_self_profile": _get_self_profile,
    "get_friends": _get_friends,
    "get_groups": _get_groups,
    "mute_member": _mute_member,
    "unmute_member": _unmute_member,
    "mute_everyone": _mute_everyone,
    "unmute_everyone": _unmute_everyone,
    "kick": _kick,
    "get_announcements": _get_announcements,
    "get_members": _get_members,
    "fetch_media": _fetch_media,
    "upload": _upload,
    "recall_message": _recall_message,
    "get_history_messages": _get_history_messages,
    "send_fake_forward": _send_fake_forward,
}
