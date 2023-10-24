from bot import _log, register_command, BotAPI, Message

@register_command("ping")
async def ping(api: BotAPI, message: Message, params=None):
    params="pong"
    _log.info(f"回复消息: {params}")
    # 第一种用reply发送消息
    await message.reply(content=params)
    return True