from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    port: str = "16530"
    token: str
