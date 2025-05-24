from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS # Using FAISS for in-memory vector store
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量 (主要是 OPENAI_API_KEY)
load_dotenv()

# --- 1. 创建示例文档 ---
docs = [
    Document(page_content="LangChain Expression Language (LCEL) 是一种声明式的方式来组合链。", metadata={"source": "LCEL 文档"}),
    Document(page_content="LCEL的设计目标是支持将原型快速投入生产，且无需更改代码。", metadata={"source": "LCEL 设计理念"}),
    Document(page_content="LCEL链支持流式处理、异步操作和批处理。", metadata={"source": "LCEL 特性"}),
    Document(page_content="RunnableParallel允许并行执行多个Runnable对象。", metadata={"source": "LCEL 组件"}),
    Document(page_content="RunnableBranch可以根据输入条件选择不同的执行路径。", metadata={"source": "LCEL 组件"})
]

# --- 2. 创建向量存储和检索器 ---
# 初始化 OpenAI 嵌入模型
embeddings = OpenAIEmbeddings()

# 使用 FAISS 从文档和嵌入模型创建内存向量存储
# FAISS (Facebook AI Similarity Search) 是一个用于高效相似性搜索和密集向量聚类的库。
vectorstore = FAISS.from_documents(docs, embeddings)

# 从向量存储创建一个检索器，用于检索与查询相关的文档
# search_kwargs={'k': 2} 表示我们希望检索器返回最相关的2个文档
retriever = vectorstore.as_retriever(search_kwargs={'k': 2})

# --- 3. 定义文档格式化函数 ---
def format_docs(docs_list: list[Document]) -> str:
    """将检索到的文档列表格式化为单个字符串，每个文档内容后跟其来源（如果存在）。"""
    formatted = []
    for doc in docs_list:
        source_info = f" (来源: {doc.metadata.get('source', '未知')})" if doc.metadata else ""
        formatted.append(f"- {doc.page_content}{source_info}")
    return "\n".join(formatted)

# --- 4. 创建 RAG 提示模板 ---
rag_prompt_template = """
请根据以下上下文信息来回答问题。
如果你在上下文中找不到答案，请直说你不知道，不要试图编造答案。
保持答案简洁。

上下文: 
{context}

问题: {question}

答案: 
"""
prompt = ChatPromptTemplate.from_template(rag_prompt_template)

# --- 5. 初始化模型和输出解析器 ---
llm = ChatOpenAI(temperature=0) # temperature=0 使得输出更具确定性
output_parser = StrOutputParser()

# --- 6. 构建 RAG 链 ---
# RAG 链的步骤:
# 1. 输入: 一个包含 "question" 键的字典。
# 2. `RunnableParallel` (或等效的字典结构) 用于并行处理：
#    a. 检索上下文: 通过 `retriever` 获取与问题相关的文档，然后用 `format_docs` 格式化它们。
#    b. 传递问题: 使用 `RunnablePassthrough` 直接将原始问题传递下去。
# 3. 将检索到的上下文和问题填充到 `prompt` 中。
# 4. 将填充后的提示传递给 `llm` 进行处理。
# 5. 使用 `output_parser` 解析 `llm` 的输出。

rag_chain = (
    RunnableParallel(
        context=(retriever | RunnableLambda(format_docs)), # 检索并格式化文档作为上下文
        question=RunnablePassthrough() # 直接传递问题
    )
    | prompt
    | llm
    | output_parser
)

# 另一种等效的写法，使用字典快捷方式代替 RunnableParallel
# rag_chain = (
#     {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
#     | prompt
#     | llm
#     | output_parser
# )


# --- 7. 调用 RAG 链并打印结果 ---
question1 = "LCEL是什么？"
print(f"问题: {question1}")
answer1 = rag_chain.invoke(question1)
print(f"RAG链回答: {answer1}")
print("-"*30)

question2 = "RunnableBranch有什么用？"
print(f"问题: {question2}")
answer2 = rag_chain.invoke(question2)
print(f"RAG链回答: {answer2}")
print("-"*30)

question3 = "并行链怎么实现？"
print(f"问题: {question3}")
answer3 = rag_chain.invoke(question3)
print(f"RAG链回答: {answer3}")
print("-"*30)

question4 = "Python是什么语言？" # 这个问题在上下文中没有答案
print(f"问题: {question4}")
answer4 = rag_chain.invoke(question4)
print(f"RAG链回答: {answer4}")
print("-"*30)

# 如果想查看检索器返回的原始文档，可以单独调用 retriever
retrieved_docs_for_q1 = retriever.invoke(question1)
print(f"\n为问题 '{question1}' 检索到的文档:")
for doc in retrieved_docs_for_q1:
    print(f"  - 内容: {doc.page_content}, 元数据: {doc.metadata}") 