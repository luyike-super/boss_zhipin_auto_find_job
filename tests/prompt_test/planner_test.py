import os
import sys
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.multi_agents.utils import get_llm_by_type, ThinkingLevel
from app.multi_agents.prompts.template import PromptType, apply_prompt_template
from langchain_core.messages import HumanMessage, SystemMessage
from app.multi_agents.graph.state_langgraph import State
from app.config.config_com import TEAM_MEMBERS

user_query = "请计算12*12， 并去boos直聘，寻找AI Agnet 开发工作, 并且和HR进行沟通"

llm = get_llm_by_type(ThinkingLevel.ADVANCED)
# 创建一个包含messages的state字典
state = State(messages=[HumanMessage(content=user_query)] , TEAM_MEMBERS=TEAM_MEMBERS)

# 使用apply_prompt_template函数生成完整的消息列表
formatted_messages = apply_prompt_template(PromptType.PLANNER, state)



# 调用LLM
result = llm.invoke(formatted_messages)
print(result.content)
