"""
LangChain中的自定义处理逻辑示例

本示例展示如何在LangChain的LCEL（LangChain表达式语言）中使用自定义处理逻辑来增强AI应用。
重点讲解RunnableLambda的使用方法和应用场景。
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from datetime import datetime
import json
from dotenv import load_dotenv
import functools
import traceback

# 加载环境变量（包含API密钥）
load_dotenv()

# 添加一个全局变量用于存储extract_keywords的结果
_extract_keywords_result = {}

# 添加一个错误处理装饰器
def safe_execution(func):
    """装饰器：捕获并打印函数执行过程中的错误"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"错误发生在 {func.__name__}: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            # 返回一个默认值，避免程序崩溃
            return {"error": str(e)}
    return wrapper

def demo_basic_usage():
    """
    1. RunnableLambda 基础用法
    展示如何在链中添加简单的文本处理函数
    """
    print("\n=== 基础用法示例 ===")
    
    # 基础模型设置
    model = ChatOpenAI()
    output_parser = StrOutputParser()
    
    # 定义一个简单的处理函数
    def add_prefix(text):
        """为文本添加前缀"""
        return "处理结果: " + text
    
    # 创建一个基础链
    prompt = ChatPromptTemplate.from_template("生成一个关于{topic}的短句")
    base_chain = prompt | model | output_parser
    
    # 添加自定义处理逻辑
    enhanced_chain = base_chain | RunnableLambda(add_prefix)
    
    # 执行链
    result = enhanced_chain.invoke({"topic": "人工智能"})
    print(result)

def demo_json_processing():
    """
    2. 复杂数据处理
    展示如何处理JSON数据和进行数据转换
    """
    print("\n=== JSON处理示例 ===")
    
    model = ChatOpenAI()
    output_parser = StrOutputParser()
    
    # 创建一个要求模型输出JSON格式的提示
    json_prompt = ChatPromptTemplate.from_template(
        """生成一个关于{topic}的短句。
        请以JSON格式返回，包含以下字段：'sentence', 'length', 'sentiment'。
        sentiment应为'positive', 'neutral', 或'negative'。"""
    )
    
    def process_json_response(text):
        """处理JSON响应并增强数据"""
        try:
            # 尝试解析JSON
            data = json.loads(text)
            
            # 增强数据
            data["word_count"] = len(data.get("sentence", "").split())
            data["processed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 转换情感值为中文
            sentiment_map = {
                "positive": "积极",
                "neutral": "中性",
                "negative": "消极"
            }
            data["sentiment_cn"] = sentiment_map.get(data.get("sentiment"), "未知")
            
            return data
        except json.JSONDecodeError:
            return {"error": "无法解析JSON", "raw_text": text}
    
    # 创建带有JSON处理的链
    json_chain = json_prompt | model | output_parser | RunnableLambda(process_json_response)
    
    # 执行链
    json_result = json_chain.invoke({"topic": "机器学习"})
    print(json_result)

def demo_external_api():
    """
    3. 使用外部API增强响应
    展示如何集成外部服务
    """
    print("\n=== 外部API集成示例 ===")
    
    model = ChatOpenAI()
    output_parser = StrOutputParser()
    
    def get_weather(city):
        """模拟获取城市天气信息"""
        # 在实际应用中，这里会调用真实的天气API
        weather_data = {
            "北京": {"temperature": 22, "condition": "晴朗"},
            "上海": {"temperature": 26, "condition": "多云"},
            "广州": {"temperature": 30, "condition": "阵雨"},
            "深圳": {"temperature": 29, "condition": "晴朗"}
        }
        return weather_data.get(city, {"temperature": 25, "condition": "未知"})
    
    def enhance_with_weather(input_dict):
        """根据城市名添加天气信息"""
        city = input_dict.get("city", "")
        weather = get_weather(city)
        
        return {
            "city": city,
            "weather": weather,
            "query": input_dict.get("query", "")
        }
    
    # 定义一个建议提示模板
    suggestion_prompt = ChatPromptTemplate.from_template(
        """根据以下信息提供旅行建议：
        城市: {city}
        天气: 温度 {weather.temperature}°C, 天气状况 {weather.condition}
        查询: {query}
        
        提供针对这座城市当前天气的具体旅行建议。"""
    )
    
    # 创建完整链条
    travel_chain = (
        RunnableLambda(enhance_with_weather)
        | suggestion_prompt
        | model
        | output_parser
    )
    
    # 执行链
    travel_result = travel_chain.invoke({"city": "北京", "query": "周末旅行计划"})
    print(travel_result)

def demo_conditional_logic():
    """
    4. 条件逻辑处理
    展示如何根据不同条件执行不同的处理逻辑
    """
    print("\n=== 条件逻辑示例 ===")
    
    model = ChatOpenAI()
    output_parser = StrOutputParser()
    
    def route_by_language(input_dict):
        """根据指定的语言决定使用哪个提示模板"""
        language = input_dict.get("language", "chinese").lower()
        content = input_dict.get("content", "")
        
        templates = {
            "chinese": f"请用中文总结以下内容：{content}",
            "english": f"Please summarize the following content in English: {content}",
            "french": f"Veuillez résumer le contenu suivant en français: {content}"
        }
        
        return {"template": templates.get(language, templates["chinese"])}
    
    # 创建动态提示模板
    dynamic_prompt = ChatPromptTemplate.from_template("{template}")
    
    # 创建多语言总结链
    multilingual_chain = (
        RunnableLambda(route_by_language)
        | dynamic_prompt
        | model
        | output_parser
    )
    
    # 测试不同语言
    test_text = "人工智能(AI)是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"
    
    print("中文结果:")
    chinese_result = multilingual_chain.invoke({
        "language": "chinese", 
        "content": test_text
    })
    print(chinese_result)
    
    print("\n英文结果:")
    english_result = multilingual_chain.invoke({
        "language": "english", 
        "content": test_text
    })
    print(english_result)

def demo_logging():
    """
    5. 日志记录和监控
    展示如何添加日志记录功能
    """
    print("\n=== 日志记录示例 ===")
    
    model = ChatOpenAI()
    output_parser = StrOutputParser()
    
    def log_interaction(input_dict):
        """记录互动并返回原始输入"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 接收到查询: {input_dict}")
        return input_dict
    
    def log_output(output):
        """记录输出结果并返回原始输出"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 生成响应: {output[:50]}...")
        return output
    
    # 创建带日志记录的链
    logging_chain = (
        RunnableLambda(log_interaction)
        | ChatPromptTemplate.from_template("对'{text}'进行情感分析")
        | model
        | output_parser
        | RunnableLambda(log_output)
    )
    
    # 执行链
    logging_result = logging_chain.invoke({"text": "这款产品非常好用，超出了我的预期！"})
    print("\n完整结果:")
    print(logging_result)

