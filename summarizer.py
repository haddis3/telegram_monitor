import anthropic
from config import Config


class Summarizer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    def summarize(self, messages: list[dict], chat_title: str) -> str:
        """
        总结消息列表

        Args:
            messages: 消息列表，每条包含 sender, text, time
            chat_title: 群名称

        Returns:
            总结文本
        """
        if not messages:
            return f"📊 **{chat_title}** 过去 8 小时内没有消息。"

        # 格式化消息
        formatted = "\n".join(
            f"[{m['time']}] {m['sender']}: {m['text']}"
            for m in messages
        )

        # 限制输入长度
        max_chars = 100000
        if len(formatted) > max_chars:
            formatted = formatted[:max_chars] + "\n...(消息过多，已截断)"

        prompt = f"""你是一个群聊消息总结助手。请对以下 Telegram 群 "{chat_title}" 的聊天记录进行总结。

要求：
1. 提取讨论的主要话题和要点
2. 列出重要的结论或决定
3. 如果有问题被提出，指出是否已解决
4. 使用中文回复，格式清晰
5. 不要列出活跃参与者

聊天记录：
{formatted}

请生成总结："""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            summary = response.content[0].text

            # 添加标题和统计
            header = f"📊 **{chat_title}** 消息总结\n"
            header += f"📅 统计时段: 过去 8 小时\n"
            header += f"💬 消息数量: {len(messages)} 条\n"
            header += "─" * 30 + "\n\n"

            return header + summary

        except Exception as e:
            return f"❌ 总结生成失败: {str(e)}"

    def summarize_multiple(self, all_summaries: list[str]) -> str:
        """
        如果监控多个群，生成一个汇总

        Args:
            all_summaries: 各群的总结列表

        Returns:
            汇总文本
        """
        return "\n\n" + "═" * 40 + "\n\n".join(all_summaries)
