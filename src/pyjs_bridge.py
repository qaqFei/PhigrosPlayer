import typing
import string
import ast
from abc import abstractmethod

@typing.runtime_checkable
class PyJsVar(typing.Protocol):
    __slots__ = ()
    
    @abstractmethod
    def __js_eval__(self) -> str:
        pass

js_keywords = (
    "abstract", "arguments", "boolean", "break", "byte",
    "case", "catch", "char", "class", "const",
    "continue", "debugger", "default", "delete", "do",
    "double", "else", "enum", "export",
    "extends", "false", "final", "finally", "float",
    "for", "function", "goto", "if", "implements",
    "import", "in", "instanceof", "int", "interface",
    "let", "long", "native", "new", "null",
    "package", "private", "protected", "public", "return",
    "short", "static", "super", "switch", "synchronized",
    "throw", "throws", "transient", "true",
    "try", "typeof", "var", "void", "volatile",
    "while", "with", "yield"
)

type jseval_type = (
    int|
    float|
    bool|
    str|
    bytes|bytearray|memoryview|
    set|frozenset|
    typing.Iterable|
    typing.Mapping|
    PyJsVar
)

class JsUndefined(PyJsVar):
    def __js_eval__(self) -> str:
        return "undefined"

    def __setattr__(self, name: str, value: typing.Any):
        raise AttributeError("Cannot set attribute on undefined")

class JsBigInt(int, PyJsVar):
    def __js_eval__(self) -> str:
        return f"{self}n"

class JsNan(PyJsVar):
    def __js_eval__(self) -> str:
        return "NaN"

class JsInfinity(PyJsVar):
    def __js_eval__(self) -> str:
        return "Infinity"

class JsNegativeInfinity(PyJsVar):
    def __js_eval__(self) -> str:
        return "-Infinity"
    
class JsAst_Variable(PyJsVar):
    def __init__(self, name: str):
        if not name:
            raise ValueError("Variable name cannot be empty")
        
        if "\n" in name:
            raise ValueError("Variable name cannot contain newline")
        
        if " " in name:
            raise ValueError("Variable name cannot contain space")
        
        if "-" in name:
            raise ValueError("Variable name cannot contain dash")
        
        if "/" in name:
            raise ValueError("Variable name cannot contain slash")

        if name in js_keywords:
            raise ValueError(f"Variable name cannot be a reserved keyword: {name}")
        
        if name.startswith(tuple(string.digits)):
            raise ValueError("Variable name cannot start with a number")
        
        self.name = name
        
    def __js_eval__(self) -> str:
        return self.name

class JsAst_PrecededUnaryOp(PyJsVar):
    op: str
    
    def __init__(self, operand: PyJsVar):
        if not hasattr(self, "op"):
            raise TypeError("JsAst_UnaryOp cannot be instantiated")
        
        self.operand = operand

    def __js_eval__(self) -> str:
        return f"{self.op}{tojseval(self.operand)}"

class JsAst_Not(JsAst_PrecededUnaryOp): op = "!"
class JsAst_BitNot(JsAst_PrecededUnaryOp): op = "~"
class JsAst_Pos(JsAst_PrecededUnaryOp): op = "+"
class JsAst_Neg(JsAst_PrecededUnaryOp): op = "-"
class JsAst_Typeof(JsAst_PrecededUnaryOp): op = "typeof "
class JsAst_Delete(JsAst_PrecededUnaryOp): op = "delete "
class JsAst_Inc(JsAst_PrecededUnaryOp): op = "++"
class JsAst_Dec(JsAst_PrecededUnaryOp): op = "--"

class JsAst_PostfixUnaryOp(PyJsVar):
    op: str

    def __init__(self, operand: PyJsVar):
        if not hasattr(self, "op"):
            raise TypeError("JsAst_UnaryOp cannot be instantiated")

        self.operand = operand

    def __js_eval__(self) -> str:
        return f"{tojseval(self.operand)}{self.op}"

