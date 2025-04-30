import os
import sys
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.multi_agents.utils import get_llm_by_type, ThinkingLevel
from app.multi_agents.prompts.template import PromptType, apply_prompt_template
from langchain_core.messages import HumanMessage, SystemMessage

user_query = "我爱你"

llm = get_llm_by_type(ThinkingLevel.SIMPLE)
# 创建一个包含messages的state字典
state = {"messages": [{"role": "user", "content": "你好"}]}

# 使用apply_prompt_template函数生成完整的消息列表
formatted_messages = apply_prompt_template(PromptType.COORDINATOR, state)


# 正确处理消息格式
messages = []
for msg in formatted_messages:
    if msg["role"] == "system":
        messages.append(SystemMessage(content=msg["content"]))
    elif msg["role"] == "user":
        messages.append(HumanMessage(content=msg["content"]))

# 添加用户查询
messages.append(HumanMessage(content=user_query))

# 调用LLM
result = llm.invoke(messages)
print(result.content)
