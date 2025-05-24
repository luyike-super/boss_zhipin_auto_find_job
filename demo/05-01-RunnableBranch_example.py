from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化大语言模型
model = ChatOpenAI()

# 初始化输出解析器
output_parser = StrOutputParser()

# --- 定义子链 ---

# 1. 回答问题的链
prompt_question = ChatPromptTemplate.from_template("你是一个乐于助人的助手。请回答以下问题： {question}")
chain_question = prompt_question | model | output_parser

# 2. 总结文本的链
prompt_summarize = ChatPromptTemplate.from_template("请将以下文本总结为一段话：\n\n{text_to_summarize}")
chain_summarize = prompt_summarize | model | output_parser

# 3. 默认链 (当其他条件都不满足时执行)
def handle_default(input_dict):
    return f"无法处理该类型的请求。收到的输入是：{input_dict}"

chain_default = RunnableLambda(handle_default)

# --- 构建 RunnableBranch ---

# RunnableBranch 接受一个元组列表作为参数
# 每个元组包含： (条件函数, 要执行的链)
# 条件函数接收 RunnableBranch 的输入，并返回 True 或 False
# RunnableBranch 会按顺序评估这些条件，并执行第一个条件为 True 的链
# 最后一个参数是当所有条件都为 False 时执行的默认链

conditional_branch = RunnableBranch(
    # 判断 "question" 这个键是否在字典 x 中，并且 x["question"] 的值是否为真（非空、非None、非False等）。
    (lambda x: "question" in x and x["question"], chain_question),  # 如果输入包含有效的 "question"
    (lambda x: "text_to_summarize" in x and x["text_to_summarize"], chain_summarize), # 如果输入包含有效的 "text_to_summarize"
    chain_default  # 默认链
)

# --- 测试 RunnableBranch ---

# 示例 1: 输入一个问题
input_q = {"question": "LangChain是什么？它有什么主要特点？"}
result_q = conditional_branch.invoke(input_q)
print(f"输入: {input_q}")
print(f"回答: {result_q}")
print("-"*20)

# 示例 2: 输入一段待总结的文本
input_s = {"text_to_summarize": "LangChain是一个用于构建基于大型语言模型（LLM）的应用程序的框架。它提供了模块化的组件和工具，简化了LLM应用的开发流程，包括提示管理、链式调用、数据增强生成、代理和内存等功能。"}
result_s = conditional_branch.invoke(input_s)
print(f"输入: {input_s}")
print(f"总结: {result_s}")
print("-"*20)

# 示例 3: 输入一个不符合任何已知条件的字典
input_unknown = {"topic": "一个未知的主题"}
result_unknown = conditional_branch.invoke(input_unknown)
print(f"输入: {input_unknown}")
print(f"响应: {result_unknown}")
print("-"*20)

# 示例 4: 输入一个空字典，或者不包含预期键的字典
input_empty = {}
result_empty = conditional_branch.invoke(input_empty)
print(f"输入: {input_empty}")
print(f"响应: {result_empty}")
print("-"*20)

input_other_key = {"message": "你好"}
result_other_key = conditional_branch.invoke(input_other_key)
print(f"输入: {input_other_key}")
print(f"响应: {result_other_key}") 


