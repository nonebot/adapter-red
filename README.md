<div align="center">

# NoneBot-Adapter-Red

_✨ NoneBot2 Red Protocol适配器 / Red Protocol Adapter for NoneBot2 ✨_

</div>

## 安装

### Chronocat

请按照 [Chronocat](https://chronocat.vercel.app) 的指引安装。

## 配置

修改 NoneBot 配置文件 `.env` 或者 `.env.*`。

### Driver

参考 [driver](https://nonebot.dev/docs/appendices/config#driver) 配置项，添加 `ForwardDriver` 支持。

如：

```dotenv
DRIVER=~httpx+~websockets
DRIVER=~aiohttp
```

### RED_BOTS

配置机器人帐号，如：

```dotenv
RED_BOTS='
[
  {
    "port": "xxx",
    "token": "xxx",
    "host": "xxx"
  }
]
'
```

其中 `port` 暂时一律为 `16530`

`token` 被默认存储在 %AppData%/BetterUniverse/QQNT/RED_PROTOCOL_TOKEN 或 ~/BetterUniverse/QQNT/RED_PROTOCOL_TOKEN 中，
首次启动 Chronocat 时会自动生成，并保持不变。

`host` 为运行 QQNT 的设备主机，默认为 `localhost`。


## 功能

支持的事件：
- 群聊消息、好友消息 (能够接收到来着不同设备的自己的消息)
- 群名称改动事件
- 群成员禁言/解除禁言事件
- 群成员加入事件 (包括旧版受邀请入群)

支持的 api:
- 发送消息 (文字，at，图片，文件，表情，引用回复)
- 发送伪造合并转发 (文字，at，图片)
- 获取自身资料
- 获取好友、群组、群组内群员资料
- 获取群公告
- 禁言/解禁群员
- 全体禁言
- 获取历史消息
- 获取媒体消息的原始数据

完整的 api 文档请参考 [API 文档](api.md) 或 [QQNTRedProtocol](https://chrononeko.github.io/QQNTRedProtocol/http/)

## 示例

```python
from pathlib import Path

from nonebot import on_command
from nonebot.adapters.red import Bot
from nonebot.adapters.red.event import MessageEvent
from nonebot.adapters.red.message import MessageSegment


matcher = on_command("test")

@matcher.handle()
async def handle_receive(bot: Bot, event: MessageEvent):
    await bot.send_group_message(event.scene, MessageSegment.image(Path("path/to/img.jpg")))
```
