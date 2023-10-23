import asyncio
import os
import botpy
import logging
import openai

from botpy.ext.cog_yaml import read
from botpy.message import Message
from botpy import BotAPI

# 移除之前的所有处理器
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# 设置日志的基本配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler("logfile.log")  # 输出到日志文件
    ]
)

_log = logging.getLogger(__name__)
test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

# 创建一个字典来存储已注册的命令和对应的处理函数
commands = {}

def register_command(command_name):
    # 使用装饰器来注册命令
    def decorator(func):
        async def command_handler(api: BotAPI, message: Message, params=None):
            await func(api, message, params)
        commands[command_name] = command_handler
        return command_handler
    return decorator

@register_command("ping")
async def ping(api: BotAPI, message: Message, params=None):
    params="pong"
    _log.info(f"回复消息: {params}")
    # 第一种用reply发送消息
    await message.reply(content=params)
    return True
	
@register_command("status")
async def status(api: BotAPI, message: Message, params=None):
    params="status"
    _log.info(f"回复消息: {params}")
    # 第一种用reply发送消息
    await message.reply(content=params)
    return True

class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    #全局消息
    #async def on_message_create(self, message: Message):
    async def on_at_message_create(self, message: Message):
        _log.info(f"收到消息: {message.content}")
        # 检查消息是否包含已注册的命令
        command_found = False
        for command_name, command_handler in commands.items():
            if command_name in message.content:
                await command_handler(api=self.api, message=message)
                command_found = True
                break

        # 如果消息不包含已注册的命令，使用 OpenAI GPT 生成回复
        if not command_found:
            await self.reply_with_gpt(api=self.api, message=message)

    async def reply_with_gpt(self, api, message):
        # 获取用户发送的问题
        user_question = message.content
    
        # 使用chat模型需要创建包含系统消息和用户消息的消息列表
        messages = [
            {"role": "system", "content": test_config["openai_system"]},
            {"role": "user", "content": user_question}
        ]
    
        # 调用 OpenAI GPT 来生成回复
        openai_response = openai.ChatCompletion.create(
            model=test_config["model"],
            messages=messages
        )
    
        # 从 OpenAI 响应中提取回复内容
        gpt_response = openai_response.choices[0].message.content
    
        # 回复用户
        _log.info(f"回复消息: {gpt_response}")
        await message.reply(content=gpt_response)


if __name__ == "__main__":
    openai.api_base =test_config["openai_api_base"]
    openai.api_key =test_config["openai_api_key"]
	
    # 通过kwargs，设置需要监听的事件通道
	#发送消息事件，代表频道内的全部消息仅 私域 机器人能够设置此
    #intents = botpy.Intents(guild_messages=True)
    #当收到@机器人的消息时
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], token=test_config["token"])