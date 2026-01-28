import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from config import Config
from telegram_client import TelegramMonitor
from summarizer import Summarizer


class MonitorScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.telegram = TelegramMonitor()
        self.summarizer = Summarizer()
        self._running = False

    async def run_daily_checkin(self):
        """每日打卡"""
        print(f"\n[{datetime.now()}] 执行每日打卡...")
        try:
            await self.telegram.send_message(Config.TARGET_CHANNEL_ID, "🥒🐱")
            print(f"  ✅ 打卡完成")
        except Exception as e:
            print(f"  ❌ 打卡失败: {e}")

    async def run_summary_task(self):
        """执行一次总结任务"""
        print(f"\n[{datetime.now()}] 开始执行总结任务...")

        all_summaries = []

        for chat_id in Config.MONITOR_CHAT_IDS:
            try:
                print(f"  正在获取 {chat_id} 的消息...")
                chat_title = await self.telegram.get_chat_title(chat_id)
                messages = await self.telegram.get_messages(
                    chat_id,
                    hours=Config.SUMMARY_INTERVAL_HOURS
                )
                print(f"  获取到 {len(messages)} 条消息")

                print(f"  正在生成总结...")
                summary = self.summarizer.summarize(messages, chat_title)
                all_summaries.append(summary)

            except Exception as e:
                print(f"  ❌ 处理 {chat_id} 时出错: {e}")
                all_summaries.append(f"❌ 获取 {chat_id} 消息失败: {str(e)}")

        # 发送总结到目标 channel
        if all_summaries:
            final_summary = "\n\n" + "═" * 40 + "\n\n".join(all_summaries) if len(all_summaries) > 1 else all_summaries[0]
            try:
                print(f"  正在发送总结到 {Config.TARGET_CHANNEL_ID}...")
                await self.telegram.send_message(Config.TARGET_CHANNEL_ID, final_summary)
                print(f"  ✅ 总结已发送")
            except Exception as e:
                print(f"  ❌ 发送失败: {e}")

        print(f"[{datetime.now()}] 总结任务完成\n")

    async def start(self):
        """启动调度器"""
        Config.validate()

        print("正在连接 Telegram...")
        await self.telegram.start()

        # 添加总结定时任务
        self.scheduler.add_job(
            self.run_summary_task,
            trigger=IntervalTrigger(hours=Config.SUMMARY_INTERVAL_HOURS),
            id="summary_task",
            name="群消息总结",
            next_run_time=datetime.now()  # 立即执行一次
        )

        # 添加每日打卡任务（每天早上8点）
        self.scheduler.add_job(
            self.run_daily_checkin,
            trigger=CronTrigger(hour=8, minute=0),
            id="daily_checkin",
            name="每日打卡"
        )

        self.scheduler.start()
        self._running = True

        print(f"\n✅ 监控已启动")
        print(f"   监控群: {Config.MONITOR_CHAT_IDS}")
        print(f"   目标 Channel: {Config.TARGET_CHANNEL_ID}")
        print(f"   总结间隔: 每 {Config.SUMMARY_INTERVAL_HOURS} 小时")
        print(f"   每日打卡: 每天 08:00")
        print(f"\n按 Ctrl+C 停止...\n")

        # 保持运行
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def stop(self):
        """停止调度器"""
        self._running = False
        self.scheduler.shutdown()
        await self.telegram.stop()
        print("\n监控已停止")

    async def run_once(self):
        """手动执行一次总结（用于测试）"""
        Config.validate()
        await self.telegram.start()
        await self.run_summary_task()
        await self.telegram.stop()
