import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram 配置 (默认使用 Telegram Desktop 的公开凭证)
    TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "2040"))
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "b18441a1ff607e10a989891a5462e627")

    # 智谱 API (备用)
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")

    # Claude API
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

    # 监控的群 ID 列表
    _chat_ids = os.getenv("MONITOR_CHAT_IDS", "")
    MONITOR_CHAT_IDS = [
        int(cid.strip()) if cid.strip().lstrip('-').isdigit() else cid.strip()
        for cid in _chat_ids.split(",") if cid.strip()
    ]

    # 目标 Channel
    _target = os.getenv("TARGET_CHANNEL_ID", "")
    TARGET_CHANNEL_ID = int(_target) if _target.lstrip('-').isdigit() else _target

    # 总结间隔
    SUMMARY_INTERVAL_HOURS = int(os.getenv("SUMMARY_INTERVAL_HOURS", "8"))

    # Session 文件名
    SESSION_NAME = "telegram_monitor"

    # Telegram 手机号（用于自动登录）
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")

    # 特别关注的用户 username（不带@）
    HIGHLIGHT_USERNAME = os.getenv("HIGHLIGHT_USERNAME", "").lstrip("@")

    # 该用户发言只展示在此群的总结后面
    _highlight_chat = os.getenv("HIGHLIGHT_CHAT_ID", "")
    HIGHLIGHT_CHAT_ID = int(_highlight_chat) if _highlight_chat.lstrip('-').isdigit() else _highlight_chat

    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        errors = []
        if not cls.TELEGRAM_API_ID:
            errors.append("TELEGRAM_API_ID 未设置")
        if not cls.TELEGRAM_API_HASH:
            errors.append("TELEGRAM_API_HASH 未设置")
        if not cls.CLAUDE_API_KEY:
            errors.append("CLAUDE_API_KEY 未设置")
        if not cls.MONITOR_CHAT_IDS:
            errors.append("MONITOR_CHAT_IDS 未设置")
        if not cls.TARGET_CHANNEL_ID:
            errors.append("TARGET_CHANNEL_ID 未设置")

        if errors:
            raise ValueError("配置错误:\n" + "\n".join(f"  - {e}" for e in errors))
