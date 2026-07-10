# my_calculator_tool.py

import ast
import operator
import math
from ..registry import ToolRegistry

def my_calculate(expression: str) -> str:
    """计算数学表达式"""
    if not expression.strip():
        return "错误：计算表达式不能为空"
    
    # 定义支持的运算符
    operators = {
        ast.Add: operator.add,  # AST 的"加号"节点 → Python 的加法函数
        ast.Sub: operator.sub, 
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.xor,
        ast.USub: operator.neg,
    }

    # 支持的数学函数
    functions = {
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'exp': math.exp,
        'pi': math.pi,
    }

    try:
        node = ast.parse(expression, mode='eval')  # 解析表达式为ast的节点，是一个树形结构
        result = _eval_node(node.body, operators, functions)
        return str(result)
    except Exception as e:
        return f"错误：无法计算表达式。详情: {str(e)}"
    
def _eval_node(node, operators, functions):
    """递归计算AST节点"""
    if isinstance(node, ast.Constant):
        # 处理常量节点
        return node.value
    elif isinstance(node, ast.BinOp):
        # 处理二元运算节点
        left = _eval_node(node.left, operators, functions)
        right = _eval_node(node.right, operators, functions)
        op = operators.get(type(node.op))
        return op(left, right)
    elif isinstance(node, ast.Call):
        # 处理函数调用节点
        func_name = node.func.id
        if func_name in functions:
            args = [_eval_node(arg, operators, functions) for arg in node.args]
            return functions[func_name](*args)
    elif isinstance(node, ast.Name):
        if node.id in functions:
            return functions[node.id]
        
def create_calculator_registry() -> ToolRegistry:
    """创建并注册计算器工具"""
    registry = ToolRegistry()
    registry.register_function(
        name="my_calculator",
        description="执行数学计算。支持基本运算、数学函数等。例如：2+3*4, sqrt(16), sin(pi/2)等。",
        func=my_calculate
    )
    return registry