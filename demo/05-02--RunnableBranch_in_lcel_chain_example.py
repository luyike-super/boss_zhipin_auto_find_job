from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化大语言模型
model = ChatOpenAI()

# 初始化输出解析器
output_parser = StrOutputParser()

# --- 定义 RunnableBranch 中使用的子链 ---

# 1. 回答问题的链
prompt_question = ChatPromptTemplate.from_template("请回答以下问题： {question}")
chain_question = prompt_question | model | output_parser

# 2. 总结文本的链
prompt_summarize = ChatPromptTemplate.from_template("请总结以下文本：\n\n{text_to_summarize}")
chain_summarize = prompt_summarize | model | output_parser

# 3. 默认链
def handle_default(input_dict):
    return f"无法识别的操作。原始输入：{input_dict.get('original_input', input_dict)}"

chain_default = RunnableLambda(handle_default)

# --- 构建 RunnableBranch ---
conditional_branch = RunnableBranch(
    (lambda x: "question" in x and x["question"], chain_question),
    (lambda x: "text_to_summarize" in x and x["text_to_summarize"], chain_summarize),
    chain_default
)

# --- 构建完整的 LCEL 链，将 RunnableBranch 集成在内 ---

# 1. 预处理步骤：根据输入类型决定如何构造 branch 的输入
def preprocess_input(raw_input: dict) -> dict:
    """根据 raw_input 的内容，决定下一步是提问还是总结，或者其他。"""
    if "query" in raw_input and raw_input["query"]:
        # 如果输入包含 'query'，我们将其视为一个问题
        return {"question": raw_input["query"], "original_input": raw_input}
    elif "document" in raw_input and raw_input["document"]:
        # 如果输入包含 'document'，我们将其视为待总结文本
        return {"text_to_summarize": raw_input["document"], "original_input": raw_input}
    else:
        # 其他情况，直接传递，由 branch 的 default 处理
        return {"original_input": raw_input} 

preprocessor = RunnableLambda(preprocess_input)

# 2. 后处理步骤：对 branch 的输出进行格式化
def postprocess_output(branch_output: str) -> str:
    """对 RunnableBranch 的输出进行简单的格式化。"""
    return f"--- Agent 回答 ---\n{branch_output}\n--- 回答结束 ---"

postprocessor = RunnableLambda(postprocess_output)

# 3. 将所有部分组合成一个 LCEL 链
# 链的流程： 原始输入 -> 预处理器 -> 条件分支 -> 后处理器
integrated_lcel_chain = preprocessor | conditional_branch | postprocessor

# --- 测试集成的 LCEL 链 ---

# 测试用例 1: 输入一个问题
input_data_q = {"query": "什么是 LCEL？"}
result1 = integrated_lcel_chain.invoke(input_data_q)
print(f"输入: {input_data_q}")
print(f"集成链输出:\n{result1}")
print("="*30)

# 测试用例 2: 输入一段待总结文本
input_data_s = {"document": "LangChain Expression Language (LCEL) 是一种声明式的方式来组合链。LCEL 从第一天开始就被设计为支持将原型投入生产，无需代码更改，从最简单的\"提示+LLM\"链到最复杂的链（例如，我们已经看到人们在生产中成功运行具有数百个步骤的LCEL链）。"}
result2 = integrated_lcel_chain.invoke(input_data_s)
print(f"输入: {input_data_s}")
print(f"集成链输出:\n{result2}")
print("="*30)

# 测试用例 3: 输入一个无法被预处理器识别的类型
input_data_unknown = {"user_text": "随便聊聊天气吧。"}
result3 = integrated_lcel_chain.invoke(input_data_unknown)
print(f"输入: {input_data_unknown}")
print(f"集成链输出:\n{result3}")
print("="*30)

# 演示 RunnablePassthrough 如何在链中传递原始输入或特定字段
# 假设我们希望 branch 的输出能够访问到预处理器的输出，而不仅仅是其最终选择的路径结果

chain_with_passthrough = (
    preprocessor
    | RunnablePassthrough.assign(branch_result=conditional_branch) # 执行branch并将结果赋给新键
    | RunnableLambda(lambda x: f"预处理后输入: {x['original_input']}\n分支判断结果: {x['branch_result']}")
)

print("\n--- 带 Passthrough 的链演示 ---")
result_passthrough_q = chain_with_passthrough.invoke({"query": "Python有什么特点?"})
print(result_passthrough_q)

result_passthrough_s = chain_with_passthrough.invoke({"document": "Python是一种解释型、高级通用编程语言。"})
print(result_passthrough_s) 