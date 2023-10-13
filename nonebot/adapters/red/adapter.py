import json
import asyncio
from typing_extensions import override
from typing import Any, List, Type, Union, Optional

from nonebot.utils import escape_tag
from pydantic import ValidationError
from nonebot.drivers import Driver, Request, WebSocket, ForwardDriver
from nonebot.exception import ActionFailed, NetworkError, WebSocketClosed

from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .utils import log
from .api.model import MsgType
from .api.handle import HANDLERS
from .api.model import Message as MessageModel
from .config import Config, BotInfo, get_config
from .event import (
    Event,
    MemberAddEvent,
    MemberMuteEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
    GroupNameUpdateEvent,
)


class Adapter(BaseAdapter):
    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        # 读取适配器所需的配置项
        self.red_config: Config = Config.parse_obj(self.config)
        self._bots = self.red_config.red_bots
        if self.red_config.red_auto_detect and not self._bots:
            try:
                log("INFO", "Auto detect chronocat config...")
                self._bots = get_config()
                log("SUCCESS", f"Auto detect {len(self._bots)} bots.")
            except ImportError:
                log("ERROR", "Please install `PyYAML` to enable auto detect!")
        self.tasks: List[asyncio.Task] = []  # 存储 ws 任务
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

    async def startup(self) -> None:
        """定义启动时的操作，例如和平台建立连接"""
        if not self._bots:
            log(
                "WARNING",
                "No bots found in config! \n"
                "Please check your config file and make sure it's correct.",
            )
        for bot in self._bots:
            self.tasks.append(asyncio.create_task(self._forward_ws(bot)))

    async def shutdown(self) -> None:
        for task in self.tasks:
            if not task.done():
                task.cancel()

    async def _forward_ws(self, bot_info: BotInfo) -> None:
        bot: Optional[Bot] = None
        ws_url = f"ws://{bot_info.host}:{bot_info.port}/"
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
                        "payload": {"token": bot_info.token},
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
                            f"Chronocat Version: "
                            f"{connect_data['payload']['version']}",
                        )
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
                        if bot:
                            self.bot_disconnect(bot)
            except Exception as e:
                # 尝试重连
                log(
                    "ERROR",
                    "<r><bg #f8bbd0>"
                    "Error while setup websocket to "
                    f"{escape_tag(str(ws_url))}. Trying to reconnect..."
                    f"</bg #f8bbd0></r>",
                    e,
                )
                await asyncio.sleep(3)  # 重连间隔

    async def _loop(self, bot: Bot, ws: WebSocket):
        while True:
            data = await ws.receive()
            json_data = json.loads(data)
            _event_type = json_data["type"]
            if not json_data["payload"]:
                log("WARNING", f"received empty event {_event_type}")
                continue

            def _handle_event(event_data: Any, target: Type[Event]):
                try:
                    event = target.convert(event_data)
                except Exception as e:
                    log(
                        "WARNING",
                        f"Failed to parse event data: {event_data}",
                        e,
                    )
                else:
                    asyncio.create_task(bot.handle_event(event))

            def _handle_message(message: dict):
                try:
                    _data = MessageModel.parse_obj(message)
                except ValidationError as e:
                    log(
                        "WARNING",
                        f"Failed to parse message data: {message}",
                        e,
                    )
                    return
                if _data.msgType == MsgType.system and _data.sendType == 3:
                    if (
                        _data.subMsgType == 8
                        and _data.elements[0].elementType == 8
                        and _data.elements[0].grayTipElement
                        and _data.elements[0].grayTipElement.subElementType == 4
                        and _data.elements[0].grayTipElement.groupElement
                        and _data.elements[0].grayTipElement.groupElement.type == 1
                    ):
                        _handle_event(_data, MemberAddEvent)
                    elif (
                        _data.subMsgType == 8
                        and _data.elements[0].elementType == 8
                        and _data.elements[0].grayTipElement
                        and _data.elements[0].grayTipElement.subElementType == 4
                        and _data.elements[0].grayTipElement.groupElement
                        and _data.elements[0].grayTipElement.groupElement.type == 8
                    ):
                        _handle_event(_data, MemberMuteEvent)
                    elif (
                        _data.subMsgType == 8
                        and _data.elements[0].elementType == 8
                        and _data.elements[0].grayTipElement
                        and _data.elements[0].grayTipElement.subElementType == 4
                        and _data.elements[0].grayTipElement.groupElement
                        and _data.elements[0].grayTipElement.groupElement.type == 5
                    ):
                        _handle_event(_data, GroupNameUpdateEvent)
                    elif (
                        _data.subMsgType == 12
                        and _data.elements[0].elementType == 8
                        and _data.elements[0].grayTipElement
                        and _data.elements[0].grayTipElement.subElementType == 12
                        and _data.elements[0].grayTipElement.xmlElement
                        and _data.elements[0].grayTipElement.xmlElement.busiType == "1"
                        and _data.elements[0].grayTipElement.xmlElement.busiId
                        == "10145"
                    ):
                        _handle_event(_data, MemberAddEvent)
                    else:
                        log("WARNING", f"received unsupported event: {message}")
                        return
                else:
                    if _data.chatType == 1:
                        _handle_event(_data, PrivateMessageEvent)
                    elif _data.chatType == 2:
                        _handle_event(_data, GroupMessageEvent)
                    else:
                        log("WARNING", f"received unsupported event: {message}")
                        return

            if _event_type == "message::recv":
                for msg in json_data["payload"]:
                    _handle_message(msg)
            else:
                _handle_event(json_data["payload"], Event)

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Union[dict, bytes]:
        log("DEBUG", f"Calling API <y>{api}</y>")  # 给予日志提示
        if not (handler := HANDLERS.get(api)):
            raise NotImplementedError(f"API {api} not implemented")
        api, method, platform_data = handler(data)
        # 采用 HTTP 请求的方式，需要构造一个 Request 对象
        request = Request(
            method=method,  # 请求方法
            url=bot.info.api_base / api,  # 接口地址
            headers={"Authorization": f"Bearer {bot.info.token}"},
            content=json.dumps(platform_data),
            data=platform_data,
        )
        if api == "message/fetchRichMedia":
            return (await self.request(request)).content  # type: ignore
        # 发送请求，返回结果
        return json.loads((await self.request(request)).content)  # type: ignore

    @override
    async def request(self, setup: Request):
        try:
            resp = await super().request(setup)
        except Exception as e:
            raise NetworkError(f"Failed to request {setup.url}") from e
        if resp.status_code != 200:
            raise ActionFailed(
                self.get_name(),
                f"HTTP status code {resp.status_code} "
                f"response body: {resp.content}",
            )
        return resp
