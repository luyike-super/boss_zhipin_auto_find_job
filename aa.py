import asyncio
from pydantic import BaseModel, Field
from typing import ClassVar, Type, Optional
from langchain.tools import BaseTool

from browser_use import Browser, BrowserConfig, AgentHistoryList
from browser_use import Agent as BrowserAgent
from app.multi_agents.utils import LLMFactory, LLMProviderType
from app.utils.log_util import create_logged_tool
from app.config.config_com import CHROME_INSTANCE_PATH

# 创建LLM实例
llm_deepseek = LLMFactory.create_llm(LLMProviderType.QIANWEN)

# 如果指定了Chrome实例则使用，可以指定为本地的chrome浏览器，也可以指定为远程的浏览器
expected_browser = None
# if CHROME_INSTANCE_PATH:
#     expected_browser = Browser(
#         config=BrowserConfig(chrome_instance_path=CHROME_INSTANCE_PATH)
#     )


class BossJobInput(BaseModel):
    """BossJobTool的输入"""
    
    instruction: str = Field(..., description="用于在Boss直聘上查找工作的指令")


class BossJobTool(BaseTool):
    name: ClassVar[str] = "boss_job"
    args_schema: Type[BaseModel] = BossJobInput
    description: ClassVar[str] = (
        "使用这个工具在Boss直聘网站上查找工作。输入应该是对你想在Boss直聘上做什么的自然语言描述，"
        "例如'在Boss直聘上搜索深圳的Python开发工作'或'查找上海月薪2万以上的产品经理职位'。"
    )

    _agent: Optional[BrowserAgent] = None
    _browser: Optional[Browser] = None

    def _run(self, instruction: str) -> str:
        """同步运行Boss直聘任务"""
        
        # 创建浏览器实例
        self._browser = Browser(config=BrowserConfig(
            headless=False,
            cdp_url="http://localhost:9999"
        ))
        
        self._agent = BrowserAgent(
            task=instruction,
            llm=llm_deepseek,
            browser=self._browser,
        )
        
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # 运行协程并等待结果
                result = loop.run_until_complete(self._agent.run())
                # 在关闭浏览器之前处理返回结果
                if isinstance(result, AgentHistoryList):
                    return result.final_result
                return str(result)
            finally:
                # 确保关闭浏览器连接
                if self._browser:
                    loop.run_until_complete(self._browser.close())
                # 关闭事件循环
                loop.close()
        except Exception as e:
            return f"执行Boss直聘任务时出错: {str(e)}"

    async def _arun(self, instruction: str) -> str:
        """异步运行Boss直聘任务"""
        # 创建浏览器实例
        self._browser = Browser(config=BrowserConfig(
            headless=False,
            cdp_url="http://localhost:9999"
        ))
        
        try:
            self._agent = BrowserAgent(
                task=instruction,
                llm=llm_deepseek,
                browser=self._browser
            )
            # 运行任务
            result = await self._agent.run()
            # 处理返回结果
            if isinstance(result, AgentHistoryList):
                return result.final_result
            return str(result)
        except Exception as e:
            return f"执行Boss直聘任务时出错: {str(e)}"
        finally:
            # 确保浏览器被关闭
            if self._browser:
                await self._browser.close()
                self._browser = None


# 使用create_logged_tool进行日志追踪
BossJobTool = create_logged_tool(BossJobTool)
boss_job_tool = BossJobTool()


if __name__ == "__main__":
    # 测试工具
    try:
        result = boss_job_tool.run("在Boss直聘上搜索深圳的Python开发工作")
        print(f"执行结果: {result}")
    except Exception as e:
        print(f"执行出错: {e}")