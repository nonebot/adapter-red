import asyncio
import json
import websockets
from typing import Any, Optional, Dict, Callable
from typing_extensions import override

from nonebot.drivers import Driver, Request, ForwardDriver
from nonebot.adapters import Adapter as BaseAdapter
from nonebot.adapters import Event as BaseEvent
from nonebot.exception import WebSocketClosed
from nonebot.typing import overrides
from nonebot.utils import escape_tag

from .bot import Bot
from .config import Config
from .event import Event, GroupMessageEvent, PrivateMessageEvent
from .utils import log, handle_data

class Adapter(BaseAdapter):
    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        # 读取适配器所需的配置项
        self.platform_config: Config = Config.parse_obj(self.config)
        self.task: Optional[asyncio.Task] = None  # 存储 ws 任务
        self.setup()

    @classmethod
    @override
    def get_name(cls) -> str:
        """适配器名称"""
        return "RedProtocol"
    
    def setup(self) -> None:
        if not isinstance(self.driver, ForwardDriver):
            # 判断用户配置的Driver类型是否符合适配器要求，不符合时应抛出异常
            raise RuntimeError(
                f"Current driver {self.config.driver} doesn't support forward connections!"
                f"{self.get_name()} Adapter need a ForwardDriver to work."
            )
        # 在 NoneBot 启动和关闭时进行相关操作
        self.driver.on_startup(self.startup)
        self.driver.on_shutdown(self.shutdown)

    async def startup(self) -> None:
        """定义启动时的操作，例如和平台建立连接"""
        self.task = asyncio.create_task(self._forward_ws())  # 建立 ws 连接

    async def _forward_ws(self):
        bot: Optional[Bot] = None
        ws_url = f"ws://localhost:{self.platform_config.port}/"

        while True:
            try:
                ws = await websockets.connect(ws_url)
                log(
                    "DEBUG",
                    f"WebSocket Connection to {escape_tag(str(ws_url))} established",
                )
                connect_packet = {
                    "type": "meta::connect",
                    "payload": {
                        "token": self.platform_config.token
                    }
                }
                await ws.send(json.dumps(connect_packet))
                connect_data = json.loads(await ws.recv())

                self_id = connect_data['payload']['authData']['uin']
                bot = Bot(self, self_id)
                self.bot_connect(bot)

                log("INFO", f"<y>Bot {escape_tag(self_id)}</y> connected")
                while True:
                    try:
                        # 处理 websocket
                        while True:
                            data = await ws.recv()
                            json_data = json.loads(data)
                            try:
                                event = self.payload_to_event(json_data["payload"][0])
                            except IndexError:
                                log(
                                    "WARNING",
                                    "Failed to get message payload. \n"
                                    f"{data}"
                                )
                            asyncio.create_task(bot.handle_event(event))
                    except WebSocketClosed as e:
                        log(
                            "ERROR",
                            "<r><bg #f8bbd0>WebSocket Closed</bg #f8bbd0></r>",
                            e,
                        )
                    except Exception as e:
                        log(
                            "ERROR",
                            "<r><bg #f8bbd0>Error while process data from "
                            f"websocket {ws_url}. "
                            "Trying to reconnect...</bg #f8bbd0></r>",
                            e,
                        )
                    finally:
                        self.bot_disconnect(bot)
            except Exception as e:
                # 尝试重连
                log(
                    "ERROR",
                    "<r><bg #f8bbd0>Error while setup websocket to "
                    f"{ws_url}. Trying to reconnect...</bg #f8bbd0></r>",
                    e,
                )
                await asyncio.sleep(3)  # 重连间隔

    async def shutdown(self) -> None:
        """定义关闭时的操作，例如停止任务、断开连接"""
        # 断开 ws 连接
        if self.task is not None and not self.task.done():
            self.task.cancel()

    @classmethod
    def parse_obj(cls, obj: dict):
        chat_type_parser = {
            1: PrivateMessageEvent.parse_obj,
            2: GroupMessageEvent.parse_obj
        }

        try:
            parse_func = chat_type_parser.get(obj["chatType"], Event.parse_obj)
        except KeyError:
            parse_func = Event.parse_obj

        return parse_func(obj)

    @classmethod
    def payload_to_event(cls, payload: Dict[str, Any]) -> Event:
        """根据平台事件的特性，转换平台 payload 为具体 Event


        Event 模型继承自 pydantic.BaseModel，具体请参考 pydantic 文档
        """


        # 做一层异常处理，以应对平台事件数据的变更
        try:
            return cls.parse_obj(payload)
        except Exception as e:
            # 无法正常解析为具体 Event 时，给出日志提示
            log(
                "WARNING",
                f"Parse event error: {str(payload)}",
            )
            # 也可以尝试转为基础 Event 进行处理
            return BaseEvent.parse_obj(payload)

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        log("DEBUG", f"Calling API <y>{api}</y>")  # 给予日志提示
        method, platform_data = handle_data(data)

        # 采用 HTTP 请求的方式，需要构造一个 Request 对象
        request = Request(
            method=method,  # 请求方法
            url=f"http://localhost:{self.platform_config.port}/api/{api}",  # 接口地址
            headers={'Authorization': f'Bearer {self.platform_config.token}'},  # 请求头，通常需要包含鉴权信息
            content=json.dumps(platform_data),
            data=data,
        )
        # 发送请求，返回结果
        return await self.driver.request(request)
    