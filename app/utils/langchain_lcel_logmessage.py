from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
# from datetime import datetime # 已被logging模块的时间戳替代
import json
from dotenv import load_dotenv
import logging # 新增：标准日志模块
import sys # 新增：用于指定日志输出到stdout
from typing import Any # 新增：用于更准确的类型提示

load_dotenv()

# 企业级日志配置：在应用早期进行配置
logging.basicConfig(
    level=logging.INFO,  # 日志级别，INFO及以上会被记录
    format='%(asctime)s - %(levelname)s - [%(name)s:%(funcName)s:%(lineno)d] - %(message)s', # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S',  # 时间戳格式
    handlers=[
        logging.StreamHandler(sys.stdout)  # 日志输出到标准输出
        # 在实际企业应用中，可能还会添加 FileHandler, SysLogHandler, SentryHandler 等
    ]
)

# 获取当前模块的logger实例
module_logger = logging.getLogger(__name__)

def _json_serializer_default(obj: Any) -> Any:
    """
    自定义 JSON 序列化函数，用于处理 Pydantic 模型等特殊对象。
    """
    if hasattr(obj, 'model_dump'):  # 适用于 Pydantic V2 模型
        return obj.model_dump()
    if hasattr(obj, 'dict'):  # 适用于 Pydantic V1 模型
        return obj.dict()
    # 特殊处理 Langchain 的 ChatPromptValue (它不是 Pydantic 模型但包含 Pydantic 模型)
    if obj.__class__.__name__ == 'ChatPromptValue' and hasattr(obj, 'messages'):
        # messages 列表中的元素 (如 HumanMessage) 会被递归处理 (因为它们是 Pydantic 模型)
        return {"lc_type": "ChatPromptValue", "messages": obj.messages, "string_representation": str(obj)}
    
    # 如果有其他无法直接序列化的类型，可在此处添加处理逻辑
    # 例如: if isinstance(obj, datetime.date): return obj.isoformat()
    
    # 如果以上都不是，则让 json.dumps 抛出 TypeError
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable by _json_serializer_default")
 

def log_message(val: Any) -> Any: # 将类型提示从 dict 改为 Any，返回值也为 Any
    """
    企业级日志记录函数。
    使用标准 logging 模块记录 Langchain runnable chain 中间传递的数据。
    会尝试将数据序列化为 JSON 格式以便查看和分析。
    """
    try:
        # 尝试使用自定义序列化器将 val 转换为 JSON 字符串
        # ensure_ascii=False 支持中文等非ASCII字符正常显示
        # indent=2 使JSON输出更易读
        log_payload = json.dumps(val, ensure_ascii=False, indent=2, default=_json_serializer_default)
        message_to_log = f"Data in chain step:\n{log_payload}"
    except TypeError as te:
        # 如果自定义序列化器也无法处理（或者val本身不是复杂对象，而是字符串等）
        # 则回退到记录对象的字符串表示
        module_logger.debug(f"Value could not be fully serialized to JSON by custom serializer (TypeError: {te}). Falling back to str().")
        message_to_log = f"Data in chain step (raw representation for {type(val).__name__}):\n{str(val)}"
    except Exception as e:
        # 捕获其他可能的序列化错误
        module_logger.error(f"Unexpected error during serialization for logging: {e}")
        message_to_log = f"Data in chain step (serialization error, raw representation for {type(val).__name__}):\n{str(val)}"

    module_logger.info(message_to_log)
    return val

def demo_basic_usage():
    """
    基础用法示例
    """
    prompt = ChatPromptTemplate.from_template("生成一个关于{topic}的短句")
    model = ChatOpenAI()
    output_parser = StrOutputParser()

    chain = prompt | RunnableLambda(log_message) | model | RunnableLambda(log_message) | output_parser
    result = chain.invoke({"topic": "人工智能"})
    print(f"Final result: {result}") # 添加前缀以便区分最终结果和日志

def main():
    demo_basic_usage()

if __name__ == "__main__":
    main()
 