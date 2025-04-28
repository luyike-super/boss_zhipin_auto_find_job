import logging
from langchain_community.tools.file_management import WriteFileTool
from app.utils import create_logged_tool
# 优点带日志
# 日志工具类
# py项目通用找个


logger = logging.getLogger(__name__)

# Initialize file management tool with logging
LoggedWriteFile = create_logged_tool(WriteFileTool)
write_file_tool = LoggedWriteFile()

