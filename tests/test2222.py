import logging # 新增：标准日志模块
import sys # 新增：用于指定日志输出到stdout
from typing import Any # 新增：用于更准确的类型提示
from dotenv import load_dotenv
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

logger = logging.getLogger(__name__)

if
