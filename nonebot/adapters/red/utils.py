import struct

from nonebot.utils import logger_wrapper

log = logger_wrapper("red")


def is_amr(data: bytes) -> bool:
    amr_nb_header = b"#!AMR\n"
    amr_wb_header = b"#!AMR-WB\n"
    header = struct.unpack("6s", data[:6])[0]
    return header in [amr_nb_header, amr_wb_header]
