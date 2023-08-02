from typing import Any, Tuple, Union
from typing_extensions import override

from nonebot.message import handle_event

from nonebot.adapters import Bot as BaseBot
from nonebot.adapters import Adapter as BaseAdapter

from .utils import log
from .config import Config
from .event import Event, MessageEvent
from .message import Message, MessageSegment


class Bot(BaseBot):
    """
    your_adapter_name 协议 Bot 适配。
    """

    @override
    def __init__(self, adapter: BaseAdapter, self_id: str, **kwargs: Any):
        super().__init__(adapter, self_id)
        self.adapter: BaseAdapter = adapter
        self.platform_config = Config.parse_obj(self.config)
        # 一些有关 Bot 的信息也可以在此定义和存储

    async def handle_event(self, event: Event):
        # 根据需要，对事件进行某些预处理，例如：
        # 检查事件是否和机器人有关操作，去除事件消息首尾的 @bot
        # 检查事件是否有回复消息，调用平台 API 获取原始消息的消息内容
        # 调用 handle_event 让 NoneBot 对事件进行处理
        # TODO: 见上
        await handle_event(self, event)

    async def get_peer_data(self, event: Event, **kwargs: Any) -> Tuple[int, str]:
        if isinstance(event, MessageEvent):
            return event.chatType, event.peerUin or event.peerUid
        return kwargs["chatType"], kwargs["peerUin"]

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs: Any,
    ) -> Any:
        # 根据平台实现 Bot 回复事件的方法

        # 将消息处理为平台所需的格式后，调用发送消息接口进行发送，例如：
        chatType, peerUin = await self.get_peer_data(event, **kwargs)
        element_data = await Message(message).export(self.adapter, chatType, peerUin)
        log("DEBUG", "Trying to send a message")
        await self.send_message(
            chatType=chatType,
            peerUin=peerUin,
            element_data=element_data,
        )
