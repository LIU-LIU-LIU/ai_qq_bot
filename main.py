import asyncio
import os
import botpy
import openai
from botpy.ext.cog_yaml import read
from bot import MyClient

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

if __name__ == "__main__":
    openai.api_base =test_config["openai_api_base"]
    openai.api_key =test_config["openai_api_key"]

    at_intents=test_config["at_intents"]
    # 通过kwargs，设置需要监听的事件通道
    if at_intents:
    #at消息
        intents = botpy.Intents(public_guild_messages=True)
    else:
    #全部消息
        intents = botpy.Intents(guild_messages=True)
    client = MyClient(
        intents=intents,
        openai_system_prompt=test_config["openai_system_prompt"],
        openai_model=test_config["openai_model"],
        history=test_config["history"]
    )
    client.run(
        appid=test_config["appid"],
        token=test_config["token"]
    )