def demo_multi_stage():
    """
    6. 综合应用：多阶段处理链
    展示如何构建复杂的多阶段处理流程
    """
    print("\n=== 多阶段处理链示例 ===")
    
    # 使用较高温度设置，以增加创造性
    model = ChatOpenAI(temperature=0.7)
    output_parser = StrOutputParser()
    
    @safe_execution
    def extract_keywords(text):
        """从文本中提取关键词(模拟)"""
        # 此处简化处理，实际应用中可能使用NLP库
        words = text.split()
        # 模拟提取关键词
        keywords = [word for word in words if len(word) > 3][:5]
        print(f"提取的关键词: {keywords}")
        # 存储结果到全局变量
        global _extract_keywords_result
        _extract_keywords_result = {"original_text": text, "keywords": keywords}
        return _extract_keywords_result
    
    # 第二步：增强关键词
    keyword_prompt = ChatPromptTemplate.from_template(
        """原文：{original_text}
        
        从上述文本中提取的关键词有：{keywords}
        
        请扩展这些关键词，为每个关键词提供相关的术语或同义词。
        
        严格按照以下JSON格式返回，不要添加任何其他解释:
        {{
          "关键词1": ["相关术语1", "相关术语2", ...],
          "关键词2": ["相关术语1", "相关术语2", ...],
          ...
        }}"""
    )
    
    # 第四步：生成最终内容
    final_prompt = ChatPromptTemplate.from_template(
        """请使用以下扩展关键词为基础，撰写一篇关于原始文本的详细说明：
        
        原文：{original_text}
        关键词扩展：{keyword_expansion}
        
        生成的内容应该专业、全面，并且包含这些关键词及其相关术语。"""
    )
    
    # 组合完整的多阶段链
    multi_stage_chain = (
        RunnableLambda(extract_keywords)
        | keyword_prompt
        | model
        | JsonOutputParser()  # 使用LCEL内置的JSON解析器
        | RunnableLambda(lambda json_data: {"keyword_expansion": json_data, "original_text": _extract_keywords_result["original_text"]})
        | final_prompt
        | model
        | output_parser
    )
    
    # 执行多阶段链
    complex_result = multi_stage_chain.invoke(
        "深度学习是人工智能的一个分支，它基于人工神经网络的结构和功能来模拟人脑学习过程。"
    )
    print(complex_result)

def main():
    """主函数：运行所有示例"""
    print("开始运行LangChain自定义处理逻辑示例...")
    
    # 运行各个示例

    demo_multi_stage()
    
    print("\n所有示例运行完成！")

if __name__ == "__main__":
    main() 