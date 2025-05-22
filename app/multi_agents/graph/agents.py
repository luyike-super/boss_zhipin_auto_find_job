from langgraph.prebuilt import create_react_agent

from app.multi_agents.utils import ThinkingLevel, get_llm_by_type
from app.multi_agents.tools import browser_tool, db_query_tools
from app.multi_agents.prompts import apply_prompt_template, PromptType


# 创建职位查找Agent
job_find_agent = create_react_agent(
    model=get_llm_by_type(ThinkingLevel.BASIC), 
    tools=[browser_tool],
    prompt=apply_prompt_template(PromptType.JOB_FIND)
)

# 创建数据库查询Agent
db_query_agent = create_react_agent(
    model=get_llm_by_type(ThinkingLevel.ADVANCED),
    tools=db_query_tools,
    prompt=apply_prompt_template(PromptType.DB_QUERY)
)











"""
创建一个新的agent，用于查询数据库      ,风格参考：job_find_agent

都是查询sqllite3数据库，只是数据库的表和字段不同

工具1：查询电路引脚表

工具2：查询电路原理图表

工具3：查询电路PCB表

工具4：查询电路3D模型表

工具5：查询电路BOM表

"""
