# 迁移指南

## 前言

`Red Protocol` 实现的事件非常少，对于原先使用 `onebot` 协议的机器人，需要进行大量的修改。

### 为什么不推荐使用 `Chronocat`

`Chronocat` 属于 hook 框架，意味着你需要先运行一个完整的 `NTQQ` 客户端。哪怕 `Chronocat` 提供了无头模式，大幅降低了资源占用，但是其无法阻止 `NTQQ` 客户端
向存储设备写入大量的缓存数据，这对于一些资源有限的设备来说是致命的。

而由于 `Chronocat` 所依靠运行的 `LiteLoaderQQNT` 等框架的不稳定性 (`llqqnt` 受最新版 ntqq 的检测影响，至今仍未给出解决方案)，
以及 `Chronocat` 的维护者的个人原因（如学业问题），`Chronocat` 也不是一个长期可靠的解决方案。

因此，我们不推荐也不反对使用 `Chronocat`

### 官方接口

再者，若你的机器人只需要接入 `QQ`，QQ 的官方接口也即将开放，我们也推荐有能力的开发者使用官方接口进行开发。`Nonebot` 已经发布了 QQ 官方接口的适配器：[`nonebot-adapter-qq`](https://github.com/nonebot/adapter-qq)。

### 其他的 qqnt 框架

如果你不想迁移插件，仍然想使用 `onebot` 适配器，那么你可以尝试 [Shamrock](https://github.com/linxinrao/Shamrock)
「试试 Shamrock，更新积极，模拟器可用，支持 onebot，方便迁移」

如果你对需要定期清理客户端缓存感到烦恼，那么你可以尝试 NTQQ 的协议实现，如 [Lagrange](https://github.com/Linwenxuan05/Lagrange.Core)
「试试 Lagrange，NTPC 协议，新时代协议实现」


## 跨平台方案

基于不稳定因素，我们更希望开发者考虑为自己的插件使用跨平台组件，如 `nonebot-adapter-satori`，`nonebot-plugin-alconna`，
`nonebot-plugin-send-anything-anywhere` 等。

### Satori

随着 [`Satori` 适配器](https://github.com/nonebot/adapter-satori)的发布，接入 `Chronocat` 现在更推荐使用 `Satori` 适配器了。

关于 `Satori`：[介绍](https://satori.js.org/zh-CN/introduction.html)

`Satori` 与 `onebot12` 定位相同，都属于跨平台协议，并且你可以通过 satori 接入 `Koishi` (https://github.com/koishijs/koishi) 等框架。

你只需要把 `Chronocat` 的配置文件做如下修改：

```yaml
# ~/.chronocat/config/chronocat.yml
servers:
  - type: satori # <------------------------------------ 修改这里
    # Chronocat 已经自动生成了随机 token。要妥善保存哦！
    # 客户端使用服务时需要提供这个 token！
    token: DEFINE_CHRONO_TOKEN  # token
    # Chronocat 开启 red 服务的端口，默认为 5500。
    port: 5500  # port
```

便能让你的 `Chronocat` 以 `Satori` 服务的形式运行。

### Plugin-Alconna

[`Plugin-Alconna`](https://github.com/nonebot/plugin-alconna) 作为官方插件之一，是一个强大的 Nonebot2 命令匹配拓展，支持富文本/多媒体解析，跨平台消息收发。

使用文档：https://nonebot.dev/docs/next/best-practice/alconna/alconna

其支持的复杂命令结构、富文本解析，足以帮你丢弃以往的多媒体元素判断方法，而是直接通过 `on_alconna` 完成解析处理。

其实现的跨平台消息收发，也能让你丢弃对以往各平台的消息格式判断，而是直接通过 `send` 方法发送消息。

`Plugin-Alconna` 支持现在 `Nonebot2` 的所有适配器，包括 `Satori`。

示例：
```python
from nonebot_plugin_alconna import Image, Alconna, AlconnaMatcher, Args, Match, UniMessage, on_alconna

test = on_alconna(Alconna("test", Args["img?", Image]))

@test.handle()
async def handle_test(matcher: AlconnaMatcher, img: Match[Image]):
    if img.available:
        matcher.set_path_arg("img", img.result)


@test.got_path("img", prompt=UniMessage.template("{:At(user, $event.get_user_id())}\n请输入图片"))
async def handle_foo(img: Image):
    await save_image(img)
    await test.send("图片已收到")
```

### Send-Anything-Anywhere

[`Send-Anything-Anywhere`](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere) 是一个帮助处理不同 adapter 消息的适配和发送的插件。

使用文档：https://send-anything-anywhere.felinae98.cn/

saa 通过以下方式帮助你处理不同 adapter 的消息：
- 为常见的消息类型提供抽象类，自适应转换成对应 adapter 的消息
- 提供一套统一的，符合直觉的发送接口
- 为复杂的消息提供易用的生成接口（规划中）
- 通过传入 bot 的类型来自适应生成对应 bot adapter 所使用的 Message

saa 目前支持的适配器有 onebot v11/v12, QQ 官方接口/频道接口，Kook，Telegram，Feishu，以及本适配器。

示例：
```python
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from nonebot.adapters.onebot.v12.event import MessageEvent as V12MessageEvent
from nonebot.internal.adapter.bot import Bot
from nonebot_plugin_saa import Image, Text, MessageFactory

pic_matcher = nonebot.on_command('发送图片')

pic_matcher.handle()
async def _handle_v12(bot: Bot, event: Union[V12MessageEvent, V11MessageEvent]):
    pic_content = ...
    msg_builder = MessageFactory([
        Image(pic_content), Text("这是你要的图片")
    ])
    # or msg_builder = Image(pic_content) + Text("这是你要的图片")
    await msg_builder.send()
    await pic_matcher.finish()
```


## 消息事件

`Red` 下的消息事件只有两种：`PrivateMessageEvent` 和 `GroupMessageEvent`。

因为 `Red` 下事件结构比较贴合原始协议，以下字段你可能会感到陌生：
- `senderUin` / `senderUId`：发送者 QQ 号
- `peerUin` / `peerUId`：消息所在群组的群号或私聊对象的 QQ 号
- `sendNickName`: 发送者昵称
- `sendMemberName`: 发送者群名片 (假如是群消息)
- `peerName`: 群名 (假如是群消息)

当然，我们为 `MessageEvent` 提供了一些属性来帮助你更方便地获取消息内容：

```python
@property
def time(self):
    """消息发送时间"""
    return datetime.fromtimestamp(int(self.msgTime))

@property
def scene(self) -> str:
    """群组或好友的id"""
    return self.peerUin or self.peerUid

@property
def is_group(self) -> bool:
    """是否为群组消息"""
    return self.chatType == ChatType.GROUP

@property
def is_private(self) -> bool:
    """是否为私聊消息"""
    return self.chatType == ChatType.FRIEND

@property
def user_id(self) -> str:
    """好友的id"""
    return self.peerUin or self.peerUid

@property
def group_id(self) -> str:
    """群组的id"""
    return self.peerUin or self.peerUid
```

### 消息内容

`Red` 下消息支持的内容类型有：

- `Text`：文本消息
- `Image`：图片消息
- `Voice`：语音消息
- `Video`：视频消息
- `File`：文件消息
- `At`：@ 消息
- `AtAll`：@ 全体成员消息
- `Reply`：回复消息
- `Face`：表情消息
- `MarketFace`： 商店表情消息
- `Forward`：合并转发消息

其中 `market_face` 仅能接收，不能发送。

`forward` 需要通过特殊的 api 发送，不支持直接发送。

**注意：`Red` 不是 gocqhttp，不支持 `cq码`。如果你仍然在使用 `cq码`，请务必迁移使用 `MessageSegment`。**

关于消息与消息段的使用：https://nonebot.dev/docs/next/tutorial/message

## 提醒事件

`Red` 下的提醒事件有：
- `GroupNameUpdateEvent`：群名变更事件
- `MemberAddEvent`：群成员加入事件
- `MemberMuteEvent`：群成员禁言事件
  - `MemberMutedEvent`：群成员被禁言事件
  - `MemberUnmutedEvent`：群成员被解除禁言事件

### 群名变更事件

其有以下属性：
- `currentName`：当前群名
- `operatorUid`：操作者 QQ 号
- `operatorName`：操作者昵称

### 群成员加入事件

其有以下属性：
- `memberUid`：加入者 QQ 号
- `memberName`：加入者昵称
- `operatorUid`：操作者 QQ 号

### 群成员禁言事件

其有以下属性：
- `start`：禁言开始时间
- `duration`：禁言时长
- `operator`: 操作者
- `member`：被禁言者

## API

参照 [API 列表](./api.md)
