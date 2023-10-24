import openai
import botpy
import logging
import asyncio

from botpy.message import Message
from botpy import BotAPI
from collections import deque

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
    # 初始化类变量，用于存储用户对话历史
    def __init__(self, **kwargs):
        self.openai_model = kwargs.pop("openai_model", "gpt-3.5-turbo")
        openai_system_prompt = kwargs.pop("openai_system_prompt", "你是一个运行在QQ频道的机器人，用于解答各种问题。!")
        history_length = kwargs.pop("history", 10)  # 默认历史长度为10
        self.user_dialogues = deque(maxlen=history_length)
        self.user_dialogues.append({"role": "system", "content": openai_system_prompt})
        super().__init__(**kwargs)

    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")
        pass

    async def handle_message(self, message: Message):
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

    async def on_message_create(self, message: Message):
        await self.handle_message(message)

    async def on_at_message_create(self, message: Message):
        await self.handle_message(message)


    # 添加对话历史函数
    def add_dialogue(self, user_message, gpt_response):
        self.user_dialogues.append({"role": "user", "content": user_message})
        self.user_dialogues.append({"role": "assistant", "content": gpt_response})

    # 获取对话历史函数
    def get_dialogues(self):
        return list(self.user_dialogues)

    async def reply_with_gpt(self, api, message):
        user_question = message.content

        # 调用 OpenAI GPT
        openai_response = openai.ChatCompletion.create(
            model=self.openai_model,
            messages=self.get_dialogues() + [{"role": "user", "content": user_question}]
        )

        gpt_response = openai_response.choices[0].message.content


        _log.info(f"回复消息: {gpt_response}")
        await message.reply(content=gpt_response)

        # 将用户的当前问题和 GPT 的回复加入到对话历史中
        self.add_dialogue(user_question, gpt_response)
        _log.info(f"对话历史: {self.user_dialogues}")

