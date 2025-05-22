import asyncio
from pydantic import BaseModel, Field
from typing import ClassVar, Type, Optional, Any, List, Dict
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage

from browser_use import Browser, BrowserConfig, AgentHistoryList
from browser_use import Agent as BrowserAgent
from app.multi_agents.utils import LLMFactory, LLMProviderType
from app.utils.log_util import create_logged_tool
from app.config.config_com import CHROME_INSTANCE_PATH
from browser_use.agent.prompts import SystemPrompt

# 创建默认LLM实例
default_llm = LLMFactory.create_llm(LLMProviderType.QIANWEN)


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
    _llm: Any = None

    def __init__(self, llm=None, **kwargs):
        """初始化BossJobTool
        
        Args:
            llm: 自定义LLM，如果不提供则使用默认的千问LLM
            **kwargs: 其他BaseTool需要的参数
        """
        super().__init__(**kwargs)
        self._llm = llm if llm is not None else default_llm

    def _run(self, task: str ) -> str:
        """同步运行Boss直聘任务"""
        
        # 创建浏览器实例
        self._browser = Browser(config=BrowserConfig(
            headless=False,
            cdp_url="http://localhost:9999",
        ))
        
        
        self._agent = BrowserAgent(
            task=task,
            llm=self._llm,
            browser=self._browser,
        )
        
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # 运行协程并等待结果
                result = loop.run_until_complete(self._agent.run())
                # 处理结果
                if isinstance(result, AgentHistoryList):
                    # 构建结构化的返回结果
                    formatted_result = self._format_result(result)
                    return formatted_result
                return str(result)
            finally:
                # 确保关闭浏览器连接
                if self._browser:
                    loop.run_until_complete(self._browser.close())
                # 关闭事件循环
                loop.close()
        except Exception as e:
            return f"执行Boss直聘任务时出错: {str(e)}"

    def _format_result(self, result: AgentHistoryList) -> str:
        """将浏览器代理的结果格式化为结构化输出
        
        Args:
            result: 浏览器代理执行的结果
            
        Returns:
            格式化后的结果字符串
        """
        # 提取操作步骤
        steps = []
        for action in result.all_results:
            if action.is_done:
                # 最终结果
                final_result = action.extracted_content
            else:
                # 中间步骤
                steps.append(action.extracted_content)
        
        # 构建结构化输出
        output = f"""
## Boss直聘岗位查找结果

### 执行步骤:
{''.join([f'- {step}\n' for step in steps])}

### 任务结果:
{final_result}
"""
        return output

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
                llm=self._llm,
                browser=self._browser,
                system_prompt_class=SystemPrompt()
            )
            # 运行任务
            result = await self._agent.run()
            # 处理结果
            if isinstance(result, AgentHistoryList):
                # 构建结构化的返回结果
                formatted_result = self._format_result(result)
                return formatted_result
            return str(result)
        except Exception as e:
            return f"执行Boss直聘任务时出错: {str(e)}"
        finally:
            # 确保浏览器被关闭
            if self._browser:
                await self._browser.close()
                self._browser = None

# 创建默认工具实例
BossJobTool = create_logged_tool(BossJobTool)
boss_job_tool = BossJobTool()


def create_boss_job_tool(llm=None):
    """创建一个使用自定义LLM的BossJobTool实例
    
    Args:
        llm: 自定义LLM，如果不提供则使用默认的千问LLM
        
    Returns:
        BossJobTool实例
    """
    tool_cls = create_logged_tool(BossJobTool)
    return tool_cls(llm=llm)


if __name__ == "__main__":
    # 测试工具
    try:
        # 模拟系统消息和用户消息
        test_messages = [
            {"role": "system", "content": "你是岗位查找智能体"},
            {"role": "human", "content": "在Boss直聘上搜索深圳的Python开发工作"}
        ]
        
        # 使用消息列表格式调用
        instruction = "在Boss直聘上搜索深圳的Python开发工作"
        result = boss_job_tool.run(instruction)
        print(f"执行结果:\n{result}")
        
        # 也可以直接使用字符串格式调用
        # result = boss_job_tool._run("在Boss直聘上搜索上海的产品经理职位")
        # print(f"直接调用结果:\n{result}")
    except Exception as e:
        print(f"执行出错: {e}")