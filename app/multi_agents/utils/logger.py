import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

class AgentLogger:
    """
    智能体系统日志记录器
    
    提供统一的日志记录功能，支持控制台输出和文件记录
    可以记录不同级别的日志信息和不同智能体的操作
    """
    
    # 日志级别映射
    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    def __init__(self, name="agent_system", level="info", log_dir="logs"):
        """
        初始化日志记录器
        
        参数:
            name: 日志记录器名称
            level: 日志级别，可选值为debug, info, warning, error, critical
            log_dir: 日志文件保存目录
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVELS.get(level.lower(), logging.INFO))
        self.logger.propagate = False
        
        # 清除已有的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 添加文件处理器
        log_file = os.path.join(
            log_dir, 
            f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log(self, level, message, agent_name=None):
        """
        记录日志
        
        参数:
            level: 日志级别
            message: 日志消息
            agent_name: 智能体名称，可选
        """
        if agent_name:
            message = f"[{agent_name}] {message}"
            
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    
    def debug(self, message, agent_name=None):
        """记录调试级别日志"""
        self.log('debug', message, agent_name)
    
    def info(self, message, agent_name=None):
        """记录信息级别日志"""
        self.log('info', message, agent_name)
    
    def warning(self, message, agent_name=None):
        """记录警告级别日志"""
        self.log('warning', message, agent_name)
    
    def error(self, message, agent_name=None):
        """记录错误级别日志"""
        self.log('error', message, agent_name)
    
    def critical(self, message, agent_name=None):
        """记录严重错误级别日志"""
        self.log('critical', message, agent_name)
    
    def agent_transition(self, from_agent, to_agent, message=None):
        """
        记录智能体转换
        
        参数:
            from_agent: 源智能体名称
            to_agent: 目标智能体名称
            message: 额外信息，可选
        """
        transition_msg = f"Agent Transition: {from_agent} -> {to_agent}"
        if message:
            transition_msg += f" | {message}"
        self.info(transition_msg)
    
    def workflow_start(self, user_input):
        """记录工作流开始"""
        self.info(f"Workflow Started with input: {user_input}")
    
    def workflow_end(self, result=None):
        """记录工作流结束"""
        end_msg = "Workflow Ended"
        if result:
            end_msg += f" with result: {result}"
        self.info(end_msg)

# 创建默认日志记录器实例
default_logger = AgentLogger()

def get_logger(name=None, level=None, log_dir=None):
    """
    获取日志记录器实例
    
    参数:
        name: 日志记录器名称，可选
        level: 日志级别，可选
        log_dir: 日志目录，可选
    
    返回:
        日志记录器实例
    """
    if name is None and level is None and log_dir is None:
        return default_logger
    
    return AgentLogger(
        name=name or default_logger.logger.name,
        level=level or default_logger.logger.level,
        log_dir=log_dir or "logs"
    ) 