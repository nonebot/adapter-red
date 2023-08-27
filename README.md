<div align="center">

# NoneBot-Adapter-Red

_✨ NoneBot2 Red Protocol适配器 / Red Protocol Adapter for NoneBot2 ✨_

</div>

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
    "token": "xxx"
  }
]
'
```