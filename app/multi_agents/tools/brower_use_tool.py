import asyncio

from pydantic import BaseModel, Field
from typing import Optional, ClassVar, Type
from langchain.tools import BaseTool
from browser_use import AgentHistoryList, Browser, BrowserConfig
from browser_use import Agent as BrowserAgent
from app.multi_agents.utils import LLMFactory, LLMProviderType
from app.utils.log_util import create_logged_tool
from app.config.config_com import CHROME_INSTANCE_PATH

expected_browser = None
# 如果指定了Chrome实例则使用， 可以指定为本地的chrome浏览器， 也可以指定为远程的浏览器
# if CHROME_INSTANCE_PATH:
#    expected_browser = Browser(
#        config=BrowserConfig(chrome_instance_path=CHROME_INSTANCE_PATH)
 #   )

vl_llm = LLMFactory.create_llm(LLMProviderType.QIANWEN,    temperature=0)



class BrowserUseInput(BaseModel):
    """WriteFileTool的输入。"""

    instruction: str = Field(..., description="The instruction to use browser")


class BrowserTool(BaseTool):
    name: ClassVar[str] = "browser"
    args_schema: Type[BaseModel] = BrowserUseInput
    description: ClassVar[str] = (
        "Use this tool to interact with web browsers. Input should be a natural language description of what you want to do with the browser, such as 'Go to google.com and search for browser-use', or 'Navigate to Reddit and find the top post about AI'."
    )

    _agent: Optional[BrowserAgent] = None

    def _run(self, instruction: str) -> str:
        """同步运行浏览器任务。"""
        self._agent = BrowserAgent(
            task=instruction,  # 将根据每个请求设置
            llm=vl_llm,
            browser=expected_browser,
        )
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self._agent.run())
                return (
                    str(result)
                    if not isinstance(result, AgentHistoryList)
                    else result.final_result
                )
            finally:
                loop.close()
        except Exception as e:
            return f"Error executing browser task: {str(e)}"

    async def _arun(self, instruction: str) -> str:
        """异步运行浏览器任务。"""
        self._agent = BrowserAgent(
            task=instruction, llm=vl_llm  # 将根据每个请求设置
        )
        try:
            result = await self._agent.run()
            return (
                str(result)
                if not isinstance(result, AgentHistoryList)
                else result.final_result
            )
        except Exception as e:
            return f"Error executing browser task: {str(e)}"


BrowserTool = create_logged_tool(BrowserTool)
browser_tool = BrowserTool()

if __name__ == "__main__":
    browser_tool.run("Go to google.com and search for browser-use")
