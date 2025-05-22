import sqlite3
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from app.utils import create_logged_tool, log_func


class PinQueryInput(BaseModel):
    """电路引脚查询输入参数"""
    component_id: str = Field(..., description="元件ID")
    pin_name: Optional[str] = Field(None, description="引脚名称，不提供则返回所有引脚")


class SQLQueryInput(BaseModel):
    """SQL查询输入参数"""
    sql: str = Field(..., description="SQL查询语句")
    params: Optional[List[Any]] = Field(None, description="SQL参数")


class DBConnection:
    """数据库连接管理类"""
    
    _instance = None
    
    def __new__(cls, db_path: str = "data/circuit.db"):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            cls._instance.db_path = db_path
        return cls._instance
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)


class DBQueryTool:
    """数据库查询工具，提供电路引脚数据查询功能"""
    
    def __init__(self, db_connection: DBConnection = None):
        """初始化数据库连接
        
        Args:
            db_connection: 数据库连接，默认创建新连接
        """
        self.db_connection = db_connection or DBConnection()
    
    @log_func(level="DEBUG")
    def query_pin_table(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """查询电路引脚表
        
        Args:
            args: 查询参数，包含component_id和可选的pin_name
        
        Returns:
            查询结果字典
        """
        input_data = PinQueryInput(**args)
        
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            
            if input_data.pin_name:
                query = "SELECT * FROM pin_table WHERE component_id = ? AND pin_name = ?"
                cursor.execute(query, (input_data.component_id, input_data.pin_name))
            else:
                query = "SELECT * FROM pin_table WHERE component_id = ?"
                cursor.execute(query, (input_data.component_id,))
            
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return {"status": "success", "data": results}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @log_func(level="DEBUG")
    def execute_sql(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行SQL查询
        
        Args:
            args: SQL查询参数，包含sql和可选的params
        
        Returns:
            查询结果字典
        """
        input_data = SQLQueryInput(**args)
        
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()
            
            if input_data.params:
                cursor.execute(input_data.sql, input_data.params)
            else:
                cursor.execute(input_data.sql)
            
            # 检查是否有结果集
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                result_type = "query"
            else:
                # 对于非查询操作，返回受影响的行数
                results = {"rows_affected": cursor.rowcount}
                result_type = "update"
            
            conn.commit()
            conn.close()
            return {
                "status": "success", 
                "type": result_type,
                "data": results
            }
        
        except Exception as e:
            return {"status": "error", "message": str(e)}


# 创建LangChain工具
class PinQueryTool(BaseTool):
    """查询电路引脚表的工具"""
    name = "query_pin_table"
    description = "查询电路引脚表，需要提供元件ID和可选的引脚名称"
    args_schema = PinQueryInput
    
    def __init__(self, db_tool: DBQueryTool = None):
        super().__init__()
        self.db_tool = db_tool or DBQueryTool()
    
    def _run(self, component_id: str, pin_name: Optional[str] = None) -> Dict[str, Any]:
        return self.db_tool.query_pin_table({"component_id": component_id, "pin_name": pin_name})


class SQLQueryTool(BaseTool):
    """执行SQL查询的工具"""
    name = "execute_sql"
    description = "直接执行SQL查询语句，可以查询任何表"
    args_schema = SQLQueryInput
    
    def __init__(self, db_tool: DBQueryTool = None):
        super().__init__()
        self.db_tool = db_tool or DBQueryTool()
    
    def _run(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        return self.db_tool.execute_sql({"sql": sql, "params": params})


# 创建共享数据库连接
db_connection = DBConnection()

# 创建共享数据库工具
db_tool = DBQueryTool(db_connection)

# 创建工具实例
pin_query_tool = create_logged_tool(PinQueryTool)(db_tool=db_tool)
sql_query_tool = create_logged_tool(SQLQueryTool)(db_tool=db_tool)

# 数据库查询工具列表
db_query_tools = [pin_query_tool, sql_query_tool] 