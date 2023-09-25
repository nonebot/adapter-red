import os
from pathlib import Path
from typing import Dict, List

from yarl import URL
from pydantic import Extra, Field, BaseModel


class BotInfo(BaseModel):
    host: str = "localhost"
    port: int
    token: str

    @property
    def api_base(self):
        return URL(f"http://{self.host}:{self.port}") / "api"


class Server(BaseModel):
    type: str
    token: str
    port: int = 16530
    enable: bool = True
    host: str = Field(default="localhost", alias="listen")


class Servers(BaseModel, extra=Extra.ignore):
    servers: List[Server] = Field(default_factory=list)
    enable: bool = True


class ChronocatConfig(Servers, extra=Extra.ignore):
    overrides: Dict[str, Servers] = Field(default_factory=dict)


class Config(BaseModel, extra=Extra.ignore):
    red_bots: List[BotInfo] = Field(default_factory=list)
    """bot 配置"""

    red_auto_detect: bool = False
    """是否自动检测 chronocat 配置，默认为 False"""


# get `home` path
home = Path(os.path.expanduser("~"))
# get `config` path
config = home / ".chronocat" / "config" / "chronocat.yml"


def get_config() -> List[BotInfo]:
    import yaml

    if not config.exists():
        return []
    with open(config, encoding="utf-8") as f:
        chrono_config = ChronocatConfig.parse_obj(yaml.safe_load(f))
    base_config = next(
        (s for s in chrono_config.servers if s.type == "red" and s.enable), None
    )
    if (
        not chrono_config.overrides
        or len(chrono_config.overrides) == 1
        and "10000" in chrono_config.overrides
    ):
        return [
            BotInfo(
                port=base_config.port, token=base_config.token, host=base_config.host
            )
        ]
    return [
        BotInfo(port=server.port, token=server.token, host=server.host)
        for servers in chrono_config.overrides.values()
        for server in servers.servers
        if servers.enable and server.type == "red" and server.enable
    ]
