from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from langchain.prompts import PromptTemplate
from typing import Any, Dict, Optional, Type

# 创建模拟搜索工具
class FakeDuckDuckGoSearchRun(BaseTool):
    name: str = "DuckDuckGoSearch"
    description: str = "用于搜索互联网信息的工具"

    def _run(self, query: str) -> str:
        # 根据不同查询返回不同的模拟结果
        if "AI" in query:
            return """
            最新AI新闻:
            1. OpenAI发布了GPT-5模型，具有更强的推理能力
            2. 谷歌推出了新的AI助手Gemini Pro 2.0
            3. 中国发布了AI发展国家战略，投入1000亿资金
            4. 自动驾驶技术取得重大突破，特斯拉完全自动驾驶即将推出
            5. AI在医疗领域应用显著提升，可提前预测多种疾病
            """
        elif "天气" in query:
            return "今天天气晴朗，气温20-25度，适合户外活动"
        else:
            return f"找到关于'{query}'的模拟搜索结果。这是一个假的搜索引擎，返回的是预设内容。"
            
    async def _arun(self, query: str) -> str:
        # 异步版本的实现
        return self._run(query)

# 选择使用哪个搜索工具（取消注释使用真实搜索）
# search = DuckDuckGoSearchRun()  # 真实搜索，需要安装: pip install -U duckduckgo-search
search = FakeDuckDuckGoSearchRun()  # 模拟搜索
tools = [search]

# 创建模型
llm = ChatOpenAI(temperature=0)

# 创建提示模板
template = """回答以下问题：

问题: {input}

你有以下工具可以使用:
{tools}

工具名称列表: {tool_names}

在回答前，需要思考使用哪些工具获取信息。使用以下格式：

Thought: 你的思考过程
Action: 工具名称（必须是上面工具列表中的一个）
Action Input: 输入到工具的内容
Observation: 工具的结果
... (重复Thought/Action/Action Input/Observation，直到你可以回答问题)
Thought: 现在我知道最终答案
Final Answer: 对原始问题的最终答案

{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# 创建 Agent
agent = create_react_agent(llm, tools, prompt)

# 创建执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=3,
    verbose=True,
    handle_parsing_errors=True
)

# 执行
result = agent_executor.invoke({
    "input": "最近有哪些AI方面的新闻？"
})

# 打印结果
print("\n最终结果:")
print(result["output"])