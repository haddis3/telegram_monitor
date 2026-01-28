#!/usr/bin/env python3
"""
Telegram 登录脚本 - 手动处理登录流程
"""
import asyncio
import os
import time
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from config import Config

CODE_FILE = "/home/ubuntu/telegram-monitor/code.txt"

async def main():
    Config.validate()

    client = TelegramClient(
        Config.SESSION_NAME,
        Config.TELEGRAM_API_ID,
        Config.TELEGRAM_API_HASH
    )

    await client.connect()

    # 检查是否已登录
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"✅ 已登录: {me.first_name} (@{me.username})")
        await client.disconnect()
        return

    print(f"正在登录 Telegram...")
    print(f"手机号: {Config.TELEGRAM_PHONE}")

    # 发送验证码请求
    result = await client.send_code_request(Config.TELEGRAM_PHONE)
    phone_code_hash = result.phone_code_hash

    print(f"\n验证码已发送到您的 Telegram")
    print(f"请将验证码写入文件: {CODE_FILE}")
    print(f"例如运行: echo '12345' > {CODE_FILE}")
    print("等待验证码...")

    # 清空旧的验证码文件
    if os.path.exists(CODE_FILE):
        os.remove(CODE_FILE)

    # 等待验证码文件
    code = None
    for _ in range(120):  # 最多等待2分钟
        if os.path.exists(CODE_FILE):
            with open(CODE_FILE, 'r') as f:
                code = f.read().strip()
                if code:
                    print(f"读取到验证码: {code}")
                    os.remove(CODE_FILE)
                    break
        await asyncio.sleep(1)

    if not code:
        print("❌ 超时未收到验证码")
        await client.disconnect()
        return

    # 使用验证码登录
    try:
        await client.sign_in(Config.TELEGRAM_PHONE, code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        print("此账号启用了两步验证，需要输入密码")
        print(f"请将密码写入文件: {CODE_FILE}")

        # 等待密码文件
        password = None
        for _ in range(120):
            if os.path.exists(CODE_FILE):
                with open(CODE_FILE, 'r') as f:
                    password = f.read().strip()
                    if password:
                        print("读取到密码")
                        os.remove(CODE_FILE)
                        break
            await asyncio.sleep(1)

        if not password:
            print("❌ 超时未收到密码")
            await client.disconnect()
            return

        await client.sign_in(password=password)

    me = await client.get_me()
    print(f"\n✅ 登录成功!")
    print(f"   用户: {me.first_name} (@{me.username})")
    print(f"   Session 已保存，之后运行不需要再次登录")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
