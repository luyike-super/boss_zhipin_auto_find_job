"""
检查langgraph版本和API
"""
import sys

def check_langgraph():
    try:
        import langgraph
        print(f"langgraph版本: {langgraph.__version__}")
        
        # 检查Graph类
        from langgraph.graph import Graph
        print("成功导入Graph类")
        
        # 检查Graph构造函数支持的参数
        import inspect
        sig = inspect.signature(Graph.__init__)
        print(f"Graph.__init__的参数: {sig}")
        
        # 检查Graph类的方法
        methods = [method for method in dir(Graph) if not method.startswith('_')]
        print(f"Graph类的方法: {methods}")
        
        # 尝试创建Graph实例
        graph = Graph()
        print("成功创建Graph实例")
        
        # 检查是否有state_类参数
        if hasattr(Graph, 'set_state_type'):
            print("Graph有set_state_type方法")
        else:
            print("Graph没有set_state_type方法")
            
        if 'state_type' in sig.parameters:
            print("Graph构造函数接受state_type参数")
        else:
            print("Graph构造函数不接受state_type参数")
        
    except ImportError as e:
        print(f"导入langgraph出错: {e}")
    except Exception as e:
        print(f"检查过程中发生错误: {e}")

if __name__ == "__main__":
    check_langgraph() 