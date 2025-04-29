
from langgraph.prebuilt import create_react_agent

from app.multi_agents.utils import ThinkingLevel,get_llm_by_type
from app.multi_agents.tools import browser_tool
from app.multi_agents.prompts import apply_prompt_template,PromptType



agent_find_job   = create_react_agent(model=get_llm_by_type(ThinkingLevel.BASIC), tools=[browser_tool],prompt=apply_prompt_template(PromptType.JOB_FIND_AGENT))