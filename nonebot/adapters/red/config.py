from pydantic import BaseModel, Extra

class Config(BaseModel, extra=Extra.ignore):
    port: str = "16530"
    token: str