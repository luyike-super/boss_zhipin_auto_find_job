"""
多步骤的分析: 如何把上一步的输出作为下一步的输入?
    解决方法：
        1. 使用RunnablePassthrough.assign将上一步的输出作为下一步的输入 , 优点是自己指定的字段， 完全可控。
        2. 使用RunnableLambda将上一步的输出作为下一步的输入
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv

# 加载环境变量 (例如 OPENAI_API_KEY)
load_dotenv()

# 初始化语言模型
model = ChatOpenAI()

def create_analysis_chain():
    """
    创建一个完整的分析链条，包含两个步骤：
    1. 情感分析
    2. 基于情感分析结果生成改进建议
    """
    
    # 步骤1：情感分析提示模板
    sentiment_prompt = ChatPromptTemplate.from_template(
        "分析以下文本的情感，简洁地描述情感倾向：{text}"
    )
    
    # 步骤2：改进建议提示模板
    improvement_prompt = ChatPromptTemplate.from_template(
        "基于情感分析结果：{sentiment}\n"
        "为原文本提供具体的改进建议：{original_text}"
    )
    def log_messages(messages: any) -> any:
        print(messages)
        return messages
    
    # 构建完整的分析链
    analysis_chain = (
        # 保持原始输入，同时获取情感分析结果
        RunnablePassthrough.assign(
            sentiment=sentiment_prompt | model | StrOutputParser() | RunnableLambda(log_messages)
        )
        # 重新映射数据结构，为改进建议步骤准备输入
        | RunnableLambda(lambda x: {
            "sentiment": x["sentiment"],
            "original_text": x["text"]
        })
        # 生成改进建议
        | improvement_prompt 
        | model 
        | StrOutputParser()
    )
    
    return analysis_chain

def run_sentiment_analysis(text_to_analyze):
    """
    运行情感分析链条
    
    Args:
        text_to_analyze (str): 要分析的文本
        
    Returns:
        str: 改进建议
    """
    chain = create_analysis_chain()
    result = chain.invoke({"text": text_to_analyze})
    return result

def main():
    """主函数，运行示例"""
    
    # 测试用例1：正面情感
    test_text_1 = "这个产品太棒了，我非常喜欢！"
    print("=" * 50)
    print(f"原始文本: {test_text_1}")
    suggestion_1 = run_sentiment_analysis(test_text_1)
    print(f"改进建议: {suggestion_1}")
    
    # 测试用例2：负面情感
    test_text_2 = "我对这个服务感到非常失望。"
    print("\n" + "=" * 50)
    print(f"原始文本: {test_text_2}")
    suggestion_2 = run_sentiment_analysis(test_text_2)
    print(f"改进建议: {suggestion_2}")
    
    # 测试用例3：中性带问题的情感
    test_text_3 = "我觉得这个功能有点难用，而且经常出错。"
    print("\n" + "=" * 50)
    print(f"原始文本: {test_text_3}")
    suggestion_3 = run_sentiment_analysis(test_text_3)
    print(f"改进建议: {suggestion_3}")

if __name__ == "__main__":
    main()