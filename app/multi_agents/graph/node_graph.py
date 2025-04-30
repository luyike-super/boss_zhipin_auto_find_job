from langgraph.types import Command
from langgraph.graph import END
from .state_langgraph import State
from typing import Literal
from langgraph.graph import StateGraph


def frontdesk_agent(state: State) -> Command[Literal["planner"]]:
    """
    前台智能体: 系统的入口点
    
    角色: 负责初步需求识别和任务分发
    目标: 判断用户输入是否属于系统业务范围，提取关键信息，分发给规划智能体
    责任边界: 不执行具体任务，仅负责初步分类与路由
    
    流转: 前台智能体 -> 规划智能体 or __end__
    """



    
    # 判断用户输入是否属于系统业务范围
    # 如果属于，转到规划智能体；否则结束
    # 这里简化为直接转到规划智能体
    return Command(goto="planner")

def planner_agent(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """
    规划智能体: 任务分解和规划专家
    
    角色: 负责将用户需求分解为可执行的子任务
    目标: 将复杂需求分解为子任务序列，制定执行计划
    责任边界: 不执行具体任务，专注于任务拆解和依赖关系管理
    
    流转: 规划智能体 -> 监督智能体 or __end__
    """
    # 判断是否需要监督智能体
    # 这里简化为直接转到监督智能体
    return Command(goto="supervisor")

def supervisor_agent(state: State) -> Command[Literal["executor", "__end__"]]:
    """
    监督智能体: 执行监督和质量控制
    
    角色: 负责监督任务执行和质量控制
    目标: 确保任务执行符合预期，解决执行中的冲突和异常
    责任边界: 不执行具体任务，但需要理解任务内容以便有效监督
    
    流转: 监督智能体 -> 执行智能体 or __end__
    """
    # 判断是否需要执行智能体
    # 这里简化为直接转到执行智能体
    return Command(goto="executor")

def executor_agent(state: State) -> Command[Literal["__end__"]]:
    """
    执行智能体: 具体任务执行者
    
    角色: 负责执行具体任务
    目标: 完成分配的子任务，并报告执行结果
    责任边界: 专注于执行层面，不负责整体规划或监督
    
    流转: 执行智能体 -> __end__
    """
    # 执行任务并结束
    return Command(goto=END)

def job_find_agent(state: State) -> Command[Literal["__end__"]]:
    """
    岗位查找智能体: 
    
    角色: 岗位查找智能体
    目标: 根据用户的输入， 操作浏览器， 查找岗位， 并进行自我推荐
    操作完直接结束
    
    流转: 岗位筛选智能体 -> __end__
    """
    # 使用goto参数直接指定下一个节点为__end__
    return Command(goto="__end__")

def message_processor_agent(state: State) -> Command[Literal["__end__"]]:
    """
    消息处理智能体: HR沟通分析专家
    
    角色: HR沟通分析专家和沟通信号分析专家
    目标: 分析HR回复，确定后续行动（投递简历/回答问题）和评估HR回复中的兴趣信号
    责任边界: 只负责消息分析和建议，专注于意向分析和评分
    
    流转: 消息处理智能体 -> __end__
    """
    # 使用goto参数直接指定下一个节点为__end__
    return Command(goto="__end__")

def resume_agent(state: State) -> Command[Literal["__end__"]]:
    """
    简历智能体: 负责简历相关操作
    
    角色: 简历智能体
    目标: 管理和优化用户简历
    责任边界: 只负责简历相关任务
    
    流转: 简历智能体 -> __end__
    """
    return Command(goto="__end__")

def data_collector_agent(state: State) -> Command[Literal["__end__"]]:
    """
    数据收集智能体: 负责收集各类数据
    
    角色: 数据收集智能体
    目标: 收集和整理相关数据
    责任边界: 只负责数据收集相关任务
    
    流转: 数据收集智能体 -> __end__
    """
    return Command(goto="__end__")

def user_interaction_agent(state: State) -> Command[Literal["__end__"]]:
    """
    用户交互智能体: 负责与用户的交互
    
    角色: 用户交互智能体
    目标: 处理用户输入并提供反馈
    责任边界: 只负责用户交互相关任务
    
    流转: 用户交互智能体 -> __end__
    """
    return Command(goto="__end__")

def result_synthesizer_agent(state: State) -> Command[Literal["__end__"]]:
    """
    结果整合智能体: 负责整合各智能体结果
    
    角色: 结果整合智能体
    目标: 综合各智能体的输出，生成最终结果
    责任边界: 只负责结果整合相关任务
    
    流转: 结果整合智能体 -> __end__
    """
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
    workflow.add_node("frontdesk", frontdesk_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("executor", executor_agent)
    
    # 设置入口点
    workflow.set_entry_point("frontdesk")
    
    # 添加边
    workflow.add_edge("frontdesk", "planner")
    workflow.add_edge("planner", "supervisor")
    workflow.add_edge("supervisor", "executor")
    workflow.add_edge("executor", END)
    
    # 编译并返回
    return workflow.compile(checkpointer=checkpointer)
        