class JsAst_IncPost(JsAst_PostfixUnaryOp): op = "++"
class JsAst_DecPost(JsAst_PostfixUnaryOp): op = "--"

class JsAst_BinOp(PyJsVar):
    op: str
    
    def __init__(self, left: PyJsVar, right: PyJsVar):
        if not hasattr(self, "op"):
            raise TypeError("JsAst_BinOp cannot be instantiated")
        
        self.left = left
        self.right = right

    def __js_eval__(self) -> str:
        return f"({tojseval(self.left)} {self.op} {tojseval(self.right)})"
    
class JsAst_Add(JsAst_BinOp): op = "+"
class JsAst_Sub(JsAst_BinOp): op = "-"
class JsAst_Mul(JsAst_BinOp): op = "*"
class JsAst_Div(JsAst_BinOp): op = "/"
class JsAst_Mod(JsAst_BinOp): op = "%"
class JsAst_Pow(JsAst_BinOp): op = "**"
class JsAst_LShift(JsAst_BinOp): op = "<<"
class JsAst_RShift(JsAst_BinOp): op = ">>"
class JsAst_RRShift(JsAst_BinOp): op = ">>>"
class JsAst_BitAnd(JsAst_BinOp): op = "&"
class JsAst_BitOr(JsAst_BinOp): op = "|"
class JsAst_BitXor(JsAst_BinOp): op = "^"
class JsAst_Eq(JsAst_BinOp): op = "=="
class JsAst_NotEq(JsAst_BinOp): op = "!="
class JsAst_StrictEq(JsAst_BinOp): op = "==="
class JsAst_StrictNotEq(JsAst_BinOp): op = "!=="
class JsAst_Lt(JsAst_BinOp): op = "<"
class JsAst_LtEq(JsAst_BinOp): op = "<="
class JsAst_Gt(JsAst_BinOp): op = ">"
class JsAst_GtEq(JsAst_BinOp): op = ">="
class JsAst_In(JsAst_BinOp): op = "in"
class JsAst_NotIn(JsAst_BinOp): op = "not in"
class JsAst_BoolAnd(JsAst_BinOp): op = "&&"
class JsAst_BoolOr(JsAst_BinOp): op = "||"
class JsAst_AugAssignAdd(JsAst_BinOp): op = "+="
class JsAst_AugAssignSub(JsAst_BinOp): op = "-="
class JsAst_AugAssignMul(JsAst_BinOp): op = "*="
class JsAst_AugAssignDiv(JsAst_BinOp): op = "/="
class JsAst_AugAssignMod(JsAst_BinOp): op = "%="
class JsAst_AugAssignPow(JsAst_BinOp): op = "**="
class JsAst_AugAssignLShift(JsAst_BinOp): op = "<<="
class JsAst_AugAssignRShift(JsAst_BinOp): op = ">>="
class JsAst_AugAssignRRShift(JsAst_BinOp): op = ">>>="
class JsAst_AugAssignBitAnd(JsAst_BinOp): op = "&="
class JsAst_AugAssignBitOr(JsAst_BinOp): op = "|="
class JsAst_AugAssignBitXor(JsAst_BinOp): op = "^="

class JsAst_AugAssignFloorDiv(JsAst_BinOp):
    op = "//"
    
    def __js_eval__(self) -> str:
        return f"{tojseval(JsAst_SetVal(self.left, JsAst_FloorDiv(self.left, self.right)))}"

class JsAst_FloorDiv(JsAst_BinOp):
    op = "//"
    
    def __js_eval__(self) -> str:
        return f"Math.floor({tojseval(self.left)}/{tojseval(self.right)})"

class JsAst_Statement(PyJsVar):
    def __init__(self, content: PyJsVar):
        self.content = content
        
    def __js_eval__(self) -> str:
        return f"{tojseval(self.content)};"

class JsAst_Block(PyJsVar):
    def __init__(self, statements: typing.Optional[list[JsAst_Statement|PyJsVar]] = None):
        self.statements = statements if statements is not None else []

    def __js_eval__(self) -> str:
        return f"{{{"".join(map(lambda x: tojseval(x) if isinstance(x, JsAst_Statement) else f"{tojseval(x)};", self.statements))}}}"

