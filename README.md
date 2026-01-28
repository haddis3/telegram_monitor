# Telegram 群消息监控与总结

自动监控 Telegram 群聊消息，使用 Claude AI 生成智能总结，并定时推送到指定 Channel。

## 功能特性

- 监控多个 Telegram 群的聊天消息
- 使用 Claude API 智能总结聊天内容
- 定时自动执行（默认每 8 小时）
- 总结自动发送到指定 Telegram Channel
- 支持两步验证登录

## 安装

```bash
# 克隆仓库
git clone https://github.com/haddis3/telegram_monitor.git
cd telegram_monitor

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 配置

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填写以下配置：

```bash
# Telegram 手机号（用于登录）
TELEGRAM_PHONE=+86xxxxxxxxxxx

# Claude API Key（从 https://console.anthropic.com 获取）
CLAUDE_API_KEY=your_claude_api_key

# 监控的群 ID（多个用逗号分隔）
MONITOR_CHAT_IDS=-1001234567890

# 总结发送到的 Channel ID
TARGET_CHANNEL_ID=@your_channel

# 总结间隔（小时）
SUMMARY_INTERVAL_HOURS=8
```

### 获取群/Channel ID

1. 将 [@userinfobot](https://t.me/userinfobot) 添加到群或 Channel
2. 转发一条消息给它，即可获取 ID

## 使用

### 首次登录

```bash
python login.py
```

验证码会发送到你的 Telegram，将验证码写入 `code.txt` 文件：

```bash
echo '12345' > code.txt
```

如果启用了两步验证，同样将密码写入 `code.txt`。

### 启动监控

```bash
python main.py
```

程序将自动按设定的间隔执行总结任务。

### 单次执行（测试用）

```bash
python main.py --once
```

### 后台运行

```bash
nohup python main.py > monitor.log 2>&1 &
```

## 项目结构

```
├── main.py           # 主入口
├── login.py          # Telegram 登录脚本
├── config.py         # 配置管理
├── telegram_client.py # Telegram 客户端封装
├── summarizer.py     # Claude AI 总结模块
├── scheduler.py      # 定时任务调度
├── requirements.txt  # Python 依赖
└── .env.example      # 环境变量模板
```

## 依赖

- Python 3.10+
- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram 客户端库
- [Anthropic](https://github.com/anthropics/anthropic-sdk-python) - Claude API SDK
- [APScheduler](https://github.com/agronholm/apscheduler) - 定时任务

## License

MIT
