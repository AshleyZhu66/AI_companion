import os
import json
import uuid
import streamlit as st
from datetime import datetime
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录下的 .env（不受运行目录影响）
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# 锚定到脚本所在目录，避免受运行目录影响
BASE_DIR = Path(__file__).resolve().parent
SESSIONS_DIR = BASE_DIR / "sessions"

# 设置页面配置
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_NICK_NAME = "柒柒"
DEFAULT_NATURE = "活泼开朗、喜欢聊天、有逻辑、有耐心、有爱心"

# 每次请求携带的最大历史消息条数（只影响发给模型的上下文，不影响本地保存/展示）
MAX_CONTEXT_MESSAGES = 40

# 页面主标题 和 Logo
st.title("你的AI伴侣")
st.logo(str(BASE_DIR / "resources" / "logo.png"), size="large")

# 一次性提示消息（显示后清除，避免常驻页面）
if "flash_msg" in st.session_state:
    st.toast(st.session_state.pop("flash_msg"), icon="✅", duration=2)
if "flash_error" in st.session_state:
    st.toast(st.session_state.pop("flash_error"), icon="❗️")

# 默认昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = DEFAULT_NICK_NAME

# 默认性格
if "nature" not in st.session_state:
    st.session_state.nature = DEFAULT_NATURE

# 系统提示词模板（普通字符串 + 命名占位符，发送请求时才惰性注入，保证昵称/性格为最新值）
system_prompt = """
    你叫{nick_name}，现在是用户的真实伴侣，请完全代入伴侣角色。：
    规则：
        1. 每次只回1条消息
        2. 禁止任何场景或状态描述性文字
        3. 匹配用户的语言
        4. 回复简短，像微信聊天一样
        5. 有需要的话可以用 ❤️🥰 等emoji表情
        6. 用符合伴侣性格的方式对话
        7. 回复的内容，要充分体现伴侣的性格特征
        8. 回复时，要避免使用专业术语和行话
        9. 回复时，要避免使用复杂难懂的表达
        10. 禁止三观不正的内容、任何违法内容
        11. 禁止极端情绪引导
    伴侣性格：
        {nature}
    你必须严格遵守上述规则来回复用户。
"""


# 生成会话标识
def generate_session_name():
    while True:
        name = datetime.now().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:4]
        if not (SESSIONS_DIR / f"{name}.json").exists():
            return name


# 设置当前会话标识
if "cur_session_name" not in st.session_state:
    st.session_state.cur_session_name = generate_session_name()

# 调用大模型
api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    st.error("DEEPSEEK_API_KEY environment variable is not set")
    st.stop()

#
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# 构建发送给模型的上下文：只取最近 N 条，并保证以 user 开头
def build_context(messages, limit=MAX_CONTEXT_MESSAGES):
    window = list(messages[-limit:])
    while window and window[0]["role"] != "user":
        window.pop(0)
    return window


# 新建会话信息
def create_session_info():
    st.session_state.cur_session_name = generate_session_name()
    st.session_state.nick_name = DEFAULT_NICK_NAME
    st.session_state.nature = DEFAULT_NATURE
    st.session_state.messages = []


# 保存会话信息
def save_session_info():
    if st.session_state.cur_session_name:
        # 构建会话对象
        session_data = {
            "cur_session_name": st.session_state.cur_session_name,
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "messages": st.session_state.messages
        }
        # check sessions目录是否存在，不存在则创建
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

        with open(SESSIONS_DIR / f"{st.session_state.cur_session_name}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


# 加载会话列表
def load_sessions():
    if not SESSIONS_DIR.exists():
        return []
    return sorted((p.stem for p in SESSIONS_DIR.glob("*.json")), reverse=True)


# 加载指定会话
def load_session(session_name):
    try:
        if (SESSIONS_DIR / f"{session_name}.json").exists():
            with open(SESSIONS_DIR / f"{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.cur_session_name = session_data.get("cur_session_name", session_name)
                st.session_state.nick_name = session_data.get("nick_name", DEFAULT_NICK_NAME)
                st.session_state.nature = session_data.get("nature", DEFAULT_NATURE)
                st.session_state.messages = session_data.get("messages", [])
    except Exception as e:
        st.session_state.flash_error = f"Error loading session {session_name}: {e}"


# 删除指定会话
def delete_session(session_name):
    try:
        if (SESSIONS_DIR / f"{session_name}.json").exists():
            os.remove(SESSIONS_DIR / f"{session_name}.json")
            st.session_state.flash_msg = f"Session {session_name} deleted successfully"
            if session_name == st.session_state.cur_session_name:
                create_session_info()
        else:
            st.session_state.flash_error = f"Session {session_name} does not exist"

    except Exception as e:
        st.session_state.flash_error = f"Error deleting session {session_name}: {e}"


# 左边侧边栏
with st.sidebar:
    st.subheader("AI控制面板")
    # 新建会话按钮
    if st.button("新建会话", width="stretch", icon="✏️"):
        if st.session_state.messages:  # 如果当前会话有消息，没有消息则不重复新建会话
            # 保存当前会话
            save_session_info()
            # 新建会话
            create_session_info()
            st.rerun()
        else:
            st.toast("当前会话没有内容，不需要新建", icon="ℹ️")

    # 会话列表
    session_list = load_sessions()
    st.text("历史会话" if session_list else "")
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            button_type = "primary" if session == st.session_state.cur_session_name else "secondary"
            if st.button(session, key=f"load_{session}", type=button_type, width="stretch", icon="📄"):
                if session != st.session_state.cur_session_name and st.session_state.messages != []:
                    save_session_info()
                load_session(session)
                st.rerun()
        with col2:
            if st.button("", key=f"delete_{session}", width="stretch", icon="❌️", ):
                delete_session(session)
                st.rerun()

    st.divider()
    # AI昵称和性格
    nick_name = st.text_input("昵称", value=st.session_state.nick_name, placeholder="请输入伴侣昵称")
    if nick_name:
        st.session_state.nick_name = nick_name

    nature = st.text_area("性格", value=st.session_state.nature, placeholder="请输入伴侣性格")
    if nature:
        st.session_state.nature = nature

# 初始化聊天消息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 展示聊天信息
st.text(f"会话名称：{st.session_state.cur_session_name}")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 聊天消息输入框
prompt = st.chat_input("Message Me")
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": system_prompt.format(nick_name=st.session_state.nick_name, nature=st.session_state.nature)},
                *build_context(st.session_state.messages)
            ],
            stream=True
        )
        full_res = ""
        # 进入 assistant 容器一次，内部用 placeholder 增量更新，避免每个 chunk 重建容器
        with st.chat_message("assistant"):
            response_msg = st.empty()
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_res += content
                    response_msg.write(full_res)

        # 侧边栏在本次运行开头就已渲染，新会话首次落盘后重跑一次刷新历史列表
        if full_res.strip():  # 避免模型返回空内容时插入一条空白气泡(接口异常、被截断、内容审核拦截等)
            is_first_save = not (SESSIONS_DIR / f"{st.session_state.cur_session_name}.json").exists()
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            save_session_info()

            if is_first_save:
                st.rerun()
        else:
            st.toast("模型未返回内容，请重试", icon="ℹ️")

    except Exception as e:
        st.session_state.flash_error = f"Error generating response: {e}"
        st.rerun()
