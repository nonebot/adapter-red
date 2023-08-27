from typing import List

from pydantic import Extra, Field, BaseModel


class BotInfo(BaseModel):
    port: int
    token: str


class Config(BaseModel, extra=Extra.ignore):
    red_bots: List[BotInfo] = Field(default_factory=list)
