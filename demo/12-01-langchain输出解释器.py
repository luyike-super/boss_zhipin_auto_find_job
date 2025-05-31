import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain.schema.runnable import RunnableLambda

# 加载环境变量
load_dotenv()

class PersonInfo(BaseModel):
    name: str = Field(description="人物姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")

# 创建解析器
parser = PydanticOutputParser(pydantic_object=PersonInfo)


# 获取格式指令
format_instructions = parser.get_format_instructions()

# 构建提示模板
template = """
请提取以下文本中的人物信息：

文本：{text}

{format_instructions}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["text"],
    partial_variables={"format_instructions": format_instructions}
)

# 打印提示词示例
example_text = "张小明是一位30岁的软件工程师"
print(prompt.format(text=example_text))

# 初始化语言模型
model = ChatOpenAI(temperature=0)

# 构建调用链 - 在模型输出后应用自定义处理函数
chain = prompt | model  | parser

# 执行并获取结构化结果
result = chain.invoke({"text": "张小明是一位30岁的软件工程师"})

print("\n解析结果:")
print(f"姓名: {result.name}")
print(f"年龄: {result.age}")
print(f"职业: {result.occupation}")

# 尝试另一个例子
print("\n另一个例子:")
another_result = chain.invoke({"text": "李华今年25岁，是一名大学教师"})
print(f"姓名: {another_result.name}")
print(f"年龄: {another_result.age}")
print(f"职业: {another_result.occupation}")

