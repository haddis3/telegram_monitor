#!/usr/bin/env python3
"""
Telegram 群消息监控与总结程序

使用方法:
1. 复制 .env.example 为 .env 并填写配置
2. 运行: python main.py

命令行参数:
  --once    只执行一次总结（用于测试）
"""

import asyncio
import signal
import sys
from scheduler import MonitorScheduler


async def main():
    scheduler = MonitorScheduler()

    # 处理 Ctrl+C
    def signal_handler():
        print("\n收到停止信号...")
        asyncio.create_task(scheduler.stop())

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    # 检查是否只执行一次
    if "--once" in sys.argv:
        print("执行单次总结任务...")
        await scheduler.run_once()
    else:
        await scheduler.start()


if __name__ == "__main__":
    print("=" * 50)
    print("  Telegram 群消息监控与总结程序")
    print("=" * 50)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
