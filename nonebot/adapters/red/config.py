from typing import List

from yarl import URL
from pydantic import Extra, Field, BaseModel


class BotInfo(BaseModel):
    host: str = "localhost"
    port: int
    token: str

    @property
    def api_base(self):
        return URL(f"http://{self.host}:{self.port}") / "api"


class Config(BaseModel, extra=Extra.ignore):
    red_bots: List[BotInfo] = Field(default_factory=list)
