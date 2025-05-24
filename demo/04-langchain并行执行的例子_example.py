from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量，通常OPENAI_API_KEY等会在这里设置
load_dotenv()

# 初始化大语言模型
model = ChatOpenAI()

# 初始化输出解析器
output_parser = StrOutputParser()

# 定义第一个提示模板和链
prompt1 = ChatPromptTemplate.from_template("请总结关于 {topic} 的主要观点。")
chain1 = prompt1 | model | output_parser

# 定义第二个提示模板和链
prompt2 = ChatPromptTemplate.from_template("针对 {topic} 这个主题，写一句有吸引力的标语。")
chain2 = prompt2 | model | output_parser

# 使用 RunnableParallel 定义并行处理链
# 这个并行链会同时执行 chain1 和 chain2
# "summary" 和 "slogan" 是并行链输出结果字典中的键
parallel_chain = RunnableParallel(
    summary=chain1,     
    slogan=chain2
)

# 定义一个主题
topic_to_discuss = "人工智能在教育领域的应用"

# 调用并行链
# .invoke() 方法的输入会同时传递给 parallel_chain 中的每一个分支 (chain1 和 chain2)
# 因此，chain1 和 chain2 中的 {topic} 变量都会被 topic_to_discuss 的值替换
result = parallel_chain.invoke({"topic": topic_to_discuss})

# 打印并行处理的结果
print(f"讨论主题: {topic_to_discuss}")
print(f"总结观点: {result['summary']}")
print(f"宣传标语: {result['slogan']}")

# 另一个例子，演示并行获取不同信息

prompt_joke = ChatPromptTemplate.from_template("给我讲一个关于程序员的笑话。")
chain_joke = prompt_joke | model | output_parser

prompt_fact = ChatPromptTemplate.from_template("告诉我一个关于Python语言的有趣事实。")
chain_fact = prompt_fact | model | output_parser

parallel_info_chain = RunnableParallel(
    joke=chain_joke,
    fact=chain_fact
)

# 调用并行链，这次不需要输入，因为提示模板中没有变量
info_result = parallel_info_chain.invoke({})

print("\n--- 另一个并行示例 ---")
print(f"程序员笑话: {info_result['joke']}")
print(f"Python趣闻: {info_result['fact']}") 