from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.tl.types import Message
from config import Config


class TelegramMonitor:
    def __init__(self):
        self.client = TelegramClient(
            Config.SESSION_NAME,
            Config.TELEGRAM_API_ID,
            Config.TELEGRAM_API_HASH
        )

    async def start(self):
        """启动客户端并连接"""
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError("未登录，请先运行 python login.py 进行登录")
        me = await self.client.get_me()
        print(f"已登录: {me.first_name} (@{me.username})")

    async def stop(self):
        """断开连接"""
        await self.client.disconnect()

    async def get_messages(self, chat_id, hours: int = 8) -> list[dict]:
        """
        获取指定群在过去 N 小时内的消息

        Args:
            chat_id: 群 ID 或 username
            hours: 获取过去多少小时的消息

        Returns:
            消息列表，每条消息包含 sender, text, time
        """
        messages = []
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        async for msg in self.client.iter_messages(chat_id, offset_date=datetime.now(timezone.utc)):
            if msg.date < since:
                break

            if not isinstance(msg, Message) or not msg.text:
                continue

            sender_name = "Unknown"
            sender_username = ""
            if msg.sender:
                if hasattr(msg.sender, 'first_name'):
                    sender_name = msg.sender.first_name or ""
                    if hasattr(msg.sender, 'last_name') and msg.sender.last_name:
                        sender_name += f" {msg.sender.last_name}"
                elif hasattr(msg.sender, 'title'):
                    sender_name = msg.sender.title
                if hasattr(msg.sender, 'username') and msg.sender.username:
                    sender_username = msg.sender.username

            messages.append({
                "sender": sender_name.strip(),
                "username": sender_username,
                "text": msg.text,
                "time": msg.date.strftime("%Y-%m-%d %H:%M:%S")
            })

        # 按时间正序排列
        messages.reverse()
        return messages

    async def get_chat_title(self, chat_id) -> str:
        """获取群名称"""
        try:
            entity = await self.client.get_entity(chat_id)
            return getattr(entity, 'title', str(chat_id))
        except Exception:
            return str(chat_id)

    async def send_message(self, chat_id, text: str):
        """发送消息到指定聊天"""
        # Telegram 消息长度限制为 4096 字符
        max_length = 4000

        if len(text) <= max_length:
            await self.client.send_message(chat_id, text)
        else:
            # 分段发送
            parts = []
            current = ""
            for line in text.split("\n"):
                if len(current) + len(line) + 1 > max_length:
                    parts.append(current)
                    current = line
                else:
                    current = current + "\n" + line if current else line
            if current:
                parts.append(current)

            for i, part in enumerate(parts):
                if i > 0:
                    part = f"(续 {i+1}/{len(parts)})\n\n{part}"
                await self.client.send_message(chat_id, part)
