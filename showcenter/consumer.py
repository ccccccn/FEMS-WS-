# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: consumer.py
 @DateTime: 2025-01-15 16:07
 @SoftWare: PyCharm
"""
import asyncio
import json
import re
import time
from random import random
from urllib.parse import parse_qs
from venv import logger

import aioredis
import redis
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels_redis.core import RedisChannelLayer

from taosPro import settings

TIMEOUT = 1


def notify_clients_of_reconnect():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "show_center",  # 替换为你的 group name
    )


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            param_qs = parse_qs(self.scope['query_string'].decode('utf-8'))
            self.groups = param_qs.get('group', ['default_group'])[0]
            # 验证组名是否符合要求
            if not self.is_valid_group_name(self.groups):
                raise ValueError("Invalid group name")

            self.group_name = self.groups
            print(f"Group Name: {self.group_name}")
            # 如果 channel_layer 为 None，则不应该调用 group_add
            if self.channel_layer is not None and self.channel_name is not None:
                await self.channel_layer.group_add(self.groups, self.channel_name)
                print(f"Channel Layer: {self.channel_layer}")
                print(f"Channel Name: {self.channel_name}")
                await self.accept()
                await asyncio.create_task(self.listen_to_redis(self.groups))
            else:
                # 如果 channel_layer 为 None，则进行调试输出
                print("Error: channel_layer or channel_name is None")
                await self.close()
        except Exception as e:
            logger.info("Ws: connect error: {}".format(e))
            pass
    def is_valid_group_name(self, group_name):
        # 验证组名是否符合 Channels 的要求
        return re.match(r'^[a-zA-Z0-9_.-]{1,100}$', group_name) is not None

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.groups,
            self.channel_name
        )
        print(f"连接关闭")
        # 连接关闭时调用的方法
        pass

    async def receive(self, text_data):
        try:
            # 解析前端发送的 JSON 数据
            data = json.loads(text_data)
            message_type = data.get("type")
            payload = data.get("payload", {})

            # 根据消息类型处理数据
            if message_type == "text":
                await self.handle_text_message(data["content"])
            elif message_type == "fetch_data":
                await self.handle_fetch_data(payload)
            elif message_type == "submit_form":
                await self.handle_submit_form(payload)
            else:
                await self.send(text_data=json.dumps({
                    "error": "Unknown message type"
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON format"
            }))

    async def handle_text_message(self, content):
        await self.send(text_data=json.dumps({
            "type": "text",
            "content": f"Server received: {content}"
        }))

    async def handle_fetch_data(self, payload):
        user_id = payload.get("user_id")
        query = payload.get("query")
        # 处理数据请求逻辑
        response = {
            "type": "data_response",
            "data": {
                "user_id": user_id,
                "result": "some_data"
            }
        }
        await self.send(text_data=json.dumps(response))

    async def handle_submit_form(self, payload):
        name = payload.get("name")
        email = payload.get("email")
        # 处理表单提交逻辑
        await self.send(text_data=json.dumps({
            "type": "form_response",
            "message": "Form submitted successfully"
        }))

    async def send_data_to_client(self, data):
        await self.send(text_data=json.dumps(data))

    async def listen_to_redis(self, channel):
        redis = await aioredis.from_url("redis://localhost")
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message['type'] == 'subscribe':
                    continue

                try:
                    msg = json.loads(message['data'])
                    # print(f"Received message: {msg}")
                except json.JSONDecodeError:
                    msg = {"error": "Invalid JSON format"}
                except Exception as e:
                    print(f"Error processing message: {e}")

                await self.send_data_to_client(msg)
        except Exception as e:
            print(f"Error listening to Redis: {e}")
        # finally:
        #     await pubsub.unsubscribe('show_center')
        #     await redis.close()

    async def send_reconnect_message(self, event):
        print("我重连啦！")
        await self.send(text_data=json.dumps({"type": "reconnect"}))