class JsAst_If(JsAst_Statement):
    def __init__(self, condition: PyJsVar, code: JsAst_Block):
        self.condition = condition
        self.code = code
    
    def __js_eval__(self) -> str:
        return f"if ({tojseval(self.condition)}) {tojseval(self.code)}"

class JsAst_ElseIf(JsAst_Statement):
    def __init__(self, condition: PyJsVar, code: JsAst_Block):
        self.condition = condition
        self.code = code

    def __js_eval__(self) -> str:
        return f"else if ({tojseval(self.condition)}) {tojseval(self.code)}"

class JsAst_Else(JsAst_Statement):
    def __init__(self, code: JsAst_Block):
        self.code = code
    
    def __js_eval__(self) -> str:
        return f"else {tojseval(self.code)}"

class JsAst_For(PyJsVar):
    def __init__(self, start: PyJsVar, end: PyJsVar, step: PyJsVar, code: JsAst_Block):
        self.start = start
        self.end = end
        self.step = step
        self.code = code

    def __js_eval__(self) -> str:
        return f"for ({tojseval(self.start)}; {tojseval(self.end)}; {tojseval(self.step)}) {tojseval(self.code)}"

class JsAst_InFor(PyJsVar):
    def __init__(self, name: PyJsVar, iterable: PyJsVar, code: JsAst_Block):
        self.name = name
        self.iterable = iterable
        self.code = code

    def __js_eval__(self) -> str:
        return f"for ({tojseval(self.name)} in {tojseval(self.iterable)}) {tojseval(self.code)}"

class JsAst_OfFor(PyJsVar):
    def __init__(self, name: PyJsVar, iterable: PyJsVar, code: JsAst_Block):
        self.name = name
        self.iterable = iterable
        self.code = code

    def __js_eval__(self) -> str:
        return f"for ({tojseval(self.name)} of {tojseval(self.iterable)}) {tojseval(self.code)}"

class JsAst_While(PyJsVar):
    def __init__(self, condition: PyJsVar, code: JsAst_Block):
        self.condition = condition
        self.code = code
    
    def __js_eval__(self) -> str:
        return f"while ({tojseval(self.condition)}) {tojseval(self.code)}"

class JsAst_Continue(JsAst_Statement):
    def __init__(self):
        pass
    
    def __js_eval__(self) -> str:
        return "continue;"
    
class JsAst_Break(JsAst_Statement):
    def __init__(self):
        pass
        
    def __js_eval__(self) -> str:
        return "break;"

class JsAst_DefineVar(JsAst_Statement):
    def __init__(self, name: PyJsVar, value: JsAst_Variable, method: typing.Literal["var", "let", "const", ""] = "var"):
        self.method = method
        self.name = name
        self.value = value

    def __js_eval__(self) -> str:
        return f"{self.method if not self.method else (self.method + " ")}{tojseval(self.name)}={tojseval(self.value)};"

class JsAst_SetVal(JsAst_Statement):
    def __init__(self, name: PyJsVar, value: JsAst_Variable):
        self.name = name
        self.value = value

    def __js_eval__(self) -> str:
        return f"{self.name.__js_eval__()}={tojseval(self.value)};"
    
class JsAst_Attribute(PyJsVar):
    def __init__(self, name: PyJsVar, attr: PyJsVar):
        self.name = name
        self.attr = attr

    def __js_eval__(self) -> str:
        return f"{tojseval(self.name)}.{tojseval(self.attr)}"

class JsAst_Return(JsAst_Statement):
    def __init__(self, value: PyJsVar):
        self.value = value

    def __js_eval__(self) -> str:
        return f"return {tojseval(self.value)};"

class JsAst_Call(PyJsVar):
    def __init__(self, name: PyJsVar, args: list[PyJsVar]):
        self.name = name
        self.args = args

    def __js_eval__(self) -> str:
        return f"{tojseval(self.name)}({",".join(map(tojseval, self.args))})"

