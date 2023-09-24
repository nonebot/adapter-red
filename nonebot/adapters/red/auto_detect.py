import os
from pathlib import Path
from typing import List, Literal

import yaml
from pydantic import BaseModel

from .bot import BotInfo

# get `home` path
home = Path(os.path.expanduser("~"))
# get `config` path
config = home / "chronocat.yml"


class Server(BaseModel):
    type: Literal["red", "satori"] = "red"
    token: str
    port: int = 16530


def get_config() -> List[BotInfo]:
    if not config.exists():
        return []
    with open(config, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    servers = [Server.parse_obj(server) for server in data["servers"]]
    return [
        BotInfo(port=server.port, token=server.token)
        for server in servers
        if server.type == "red"
    ]
