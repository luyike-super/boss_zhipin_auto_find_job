from langgraph.types import Command
from langgraph.graph import END
from .state_langgraph import State
from typing import Literal

def frontdesk_agent(state: State) -> Command[Literal["__end__", "planner"]]:
    """
    前台智能体: 系统的入口点
    
    角色: 负责初步需求识别和任务分发
    目标: 判断用户输入是否属于系统业务范围，提取关键信息，分发给规划智能体
    责任边界: 不执行具体任务，仅负责初步分类与路由
    
    流转: 前台智能体 -> 规划智能体 or __end__
    """
    return Command(name="planner", args={"state": state})

def planner_agent(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """
    规划智能体: 任务分解和规划专家
    
    角色: 负责将用户需求分解为可执行的子任务
    目标: 将复杂需求分解为子任务序列，制定执行计划
    责任边界: 不执行具体任务，专注于任务拆解和依赖关系管理
    
    流转: 规划智能体 -> 监督智能体 or __end__
    """
    return Command(name="supervisor", args={"state": state})

def supervisor_agent(state: State) -> Command[Literal["job_filter", "message_processor", "resume", "data_collector", "user_interaction", "result_synthesizer"]]:
    """
    监督智能体: 工具智能体的调度者和质量控制者
    
    角色: 负责选择和调度适当的工具智能体执行任务
    目标: 基于规划选择合适的工具智能体，审查结果质量，决定后续行动
    责任边界: 不执行具体任务，专注于调度和质量控制
    
    流转: 监督智能体 -> 各种工具智能体(岗位筛选/消息处理/简历/数据收集/用户交互/结果整合)
    """
    # 根据状态选择合适的工具智能体，这里简化为默认调用job_filter_agent
    return Command(name="job_filter", args={"state": state})


def jod_find_agent(state: State) -> Command[Literal["__end__"]]:
    """
    岗位查找智能体: 
    
    角色: 岗位查找智能体
    目标: 根据用户的输入， 操作浏览器， 查找岗位， 并进行自我推荐
    操作完直接结束
    
    流转: 岗位筛选智能体 -> __end__
    """
    return Command(name="supervisor", args={"state": state},goto="__end__")

def message_processor_agent(state: State) -> Command[Literal["__end__"]]:
    """
    消息处理智能体: HR沟通分析专家
    
    角色: HR沟通分析专家和沟通信号分析专家
    目标: 分析HR回复，确定后续行动（投递简历/回答问题）和评估HR回复中的兴趣信号
    责任边界: 只负责消息分析和建议，专注于意向分析和评分
    
    流转: 消息处理智能体 -> __end__
    """
    return Command(name="supervisor", args={"state": state},goto=" __end__")