class JsAst_FunctionArg(PyJsVar):
    def __init__(self, name: JsAst_Variable, default: typing.Optional[PyJsVar] = None):
        self.name = name
        self.default = default
    
    def __js_eval__(self) -> str:
        if self.default is None:
            return self.name.__js_eval__()
        else:
            return f"{self.name.__js_eval__()}={tojseval(self.default)}"

class JsAst_Function(PyJsVar):
    def __init__(
        self,
        body: JsAst_Block|PyJsVar, name: typing.Optional[JsAst_Variable] = None, args: typing.Optional[list[JsAst_FunctionArg]] = None,
        has_ellipsis: bool = False, ellipsis_name: typing.Optional[JsAst_Variable] = None
    ):
        if not isinstance(body, JsAst_Block):
            body = JsAst_Block([JsAst_Return(body)])
            
        self.name = name
        self.args = args
        self.body = body
        self.has_ellipsis = has_ellipsis
        self.ellipsis_name = ellipsis_name
        
    def __js_eval__(self) -> str:
        arg_string = ", ".join(map(tojseval, self.args)) if self.args is not None else ""
        
        if self.has_ellipsis:
            arg_string += ", ..." + tojseval(self.ellipsis_name)
            
        body_string = tojseval(self.body)
        
        if self.name is None:
            return f"function({arg_string}){body_string}"
        else:
            return f"function {self.name}({arg_string}){body_string}"

class JsAst_Lambda(PyJsVar):
    def __init__(
        self,
        body: JsAst_Block, args: typing.Optional[list[JsAst_FunctionArg]] = None,
        has_ellipsis: bool = False, ellipsis_name: typing.Optional[JsAst_Variable] = None
    ):
        self.args = args
        self.body = body
        self.has_ellipsis = has_ellipsis
        self.ellipsis_name = ellipsis_name
    
    def __js_eval__(self) -> str:
        arg_string = ", ".join(map(tojseval, self.args)) if self.args is not None else ""

        if self.has_ellipsis:
            arg_string += ", ..." + tojseval(self.ellipsis_name)

        body_string = tojseval(self.body)

        return f"({arg_string})=>{body_string}"

class JsAst_TernaryOp(PyJsVar):
    def __init__(self, condition: PyJsVar, true_val: PyJsVar, false_val: PyJsVar):
        self.condition = condition
        self.true_val = true_val
        self.false_val = false_val

    def __js_eval__(self) -> str:
        return f"{tojseval(self.condition)}?{tojseval(self.true_val)}:{tojseval(self.false_val)}"

def tojseval(val: jseval_type) -> str:
    if isinstance(val, PyJsVar):
        return val.__js_eval__()
    
    elif isinstance(val, bool):
        return "true" if val else "false"
    
    elif isinstance(val, (int, float, str)):
        return repr(val)

    elif isinstance(val, (bytes, bytearray, memoryview)):
        return f"new Uint8Array({tojseval(list(val))})"

    elif isinstance(val, (set, frozenset)):
        return f"new Set({tojseval(list(val))})"

    elif isinstance(val, typing.Mapping):
        return f"{{{", ".join(map(lambda x: f"{tojseval(x[0])}: {tojseval(x[1])}", val.items()))}}}"

    elif isinstance(val, typing.Iterable):
        return f"[{", ".join(map(tojseval, val))}]"

    elif val is None:
        return "null"
    
    else:
        raise TypeError(f"Cannot convert {type(val)} to js eval")

