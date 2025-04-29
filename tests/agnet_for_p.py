def user_interaction_agent(state: State) -> Command[Literal["supervisor", "END"]]:
    """
    用户交互智能体: 负责与用户的直接沟通
    
    角色: 负责与用户进行交互沟通
    目标: 以友好方式呈现系统状态和进度，收集用户反馈
    责任边界: 不参与业务逻辑，专注于信息呈现和收集
    
    流转: 用户交互智能体 -> 监督智能体(继续处理) 或 END(结束流程)
    """
    # 根据状态决定是继续处理还是结束
    # 简化为默认返回监督智能体继续处理
    return Command(name="supervisor", args={"state": state})


def resume_agent(state: State) -> Command[Literal["supervisor"]]:
    """
    简历管理智能体: 简历定制专家
    
    角色: 简历定制专家
    目标: 根据岗位要求优化和定制简历
    责任边界: 专注于简历相关操作
    
    流转: 简历管理智能体 -> 监督智能体
    """
    return Command(name="supervisor", args={"state": state})

def data_collector_agent(state: State) -> Command[Literal["supervisor"]]:
    """
    数据收集智能体: 数据爬取和分析专家
    
    角色: 数据爬取和分析专家
    目标: 收集岗位信息、薪资数据等
    责任边界: 负责数据获取和初步分析
    
    流转: 数据收集智能体 -> 监督智能体
    """
    return Command(name="supervisor", args={"state": state})

def result_synthesizer_agent(state: State) -> Command[Literal["user_interaction", "END"]]:
    """
    结果整合智能体: 结果最终整合者
    
    角色: 结果最终整合
    目标: 将所有结果整合成最终结论，作为最终响应
    责任边界: 只负责结果整合，不参与业务逻辑。只在最后生效
    
    流转: 结果整合智能体 -> 用户交互智能体 或 END(结束流程)
    """
    # 简化为默认返回用户交互
    return Command(name="user_interaction", args={"state": state})
