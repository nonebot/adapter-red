import json
import asyncio
from typing import Any, Dict, List, Union, Optional

from yarl import URL
from nonebot.typing import override
from nonebot.utils import escape_tag
from nonebot.exception import WebSocketClosed
from nonebot.drivers import Driver, Request, WebSocket, ForwardDriver

from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .config import Config, BotInfo
from .utils import log, handle_data
from .event import Event, GroupMessageEvent, PrivateMessageEvent


class Adapter(BaseAdapter):
    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        # 读取适配器所需的配置项
        self.red_config: Config = Config.parse_obj(self.config)
        self.tasks: List[asyncio.Task] = []  # 存储 ws 任务
        self.wss: Dict[int, WebSocket] = {}  # 存储 ws 连接
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
                f"Current driver {self.config.driver} "
                f"doesn't support forward connections!"
                f"{self.get_name()} Adapter need a ForwardDriver to work."
            )
        # 在 NoneBot 启动和关闭时进行相关操作
        self.driver.on_startup(self.startup)
        self.driver.on_shutdown(self.shutdown)

    @staticmethod
    def api_base(port: int) -> URL:
        return URL(f"http://localhost:{port}") / "api"

    async def startup(self) -> None:
        """定义启动时的操作，例如和平台建立连接"""
        for bot in self.red_config.red_bots:
            self.tasks.append(asyncio.create_task(self._forward_ws(bot)))

    async def shutdown(self) -> None:
        for task in self.tasks:
            if not task.done():
                task.cancel()

    async def _forward_ws(self, bot_info: BotInfo) -> None:
        bot: Optional[Bot] = None
        ws_url = f"ws://localhost:{bot_info.port}/"
        req = Request("GET", ws_url, timeout=60.0)
        while True:
            try:
                async with self.websocket(req) as ws:
                    log(
                        "DEBUG",
                        f"WebSocket Connection to "
                        f"{escape_tag(str(ws_url))} established",
                    )
                    connect_packet = {
                        "type": "meta::connect",
                        "payload": {"token": bot.token},
                    }
                    try:
                        await ws.send(json.dumps(connect_packet))
                        connect_data = json.loads(await ws.receive())

                        self_id = connect_data["payload"]["authData"]["uin"]
                        bot = Bot(self, self_id, bot_info)
                        self.bot_connect(bot)
                        log(
                            "INFO",
                            f"<y>Bot {escape_tag(self_id)}</y> connected, "
                            f"RedProtocol Version: "
                            f"{connect_data['payload']['version']}",
                        )
                        self.wss[bot_info.port] = ws
                        await self._loop(bot, ws)
                    except WebSocketClosed as e:
                        log(
                            "ERROR",
                            "<r><bg #f8bbd0>WebSocket Closed</bg #f8bbd0></r>",
                            e,
                        )
                    except Exception as e:
                        log(
                            "ERROR",
                            "<r><bg #f8bbd0>Error while process data from websocket "
                            f"{escape_tag(str(ws_url))}. "
                            f"Trying to reconnect...</bg #f8bbd0></r>",
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
                self.wss.pop(bot_info.port)
                await asyncio.sleep(3)  # 重连间隔

    async def _loop(self, bot: Bot, ws: WebSocket):
        while True:
            data = await ws.receive()
            json_data = json.loads(data)
            try:
                event = self.payload_to_event(json_data["payload"][0])
            except IndexError:
                log(
                    "WARNING",
                    "Failed to get message payload. \n" f"{data}",
                )
            else:
                asyncio.create_task(bot.handle_event(event))

    @classmethod
    def parse_obj(cls, obj: dict):
        chat_type_parser = {
            1: PrivateMessageEvent.parse_obj,
            2: GroupMessageEvent.parse_obj,
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
            log("WARNING", f"Parse event error {e!r}: {payload}")
            # 也可以尝试转为基础 Event 进行处理
            return Event.parse_obj(payload)

    @override
    async def _call_api(
        self, bot: Bot, api: str, **data: Any
    ) -> Optional[Union[dict, bytes]]:
        log("DEBUG", f"Calling API <y>{api}</y>")  # 给予日志提示
        api, method, platform_data = handle_data(api, **data)
        if api == "send_message":
            ws = self.wss[bot.info.port]

            # 以后red实现端支持send的http api了就删（
            await ws.send(json.dumps(platform_data))
            return

        # 采用 HTTP 请求的方式，需要构造一个 Request 对象
        request = Request(
            method=method,  # 请求方法
            url=self.api_base(bot.info.port) / api,  # 接口地址
            headers={"Authorization": f"Bearer {bot.info.token}"},
            content=json.dumps(platform_data),
            data=data,
        )
        if api == "message/fetchRichMedia":
            return (await self.request(request)).content
        # 发送请求，返回结果
        return json.loads((await self.request(request)).content)
