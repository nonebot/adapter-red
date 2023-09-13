# API 列表

## send_message

依据聊天类型与目标 id 发送消息

参数:

- chat_type: 聊天类型，分为好友与群组
- target: 目标 id
- message: 发送的消息

## send_friend_message

发送好友消息

参数:

- target: 好友 id
- message: 发送的消息

## send_group_message

发送群组消息

参数:

- target: 群组 id
- message: 发送的消息

## send

依据收到的事件发送消息

参数:

- event: 收到的事件
- message: 发送的消息

## get_self_profile

获取登录账号自己的资料

## get_friends

获取登录账号所有好友的资料

## get_groups

获取登录账号所有群组的资料

## mute_member

禁言群成员

禁言时间会自动限制在 60s 至 30天内

参数:

- group: 群号
- *members: 禁言目标的 id
- duration: 禁言时间

## unmute_member

解除群成员禁言

参数:

- group: 群号
- *members: 禁言目标的 id

## mute_everyone

开启全体禁言

参数:

- group: 群号

## unmute_everyone

关闭全体禁言

参数:

- group: 群号

## kick

移除群成员

参数:

- group: 群号
- *members: 要移除的群成员账号
- refuse_forever: 是否不再接受群成员的入群申请
- reason: 移除理由

## get_announcements

拉取群公告

参数:

- group: 群号

## get_members

获取指定群组内的成员资料

参数:

- group: 群号
- size: 拉取多少个成员资料

## fetch

获取媒体消息段的二进制数据

参数:

- ms: 消息段

## fetch_media

获取媒体消息的二进制数据

**注意：此接口不推荐直接使用**

若需要获取媒体数据，你可以使用 `bot.fetch(MessageSegment)` 接口，或 `ms.download(Bot)` 接口

参数:

- msg_id: 媒体消息的消息 id
- chat_type: 媒体消息的聊天类型
- target: 媒体消息的聊天对象 id
- element_id: 媒体消息中媒体元素的 id

## upload

上传资源

**注意：此接口不推荐直接使用**

参数:

- file: 上传的资源数据

## recall_message

撤回消息

参数:

- chat_type: 聊天类型，分为好友与群组
- target: 目标 id
- *ids: 要撤回的消息 id

## recall_group_message

撤回群组消息

参数:

- target: 群组 id
- *ids: 要撤回的消息 id

## recall_friend_message

撤回好友消息

参数:

- target: 好友 id
- *ids: 要撤回的消息 id

## get_history_messages

拉取历史消息

参数:

- chat_type: 聊天类型，分为好友与群组
- target: 目标 id
- offset: 从最近一条消息算起，选择从第几条消息开始拉取
- count: 一次拉取多少消息

## send_fake_forward

发送伪造合并转发消息

参数:

- nodes: 合并转发节点
- chat_type: 聊天类型，分为好友与群组
- target: 目标 id
- source_chat_type: 伪造的消息来源聊天类型，分为好友与群组
- source_target: 伪造的消息来源聊天对象 id
