"""llm_client.py —— 封装 LLM API 调用"""
from openai import OpenAI
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM 调用结果"""
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMClient:
    """统一的 LLM 调用客户端——支持多模型切换"""

    def __init__(self, api_key: str, base_url: str, default_model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.default_model = default_model

    def chat(
        self,
        user_message: str,
        system_prompt: str = "你是一个有帮助的助手",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """发送单轮对话"""
        response = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        usage = response.usage
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )

    def chat_with_history(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """发送多轮对话（messages 里包含完整历史）"""
        response = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
        )

        usage = response.usage
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )

    def chat_stream(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7,
    ):
        """流式多轮对话，逐段生成助手回复内容（yield str）"""
        stream = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

# ===== 使用示例 =====
if __name__ == "__main__":
    # 初始化客户端（这里以 DeepSeek 为例）
    llm = LLMClient(
        api_key="sk-your-key",
        base_url="https://api.deepseek.com",
        default_model="deepseek-chat",
    )

    # 单轮对话
    resp = llm.chat("用 Python 写一个斐波那契数列函数")
    print(f"回答: {resp.content[:200]}...")
    print(f"消耗 Token: {resp.total_tokens}")

    # 多轮对话
    history = [
        {"role": "system", "content": "你是 Python 导师"},
        {"role": "user", "content": "什么是装饰器？"},
    ]
    resp = llm.chat_with_history(history)
    print(f"\n回答: {resp.content[:200]}...")