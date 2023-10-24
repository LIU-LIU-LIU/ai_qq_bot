import base64
from bot import _log, register_command, BotAPI, Message
from mcstatus import JavaServer
from mcstatus import BedrockServer

server = JavaServer.lookup("ahaly.cc:25565")
mc_je_status = server.status()
motd = mc_je_status.motd.to_minecraft()  # 去掉格式化字符
decoded_icon = base64.b64decode(mc_je_status.icon.removeprefix("data:image/png;base64,"))
with open("./server-icon.png", "wb") as f:
    f.write(decoded_icon)

server = BedrockServer.lookup("ahaly.cc:19132")
mc_be_status = server.status()

@register_command("status")
async def status(api: BotAPI, message: Message, params=None):
    params = f"JE服务器信息：\n玩家: {mc_je_status.players.online}\n延迟: {mc_je_status.latency}\nJE版本: {mc_je_status.version.name}\nBE版本: {mc_be_status.version.name}\n服务器信息:\n {motd}"
    _log.info(f"回复消息: {params}")
    await message.reply(file_image="./server-icon.png", content=params)
    return True