from langgraph.types import Command
from langgraph.graph import END
from .state_langgraph import State,Router
from typing import Literal
from langgraph.graph import StateGraph
from app.multi_agents.utils import get_llm_by_type, ThinkingLevel, get_logger
from app.multi_agents.prompts.template import PromptType, apply_prompt_template
from langchain_core.messages import BaseMessage,AIMessage
from app.multi_agents.tools import boss_job_tool
from browser_use.agent.prompts import SystemPrompt
from datetime import  datetime
import re


# 获取日志记录器
logger = get_logger(__name__, level="debug")


def clean_content(content):
    """
    清理内容中的代码块标记，如 ```json ... ```
    """
    # 匹配并移除代码块标记
    pattern = r'^```(?:json)?[\s\n]+([\s\S]+?)[\s\n]*```$'
    match = re.match(pattern, content.strip())
    if match:
        return match.group(1).strip()
    return content


def frontdesk_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """
    前台智能体: 系统的入口点
    
    角色: 负责初步需求识别和任务分发
    目标: 判断用户输入是否属于系统业务范围，提取关键信息，分发给规划智能体
    责任边界: 不执行具体任务，仅负责初步分类与路由
    
    流转: 前台智能体 -> 规划智能体 or __end__
    """
    llm = get_llm_by_type(ThinkingLevel.SIMPLE)
    logger.debug("前台智能体开始工作", agent_name="frontdesk")
    # 使用apply_prompt_template函数生成完整的消息列表
    formatted_messages = apply_prompt_template(PromptType.COORDINATOR, state)

    # 调用LLM
    result = llm.invoke(formatted_messages)
    if "handoff_to_planner()" in result.content:
        goto = "planner"
        logger.agent_transition("frontdesk", "planner", "满足跳转条件，包含handoff_to_planner()")
    else:
        goto = "__end__"
        logger.agent_transition("frontdesk", "__end__", "不满足跳转条件")

    return Command(goto=goto)

def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """
    规划智能体: 任务分解和规划专家
    
    角色: 负责将用户需求分解为可执行的子任务
    目标: 将复杂需求分解为子任务序列，制定执行计划
    责任边界: 不执行具体任务，专注于任务拆解和依赖关系管理
    
    流转: 规划智能体 -> 监督智能体 or __end__
    """

    llm = get_llm_by_type(ThinkingLevel.ADVANCED)
    # 使用apply_prompt_template函数生成完整的消息列表
    formatted_messages = apply_prompt_template(PromptType.PLANNER, state)
    result = llm.invoke(formatted_messages)
    
    # 清理content中的代码块标记
    cleaned_content = clean_content(result.content)
    
    logger.debug("规划智能体完成工作", agent_name="planner")    
    logger.debug(f"规划智能体结果: {cleaned_content}", agent_name="planner")
    

    # 判断是否需要监督智能体
    # 这里简化为直接转到监督智能体
    logger.agent_transition("planner", "supervisor", "规划完成，转到监督智能体")
    return Command(goto="supervisor", update={"full_plan": cleaned_content})

def supervisor_node(state: State) -> Command[Literal["executor", "job_find"]]:
    """
    监督智能体: 执行监督和质量控制

    角色: 负责监督任务执行和质量控制
    目标: 确保任务执行符合预期，解决执行中的冲突和异常
    责任边界: 不执行具体任务，但需要理解任务内容以便有效监督
    
    流转: 监督智能体 -> 执行智能体 or __end__
    """
    llm = get_llm_by_type(ThinkingLevel.SIMPLE)
    # 使用apply_prompt_template函数生成完整的消息列表
    formatted_messages = apply_prompt_template(PromptType.SUPERVISOR, state)
    result = llm.with_structured_output(Router). invoke(formatted_messages)
    goto = result["next"]

    logger.debug("监督智能体开始工作", agent_name="supervisor")



    logger.agent_transition("supervisor", "executor", "监督任务设置完成，转到执行智能体")
    return Command(goto=goto, update={"next": goto })
def executor_node(state: State) -> Command[Literal["__end__"]]:
    """
    执行智能体: 具体任务执行者
    
    角色: 负责执行具体任务
    目标: 完成分配的子任务，并报告执行结果
    责任边界: 专注于执行层面，不负责整体规划或监督
    
    流转: 执行智能体 -> __end__
    """
    # 执行任务并结束
    logger.agent_transition("executor", "__end__", "任务执行完成，工作流结束")
    return Command(goto=END)

