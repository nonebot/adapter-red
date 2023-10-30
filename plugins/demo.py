from nonebot import on_command
from nonebot.adapters.red import Bot
from nonebot.adapters.red.message import Message, ForwardNode, MessageSegment
from nonebot.adapters.red.event import MessageEvent
from pathlib import Path
import asyncio

matcher = on_command("test")

@matcher.handle()
async def handle_first_receive(bot: Bot, event: MessageEvent):
    # print(await bot.get_friends())
    # print(await bot.get_groups())

    msg = await bot.send_group_message(
        event.peerUin, Message(
            [
                MessageSegment.reply(event.msgSeq, event.msgId, event.senderUin),
                MessageSegment.image(Path("C:\\Users\\TR\\Pictures\\QQ图片20210814001401.jpg"))]))
    await asyncio.sleep(5)
    await bot.recall_message(event.chatType, event.peerUin, msg.msgId)
    # await bot.send_fake_forward(
    #     [
    #         ForwardNode(
    #             event.senderUid,
    #             event.sendNickName,
    #             event.peerUin,
    #             Message("hello")
    #         )
    #     ],
    #     event.chatType,
    #     event.peerUin,
    # )
