from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from typing import Dict, Any

# 定义几个简单的工具函数
@tool
def add(a: int, b: int) -> int:
    """将两个数字相加"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """将两个数字相乘"""
    return a * b

@tool
def search(query: str) -> str:
    """模拟搜索功能"""
    return f"这是关于'{query}'的搜索结果"

"""
示例1: 计算乘法
工具调用信息: [{'name': 'multiply', 'args': {'a': 100, 'b': 100}, 'id': 'call_0_67e5c592-a29d-4e8b-8ec7-0f6f2c1c626b', 'type': 'tool_call'}]
工具 multiply 的结果: 10000
"""
def test_llm_with_tools():
    # 定义工具列表
    tools = [add, multiply, search]
    
    # 初始化LLM
    llm = ChatDeepSeek(model="deepseek-chat", temperature=0)  
    llm_with_tools = llm.bind_tools(tools)
  
    # 测试乘法计算
    print("示例1: 计算乘法")
    result1 = llm_with_tools.invoke("计算100 * 100")  
    
    print(f"工具调用信息: {result1.tool_calls}")
    
    # 处理工具调用结果
    for tool_call in result1.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # 根据工具名称选择对应的工具
        tool_map = {"add": add, "multiply": multiply, "search": search}
        if tool_name in tool_map:
            selected_tool = tool_map[tool_name]
            tool_result = selected_tool.invoke(tool_args)
            print(f"工具 {tool_name} 的结果: {tool_result}")
    
    print("\n示例2: 计算加法")
    result2 = llm_with_tools.invoke("计算25加17等于多少?")
    
    # 处理工具调用结果
    for tool_call in result2.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # 根据工具名称选择对应的工具
        tool_map = {"add": add, "multiply": multiply, "search": search}
        if tool_name in tool_map:
            selected_tool = tool_map[tool_name]
            tool_result = selected_tool.invoke(tool_args)
            print(f"工具 {tool_name} 的结果: {tool_result}")
    
    print("\n示例3: 搜索信息")
    result3 = llm_with_tools.invoke("帮我搜索一下关于人工智能的信息")
    
    # 处理工具调用结果
    for tool_call in result3.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # 根据工具名称选择对应的工具
        tool_map = {"add": add, "multiply": multiply, "search": search}
        if tool_name in tool_map:
            selected_tool = tool_map[tool_name]
            tool_result = selected_tool.invoke(tool_args)
            print(f"工具 {tool_name} 的结果: {tool_result}")

# 运行示例
if __name__ == "__main__":
    test_llm_with_tools()

