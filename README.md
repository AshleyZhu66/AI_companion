# 你的 AI 伴侣（AI Companion）

一个基于 **Python + Streamlit + DeepSeek** 的 AI 智能伴侣聊天应用。你可以自定义伴侣的昵称和性格，像微信聊天一样与 TA 对话，并支持多会话的历史记录管理。

## ✨ 功能特性

- 🤖 **AI 伴侣对话**：基于 DeepSeek（`deepseek-chat` 模型），流式逐字输出回复
- 🎭 **角色自定义**：在侧边栏随时修改伴侣的昵称与性格，发送请求时动态注入系统提示词
- 📝 **多会话管理**：新建、切换、删除历史会话，会话以 JSON 文件持久化存储
- ✂️ **上下文窗口控制**：每次请求最多携带最近 40 条历史消息（仅影响发给模型的上下文，不影响本地保存与展示）
- 💬 **类微信体验**：单条短回复、支持 emoji 表情，禁止场景/状态描述性文字
- 🌐 **多语言匹配**：自动匹配用户使用的语言
- 🔔 **交互反馈**：会话删除、加载失败、模型空返回等场景通过 toast 即时提示（显示后自动清除）

## 🛠️ 技术栈

| 类别 | 技术 |
| ---- | ---- |
| 前端框架 | [Streamlit](https://streamlit.io) |
| 大模型 | DeepSeek API（通过 OpenAI SDK 调用，`https://api.deepseek.com`） |
| 语言/运行时 | Python 3.14+ |
| 配置管理 | python-dotenv（`.env` 文件） |
| 依赖管理 | requirements.txt |

## 📂 项目结构
```text
AI_companion/
├── src/
│   ├── agent.py          # 应用主入口（聊天逻辑、会话管理、UI 渲染）
│   ├── resources/
│   │   └── logo.png      # 页面 Logo
│   └── sessions/         # 会话记录（JSON 文件，运行时生成，不提交）
├── utils/
│   ├── __init__.py       # 工具包统一导出入口
│   └── llm_client.py     # LLM 调用封装（单轮/多轮/流式 + token 统计）
├── main.py               # 占位脚本（当前为空）
├── requirements.txt      # 依赖清单
├── .env                  # 环境变量（本地私密，不提交）
├── .env.example          # 环境变量模板
├── .gitignore
└── README.md
```

> `utils/` 只存放与 UI 无关的纯逻辑工具，模块内禁止读写 `st.session_state`（状态统一由页面层管理）；当前 `src/agent.py` 直接调用 OpenAI SDK，`utils/llm_client.py` 作为通用能力供后续扩展接入。

## 🚀 快速开始

### 1. 克隆并安装依赖

```bash
git clone <repo-url>
cd AI_companion

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
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

> Key 可在 [DeepSeek 开放平台](https://platform.deepseek.com) 申请。程序基于 `__file__` 加载项目根目录的 `.env`，因此不受启动目录影响。

### 3. 启动应用

```bash
streamlit run src/agent.py
```

浏览器会自动打开 `http://localhost:8501`，开始与你的 AI 伴侣聊天吧 💕

## 🎛️ 使用指南

1. **侧边栏「新建会话」**：当前会话有内容时才创建新会话，并自动归档上一会话
2. **历史会话列表**：按会话名（时间戳 + 随机后缀）倒序展示，点击 📄 切换、❌ 删除，当前会话高亮
3. **昵称 / 性格**：修改后即刻生效，下一条消息即按新设定回复；新建会话时恢复默认值
4. **聊天区**：底部输入框发送消息，AI 回复以流式方式增量渲染

## ⚙️ 默认配置

| 配置项 | 说明 | 默认值 |
| ---- | ---- | ---- |
| `DEFAULT_NICK_NAME` | 默认伴侣昵称 | 柒柒 |
| `DEFAULT_NATURE` | 默认性格设定 | 活泼开朗、喜欢聊天、有逻辑、有耐心、有爱心 |
| `MAX_CONTEXT_MESSAGES` | 单次请求最大历史消息条数 | 40 |
| `model` | 调用的模型名称 | `deepseek-chat` |

以上常量均位于 `src/agent.py` 顶部，可直接按需调整。

## ⚠️ 注意事项

- 必须使用 `streamlit run` 启动，直接 `python src/agent.py` 无法正常运行
- `.env` 已被 `.gitignore` 忽略，请勿提交真实密钥
- 会话记录保存在 `src/sessions/` 目录下（同样已被 Git 忽略），删除目录即清空全部历史
- 上下文窗口只裁剪发送给模型的历史，本地仍完整保存全部消息
- 模型返回空内容时不会写入空白气泡，仅提示「模型未返回内容，请重试」

## 📄 License

MIT
