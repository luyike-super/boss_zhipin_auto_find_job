from typing import Dict, Type, Optional, Any, Mapping
from abc import ABC, abstractmethod
from enum import Enum, auto
import os
from app.config.config_ai import (
    DEEPSEEK_API_KEY, DEEPSEEK_API_BASE, DEEPSEEK_MODEL,
    DASHSCOPE_API_KEY, QWEN_MODEL
)

class LLMProviderType(Enum):
    """LLM提供商类型枚举"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    QIANWEN = "qianwen"
    
    def __str__(self) -> str:
        return self.value 


class ThinkingLevel(Enum):
    """思考级别枚举"""
    SIMPLE = "简单"
    BASIC = "基础"
    ADVANCED = "高级"
    DEEP = "深度思考"
    
    def __str__(self) -> str:
        return self.value


class LLMProvider(ABC):
    """LLM提供商的抽象基类，定义所有LLM提供商必须实现的接口"""
    
    @abstractmethod
    def get_llm(self, **kwargs) -> Any:
        """返回配置好的LLM实例"""
        pass

class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        from langchain_deepseek import ChatDeepSeek
        print("=="*200)
        print(DEEPSEEK_API_KEY)
        print(DEEPSEEK_API_BASE)
        print(DEEPSEEK_MODEL)
        # 默认配置
        config = {
            "api_key": DEEPSEEK_API_KEY,
            "api_base": DEEPSEEK_API_BASE,
            "model": DEEPSEEK_MODEL,
            "temperature": 0,
            "max_tokens": None,
            "timeout": 120,
            "max_retries": 5,
            "default_headers": {"Connection": "keep-alive"}
        }
        
        # 使用传入的参数覆盖默认配置
        config.update(kwargs)
        
        return ChatDeepSeek(**config)

class OpenAIProvider(LLMProvider):
    """OpenAI LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        pass

class QianWenProvider(LLMProvider):
    """千问 LLM提供商实现"""
    
    def get_llm(self, **kwargs) -> Any:
        """
        通义千问（Qwen）LLM实现，基于 langchain_openai.ChatOpenAI
        支持参数：api_key, model, temperature, max_tokens 等
        """
        from langchain_openai import ChatOpenAI
        # 优先使用传入的 api_key，否则用配置文件中的
        api_key = kwargs.pop("api_key", None) or DASHSCOPE_API_KEY
        if api_key:
            os.environ["DASHSCOPE_API_KEY"] = api_key
        print(api_key)
        # 配置基本参数
        model = kwargs.pop("model", QWEN_MODEL)
        temperature = kwargs.pop("temperature", 0)
        max_tokens = kwargs.pop("max_tokens", None)
        
        # 创建 ChatOpenAI 实例
        return ChatOpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


class LLMFactory:
    """LLM工厂类，用于创建不同的LLM实例"""
    
    # 注册所有可用的LLM提供商
    _providers: Dict[LLMProviderType, Type[LLMProvider]] = {
        LLMProviderType.DEEPSEEK: DeepSeekProvider,
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.QIANWEN: QianWenProvider
    }
    
    @classmethod
    def register_provider(cls, provider_type: LLMProviderType, provider_class: Type[LLMProvider]) -> None:
        """注册新的LLM提供商"""
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def create_llm(cls, provider_type: LLMProviderType, **kwargs) -> Any:
        """
        根据提供商类型创建对应的LLM实例
        
        Args:
            provider_type: LLM提供商类型枚举
            **kwargs: 可选的配置参数，会覆盖默认配置
                - temperature: 温度参数，控制生成文本的随机性
                - model: 模型名称
                - max_tokens: 最大生成token数
                - 其他特定LLM提供商的参数
        
        Returns:
            配置好的LLM实例
        """
        if provider_type not in cls._providers:
            raise ValueError(f"不支持的LLM提供商: {provider_type}")
        
        provider = cls._providers[provider_type]()
        return provider.get_llm(**kwargs)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取所有可用的LLM提供商列表"""
        return list(cls._providers.keys()) 
    

# 简单、基础、高级、深度思考
def get_llm_by_type(thinking_level: ThinkingLevel = ThinkingLevel.BASIC, **kwargs) -> Any:
    """
    根据思考级别创建LLM实例，不同思考级别使用不同的LLM提供商
    
    Args:
        thinking_level: 思考级别枚举
        **kwargs: 其他可选参数
        
    Returns:
        配置好的LLM实例
    """
    match thinking_level:
        case ThinkingLevel.SIMPLE:
            config = {
                "temperature": 0.3,
                "max_tokens": 512
            }
            config.update(kwargs)
            return LLMFactory.create_llm(LLMProviderType.QIANWEN, **config)
            
        case ThinkingLevel.BASIC:
            config = {
                "temperature": 0.2,
                "max_tokens": 1024
            }
            config.update(kwargs)
            return LLMFactory.create_llm(LLMProviderType.DEEPSEEK, **config)
            
        case ThinkingLevel.ADVANCED:
            config = {
                "temperature": 0.1,
                "max_tokens": 2048
            }
            config.update(kwargs)
            return LLMFactory.create_llm(LLMProviderType.OPENAI, **config)
            
        case ThinkingLevel.DEEP:
            config = {
                "temperature": 0,
                "max_tokens": 4096
            }
            config.update(kwargs)
            return LLMFactory.create_llm(LLMProviderType.DEEPSEEK, **config)
            
        case _:
            # 默认使用基础配置和DeepSeek提供商
            config = {
                "temperature": 0.2,
                "max_tokens": 1024
            }
            config.update(kwargs)
            return LLMFactory.create_llm(LLMProviderType.DEEPSEEK, **config) 