def job_find_node(state: State) -> Command[Literal["supervisor"]]:
    """
    岗位查找智能体: 
    
    角色: 岗位查找智能体
    目标: 根据用户的输入， 操作浏览器， 查找岗位， 并进行自我推荐
    操作完直接结束
    
    流转: 岗位筛选智能体 -> supervisor
    """
    # 使用goto参数直接指定下一个节点为 supervisor
    try:
        # 获取用户的原始输入
        user_messages = state["messages"][0].content
    
        # 格式化消息
        formatted_messages = apply_prompt_template(PromptType.JOB_FIND, state, additional_vars={"originquery": user_messages})
        
        # 调用Boss直聘工具
        logger.debug(f"调用Boss直聘工具开始", agent_name="job_find")

        print(formatted_messages[0])
        result = boss_job_tool._run(formatted_messages[0])
        logger.debug(f"调用Boss直聘工具完成: {result[:100]}...", agent_name="job_find")
        
        # 创建消息
        msg = AIMessage(content=result,  name="browse")
        
        # 记录日志并返回命令
        logger.agent_transition("job_find", "supervisor", "岗位查找完成")
        return Command(goto="supervisor", update={"messages": [msg]})
    except Exception as e:
        # 处理异常
        error_msg = f"岗位查找失败: {str(e)}"
        logger.error(error_msg, agent_name="job_find")
        msg = BaseMessage(content=error_msg, type="error", name="error")
        return Command(goto="supervisor", update={"messages": [msg]})

def message_processor_node(state: State) -> Command[Literal["__end__"]]:
    """
    消息处理智能体: HR沟通分析专家
    
    角色: HR沟通分析专家和沟通信号分析专家
    目标: 分析HR回复，确定后续行动（投递简历/回答问题）和评估HR回复中的兴趣信号
    责任边界: 只负责消息分析和建议，专注于意向分析和评分
    
    流转: 消息处理智能体 -> __end__
    """
    # 使用goto参数直接指定下一个节点为__end__
    logger.agent_transition("message_processor", "__end__", "消息处理完成")
    return Command(goto="__end__")

def resume_node(state: State) -> Command[Literal["__end__"]]:
    """
    简历智能体: 负责简历相关操作
    
    角色: 简历智能体
    目标: 管理和优化用户简历
    责任边界: 只负责简历相关任务
    
    流转: 简历智能体 -> __end__
    """
    logger.agent_transition("resume", "__end__", "简历处理完成")
    return Command(goto="__end__")

def data_collector_node(state: State) -> Command[Literal["__end__"]]:
    """
    数据收集智能体: 负责收集各类数据
    
    角色: 数据收集智能体
    目标: 收集和整理相关数据
    责任边界: 只负责数据收集相关任务
    
    流转: 数据收集智能体 -> __end__
    """
    logger.agent_transition("data_collector", "__end__", "数据收集完成")
    return Command(goto="__end__")

def user_interaction_node(state: State) -> Command[Literal["__end__"]]:
    """
    用户交互智能体: 负责与用户的交互
    
    角色: 用户交互智能体
    目标: 处理用户输入并提供反馈
    责任边界: 只负责用户交互相关任务
    
    流转: 用户交互智能体 -> __end__
    """
    logger.agent_transition("user_interaction", "__end__", "用户交互完成")
    return Command(goto="__end__")

def result_synthesizer_node(state: State) -> Command[Literal["__end__"]]:
    """
    结果整合智能体: 负责整合各智能体结果
    
    角色: 结果整合智能体
    目标: 综合各智能体的输出，生成最终结果
    责任边界: 只负责结果整合相关任务
    
    流转: 结果整合智能体 -> __end__
    """
    logger.agent_transition("result_synthesizer", "__end__", "结果整合完成")
    return Command(goto="__end__")

def build_agent(checkpointer=None) -> StateGraph:
    """
    构建智能体图
    
    参数:
        checkpointer: 用于保存状态的检查点存储器
    """
    # 创建图
    workflow = StateGraph(State)
    
    # 添加节点
    workflow.add_node("frontdesk", frontdesk_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("job_find", job_find_node)
    
    # 设置入口点
    workflow.set_entry_point("frontdesk")
    
    # 添加边
    workflow.add_edge("frontdesk", "planner")
    workflow.add_edge("planner", "supervisor")

    
    logger.info("智能体图构建完成", agent_name="system")
    
    # 编译并返回
    return workflow.compile(checkpointer=checkpointer)
        