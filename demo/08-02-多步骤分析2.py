"""
客户反馈智能分析系统

这个系统演示了一个有实际商业价值的多步骤分析链条：

客户反馈文本
    |
    v
+---------------------------+
| 1. 问题分类与提取         |
| (产品/服务/价格/体验等)   |
+---------------------------+
    |
    v
+---------------------------+
| 2. 情感强度分析           |
| (1-10分 + 关键词)        |
+---------------------------+
    |
    v
+---------------------------+
| 3. 紧急程度评估           |
| (高/中/低 + 理由)        |
+---------------------------+
    |
    v
+---------------------------+
| 4. 行动建议生成           |
| (具体的业务改进方案)      |
+---------------------------+
    |
    v
结构化的分析报告 + 可执行的行动计划
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv
import json
import re

load_dotenv()
model = ChatOpenAI(temperature=0.3)  # 降低温度以获得更一致的结果

class CustomerFeedbackAnalyzer:
    """客户反馈智能分析器"""
    
    def __init__(self):
        self.model = model
        self.analysis_results = {}
    
    def create_analysis_chain(self):
        """创建完整的客户反馈分析链"""
        
        # 步骤1：问题分类与提取
        category_prompt = ChatPromptTemplate.from_template(
            """
            请分析以下客户反馈，识别并分类其中提到的问题：
            
            反馈内容：{feedback}
            
            请按以下格式输出：
            问题类别：[产品质量/客户服务/价格/物流配送/用户体验/功能需求/其他]
            核心问题：[用一句话概括主要问题]
            涉及领域：[具体的产品线或服务环节]
            """
        )
        
        # 步骤2：情感强度分析
        sentiment_prompt = ChatPromptTemplate.from_template(
            """
            基于客户反馈和问题分类结果，进行情感强度分析：
            
            原始反馈：{original_feedback}
            问题分类：{category_result}
            
            请按以下格式输出：
            情感倾向：[积极/中性/消极]
            强度评分：[1-10分，10分为最强烈]
            情感关键词：[提取2-3个最能体现情感的词语]
            客户满意度：[很满意/满意/一般/不满意/很不满意]
            """
        )
        
        # 步骤3：紧急程度评估
        urgency_prompt = ChatPromptTemplate.from_template(
            """
            基于问题分类和情感分析结果，评估此反馈的紧急处理程度：
            
            问题分类：{category_result}
            情感分析：{sentiment_result}
            
            考虑因素：
            - 问题严重性（影响使用/安全/财务）
            - 客户情感强度
            - 潜在的传播风险
            - 解决难度和时效性
            
            请按以下格式输出：
            紧急等级：[高/中/低]
            响应时限：[2小时内/24小时内/3天内/1周内]
            风险评估：[高风险/中风险/低风险]
            理由说明：[简要说明紧急程度判断依据]
            """
        )
        
        # 步骤4：行动建议生成
        action_prompt = ChatPromptTemplate.from_template(
            """
            基于完整分析结果，生成具体的行动建议：
            
            问题分类：{category_result}
            情感分析：{sentiment_result}
            紧急程度：{urgency_result}
            
            请生成详细的行动计划：
            
            立即行动：
            - [需要立即执行的具体措施]
            
            短期措施（1周内）：
            - [短期内需要完成的改进措施]
            
            长期优化（1个月内）：
            - [长期的系统性改进建议]
            
            责任部门：[建议由哪个部门负责处理]
            预期效果：[预期能达到的改善效果]
            跟进方式：[建议的客户跟进方法]
            """
        )
        
        # 构建完整的分析链
        analysis_chain = (
            # 步骤1：问题分类
            RunnablePassthrough.assign(
                category_result=category_prompt | self.model | StrOutputParser()
            )
            # 步骤2：情感分析
            | RunnablePassthrough.assign(
                sentiment_result=RunnableLambda(lambda x: (
                    sentiment_prompt | self.model | StrOutputParser()
                ).invoke({
                    "original_feedback": x["feedback"],
                    "category_result": x["category_result"]
                }))
            )
            # 步骤3：紧急程度评估
            | RunnablePassthrough.assign(
                urgency_result=RunnableLambda(lambda x: (
                    urgency_prompt | self.model | StrOutputParser()
                ).invoke({
                    "category_result": x["category_result"],
                    "sentiment_result": x["sentiment_result"]
                }))
            )
            # 步骤4：行动建议
            | RunnableLambda(lambda x: {
                **x,
                "action_plan": (action_prompt | self.model | StrOutputParser()).invoke({
                    "category_result": x["category_result"],
                    "sentiment_result": x["sentiment_result"],
                    "urgency_result": x["urgency_result"]
                })
            })
        )
        
        return analysis_chain
    
    def analyze_feedback(self, feedback_text, debug=True):
        """
        分析客户反馈
        
        Args:
            feedback_text (str): 客户反馈文本
            debug (bool): 是否显示调试信息
            
        Returns:
            dict: 完整的分析结果
        """
        chain = self.create_analysis_chain()
        result = chain.invoke({"feedback": feedback_text})
        
        if debug:
            self.print_analysis_results(feedback_text, result)
        
        return result
    
    def print_analysis_results(self, original_feedback, results):
        """格式化打印分析结果"""
        print("=" * 80)
        print("📝 客户反馈智能分析报告")
        print("=" * 80)
        
        print(f"\n📋 原始反馈:\n{original_feedback}")
        
        print(f"\n🏷️  步骤1 - 问题分类与提取:")
        print(f"{results['category_result']}")
        
        print(f"\n😊 步骤2 - 情感强度分析:")
        print(f"{results['sentiment_result']}")
        
        print(f"\n🚨 步骤3 - 紧急程度评估:")
        print(f"{results['urgency_result']}")
        
        print(f"\n💡 步骤4 - 行动建议:")
        print(f"{results['action_plan']}")
        
        print("=" * 80)

def main():
    """主函数，测试不同类型的客户反馈"""
    
    analyzer = CustomerFeedbackAnalyzer()
    
    # 测试案例1：产品质量问题（高紧急度）
    feedback_1 = """
    我昨天收到的智能手表出现了严重问题！开机后屏幕一直闪烁，根本无法正常使用。
    我是花了2000多块钱买的，结果连基本功能都用不了。客服电话也一直占线，
    完全联系不上人。这种质量真的让人很失望，我要求立即退货并给出合理解释！
    如果不能妥善处理，我会在各大平台投诉。
    """
    
    print("🔍 分析案例1：产品质量问题")
    analyzer.analyze_feedback(feedback_1)
    
    # # 测试案例2：服务体验问题（中等紧急度）
    # feedback_2 = """
    # 整体来说产品还不错，但是有几个地方希望能改进一下。首先是物流速度比较慢，
    # 订单显示3-5天到货，实际用了8天才收到。其次是包装可以再精美一些，
    # 作为礼品送人的话现在的包装显得有点简陋。客服态度还算可以，
    # 但是专业度有待提高，有些技术问题回答得不够准确。希望你们能继续优化。
    # """
    
    # print("\n🔍 分析案例2：服务体验问题")
    # analyzer.analyze_feedback(feedback_2)
    
    # # 测试案例3：功能需求建议（低紧急度）
    # feedback_3 = """
    # 用了一个月的app，整体体验很好，界面设计很清爽，功能也比较齐全。
    # 有个小建议：能不能增加夜间模式？晚上使用的时候觉得有点刺眼。
    # 另外，如果能增加数据导出功能就更完美了，这样我就能把数据备份到其他地方。
    # 总的来说很满意，会推荐给朋友使用的。期待后续版本的更新！
    # """
    
    # print("\n🔍 分析案例3：功能需求建议")
    # analyzer.analyze_feedback(feedback_3)

if __name__ == "__main__":
    main()