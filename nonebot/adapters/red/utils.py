import struct
from typing import Any, Tuple

from nonebot.utils import logger_wrapper

log = logger_wrapper("red")


def handle_data(api: str, **data: Any) -> Tuple[str, str, Any]:
    if api == "send_message":
        return (
            api,
            "POST",
            {
                "type": "message::send",
                "payload": {
                    "peer": {
                        "chatType": data["chat_type"],
                        "peerUin": data["target"],
                        "guildId": None,
                    },
                    "elements": data["elements"],
                },
            },
        )
    if api == "get_self_profile":
        return "getSelfProfile", "GET", {}
    if api == "get_friends":
        return "bot/friends", "GET", {}
    if api == "get_groups":
        return "bot/groups", "GET", {}
    if api == "mute_everyone":
        return (
            "group/muteEveryone",
            "POST",
            {"group": data["group"], "enable": data["enable"]},
        )
    if api == "kick":
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
    if api == "get_announcements":
        return "group/getAnnouncements", "POST", {"group": data["group"]}
    if api == "get_members":
        return (
            "group/getMemberList",
            "POST",
            {"group": data["group"], "size": data["size"]},
        )
    if api == "fetch_media":
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
    if api == "upload":
        return "upload", "POST", data["file"]
    if api == "recall_message":
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
    if api == "get_history_messages":
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
    raise NotImplementedError(f"API {api} not implemented")


def is_amr(data: bytes) -> bool:
    amr_nb_header = b"#!AMR\n"
    amr_wb_header = b"#!AMR-WB\n"
    header = struct.unpack("6s", data[:6])[0]
    return header in [amr_nb_header, amr_wb_header]
