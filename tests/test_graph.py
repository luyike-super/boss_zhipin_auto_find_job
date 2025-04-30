import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.multi_agents.graph.node_graph import build_agent
from app.multi_agents.graph.state_langgraph import State
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

def test_basic_flow():
    """测试基本工作流程，从前台智能体开始，执行完整流程"""
    print("开始测试基本工作流程...")
    
    # 使用内存存储器保存状态
    checkpointer = InMemorySaver()
    
    # 构建图
    graph = build_agent(checkpointer=checkpointer)
    
    # 创建初始状态
    initial_state = State(
        messages=[HumanMessage(content="我想找一份Python开发工作")]
    )
    
    # 运行图，传入初始状态
    config = {"configurable": {"thread_id": "test-thread-1"}}
    result = graph.invoke(initial_state, config)
    
    # 打印结果
    print("\n=== 执行结果 ===")
    print(f"最终状态: {result}")
    
    return result

def test_specific_agent(agent_name="job_filter"):
    """测试特定智能体的功能"""
    print(f"\n开始测试特定智能体: {agent_name}...")
    
    # 使用内存存储器保存状态
    checkpointer = InMemorySaver()
    
    # 构建图
    graph = build_agent(checkpointer=checkpointer)
    
    query ="查询蔡徐坤的最新消息"
    # 创建初始状态，将command设置为特定智能体
    initial_state = State(
        messages=[HumanMessage(content=query)]
    )
    
    # 调用图的特定节点
    config = {"configurable": {"thread_id": f"test-{agent_name}"}}
    # 从特定节点开始执行(如果需要)
    # config["entry_point"] = agent_name
    result = graph.invoke(initial_state, config)
    
    # 打印结果
    print(f"\n=== {agent_name}执行结果 ===")
    print(f"最终状态: {result}")
    # 打印chat_history
    
    return result

if __name__ == "__main__":
    # 测试完整流程
    test_basic_flow()
    
    # 测试特定智能体
    # test_specific_agent("job_filter") 