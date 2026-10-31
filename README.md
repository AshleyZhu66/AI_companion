# 你的 AI 伴侣（AI Companion）

一个基于 **Python + Streamlit + DeepSeek** 的 AI 智能伴侣聊天应用。你可以自定义伴侣的昵称和性格，像微信聊天一样与 TA 对话，并支持多会话的历史记录管理。

## ✨ 功能特性

- 🤖 **AI 伴侣对话**：基于 DeepSeek（`deepseek-chat` 模型），流式输出回复
- 🎭 **角色自定义**：在侧边栏随时修改伴侣的昵称与性格，动态注入系统提示词
- 📝 **多会话管理**：新建、切换、删除历史会话，会话以 JSON 文件持久化存储
- 💬 **类微信体验**：简短自然的回复风格，支持 emoji 表情
- 🌐 **多语言匹配**：自动匹配用户使用的语言

## 🛠️ 技术栈

| 类别 | 技术 |
| ---- | ---- |
| 前端框架 | [Streamlit](https://streamlit.io) |
| 大模型 | DeepSeek API（通过 OpenAI SDK 调用） |
| 语言/运行时 | Python 3.14+ |
| 配置管理 | python-dotenv（`.env` 文件） |

## 📂 项目结构
```text
AI_companion/
├── src/
│   ├── agent.py          # 应用主入口（聊天逻辑、会话管理）
│   ├── resources/
│   │   └── logo.png      # 页面 Logo
│   └── sessions/         # 会话记录（JSON 文件，运行时生成）
├── main.py               # 示例脚本（未使用）
├── .env                  # 环境变量（本地私密，不提交）
├── .env.example          # 环境变量模板
└── README.md
```
## 🚀 快速开始

### 1. 克隆并安装依赖

```bash
git clone <repo-url>
cd AI_companion

python -m venv .venv
source .venv/bin/activate

pip install streamlit openai python-dotenv
```

### 2. 配置 API Key

复制环境变量模板并填入你的 DeepSeek API Key：

```bash
cp .env.example .env
```

编辑 `.env`：

```text
DEEPSEEK_API_KEY=sk-你的密钥
```

> Key 可在 [DeepSeek 开放平台](https://platform.deepseek.com) 申请。

### 3. 启动应用

```bash
streamlit run src/agent.py
```

浏览器会自动打开 `http://localhost:8501`，开始与你的 AI 伴侣聊天吧 💕

## ⚠️ 注意事项

- 必须使用 `streamlit run` 启动，直接 `python src/agent.py` 无法正常运行
- `.env` 已被 `.gitignore` 忽略，请勿提交真实密钥
- 会话记录保存在运行目录下的 `sessions/` 文件夹中



## 📄 License

MIT