def pyast2jsast(pyast: ast.AST, need_somepyvar: bool = True) -> PyJsVar:
    inner_pyast2jsast = lambda x: pyast2jsast(x, False)
    
    if isinstance(pyast, (ast.Module, list)):
        block = JsAst_Block(list(map(inner_pyast2jsast, pyast.body if isinstance(pyast, ast.Module) else pyast)))
        if isinstance(pyast, ast.Module) and need_somepyvar:
            block.statements[:0] = inner_pyast2jsast(ast.parse("""
print = console.log

def range(start, stop, step=1):
    result = []
    
    if stop is undefined:
        stop = start
        start = 0
        
    if step > 0:
        while start < stop:
            result.push(start)
            start += step
    else:
        while start > stop:
            result.push(start)
            start += step

    return result

Array.prototype.append = Array.prototype.push
Array.prototype.insert = lambda index, value: this.splice(index, 0, value)
Array.prototype.remove = lambda value: this.splice(this.indexOf(value), 1)
Array.prototype.clear = lambda: Reflect.set(this, "length", 0)
Array.prototype.copy = lambda: this.slice()
Array.prototype.pop = lambda: this.splice(this.length - 1, 1)[0]
Array.prototype.reverse = lambda: this.reverse()
Array.prototype.sort = lambda comparefn = (lambda a, b: a - b): this.sort(comparefn)
""")).statements
        return block
    
    elif isinstance(pyast, ast.FunctionDef):
        return JsAst_Function(
            inner_pyast2jsast(pyast.body), pyast.name,
            inner_pyast2jsast(pyast.args),
            pyast.args.vararg is not None,
            JsAst_Variable(pyast.args.vararg.arg) if pyast.args.vararg is not None else None
        )
    
    elif isinstance(pyast, ast.Return):
        return JsAst_Return(inner_pyast2jsast(pyast.value))

    elif isinstance(pyast, ast.BinOp):
        binop_map = {
            ast.Add: JsAst_Add,
            ast.Sub: JsAst_Sub,
            ast.Mult: JsAst_Mul,
            ast.Div: JsAst_Div,
            ast.FloorDiv: JsAst_FloorDiv,
            ast.Mod: JsAst_Mod,
            ast.Pow: JsAst_Pow,
            ast.LShift: JsAst_LShift,
            ast.RShift: JsAst_RShift,
            ast.BitOr: JsAst_BitOr,
            ast.BitXor: JsAst_BitXor,
            ast.BitAnd: JsAst_BitAnd
        }
        return binop_map[type(pyast.op)](inner_pyast2jsast(pyast.left), inner_pyast2jsast(pyast.right))

    elif isinstance(pyast, ast.Name):
        return JsAst_Variable(pyast.id)
    
    elif isinstance(pyast, ast.arguments):
        result = []
        defaultstart = len(pyast.args) - len(pyast.defaults)
        for i, arg in enumerate(pyast.args):
            result.append(JsAst_FunctionArg(
                JsAst_Variable(arg.arg),
                inner_pyast2jsast(pyast.defaults[i - defaultstart]) if i >= defaultstart else None
            ))
            
        if pyast.kwarg is not None:
            raise NotImplementedError("Keyword arguments are not supported")
        return result
    
    elif isinstance(pyast, ast.Constant):
        return pyast.value
    
    elif isinstance(pyast, ast.Call):
        return JsAst_Call(inner_pyast2jsast(pyast.func), list(map(inner_pyast2jsast, pyast.args)))
    
    elif isinstance(pyast, ast.Assign):
        return JsAst_DefineVar(inner_pyast2jsast(pyast.targets[0]), inner_pyast2jsast(pyast.value), "")
    
    elif isinstance(pyast, ast.Expr):
        return inner_pyast2jsast(pyast.value)
    
    elif isinstance(pyast, (ast.Tuple, ast.List)):
        return [inner_pyast2jsast(x) for x in pyast.elts]
    
    elif isinstance(pyast, ast.Set):
        return set(map(inner_pyast2jsast, pyast.elts))
    
    elif isinstance(pyast, ast.Dict):
        return {inner_pyast2jsast(k): inner_pyast2jsast(v) for k, v in zip(pyast.keys, pyast.values)}
    
    elif isinstance(pyast, ast.Attribute):
        return JsAst_Attribute(inner_pyast2jsast(pyast.value), JsAst_Variable(pyast.attr))
    
    elif isinstance(pyast, ast.AugAssign):
        augop_map = {
            ast.Add: JsAst_AugAssignAdd,
            ast.Sub: JsAst_AugAssignSub,
            ast.Mult: JsAst_AugAssignMul,
            ast.Div: JsAst_AugAssignDiv,
            ast.FloorDiv: JsAst_AugAssignFloorDiv,
            ast.Mod: JsAst_AugAssignMod,
            ast.Pow: JsAst_AugAssignPow,
            ast.LShift: JsAst_AugAssignLShift,
            ast.RShift: JsAst_AugAssignRShift,
            ast.BitOr: JsAst_AugAssignBitOr,
            ast.BitXor: JsAst_AugAssignBitXor,
            ast.BitAnd: JsAst_AugAssignBitAnd
        }
        return augop_map[type(pyast.op)](inner_pyast2jsast(pyast.target), inner_pyast2jsast(pyast.value))
    
    elif isinstance(pyast, ast.If):
        block = JsAst_Block()
        block.statements.append(JsAst_If(inner_pyast2jsast(pyast.test), inner_pyast2jsast(pyast.body)))
        orelses = pyast.orelse.copy()
        for i, orelse in enumerate(orelses):
            if isinstance(orelse, ast.If):
                block.statements.append(JsAst_ElseIf(inner_pyast2jsast(orelse.test), inner_pyast2jsast(orelse.body)))
                orelses.extend(orelse.orelse)
            else:
                block.statements.append(JsAst_Else(JsAst_Block(list(map(inner_pyast2jsast, orelses[i:])))))
                break
        return block

    elif isinstance(pyast, ast.Compare):
        compareop_map = {
            ast.Eq: JsAst_Eq,
            ast.NotEq: JsAst_NotEq,
            ast.Lt: JsAst_Lt,
            ast.LtE: JsAst_LtEq,
            ast.Gt: JsAst_Gt,
            ast.GtE: JsAst_GtEq,
            ast.In: JsAst_In,
            ast.NotIn: JsAst_NotIn,
            ast.Is: JsAst_StrictEq,
            ast.IsNot: JsAst_StrictNotEq
        }
        expr = compareop_map[type(pyast.ops[0])](inner_pyast2jsast(pyast.left), inner_pyast2jsast(pyast.comparators[0]))
        for i, (op, comp) in enumerate(zip(pyast.ops[1:], pyast.comparators[1:])):
            expr = JsAst_BoolAnd(
                expr,
                compareop_map[type(op)](inner_pyast2jsast(pyast.comparators[i]), inner_pyast2jsast(comp))
            )
        return expr
    
    elif isinstance(pyast, ast.UnaryOp):
        unop_map = {
            ast.USub: JsAst_Neg,
            ast.UAdd: JsAst_Pos,
            ast.Not: JsAst_Not,
            ast.Invert: JsAst_BitNot
        }
        return unop_map[type(pyast.op)](inner_pyast2jsast(pyast.operand))
    
    elif isinstance(pyast, ast.For):
        return JsAst_OfFor(inner_pyast2jsast(pyast.target), inner_pyast2jsast(pyast.iter), inner_pyast2jsast(pyast.body))
    
    elif isinstance(pyast, ast.While):
        return JsAst_While(inner_pyast2jsast(pyast.test), inner_pyast2jsast(pyast.body))

    elif isinstance(pyast, ast.Continue):
        return JsAst_Continue()
    
    elif isinstance(pyast, ast.Break):
        return JsAst_Break()
    
    elif isinstance(pyast, ast.Lambda):
        return JsAst_Function(
            inner_pyast2jsast(pyast.body), None,
            inner_pyast2jsast(pyast.args),
            pyast.args.vararg is not None,
            JsAst_Variable(pyast.args.vararg.arg) if pyast.args.vararg is not None else None
        )
    
    else:
        print(f"Cannot convert {type(pyast)} to js ast")

pycode = """
for i in range(10):
    print(i ** 2)
"""

# console = type("_", (object, ), {"log": print})()
# print(exec(pycode))

pyast = ast.parse(pycode)
res = pyast2jsast(pyast)
print(tojseval(res))
