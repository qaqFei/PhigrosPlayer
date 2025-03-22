import typing
import string
import ast
import sys
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
    "extends", "false", "final", "finally",
    "for", "function", "goto", "if", "implements",
    "import", "in", "instanceof", "interface",
    "let", "long", "native", "new", "null",
    "package", "private", "protected", "public", "return",
    "short", "static", "super", "switch", "synchronized",
    "throw", "throws", "transient", "true",
    "try", "typeof", "var", "void", "volatile",
    "while", "with", "yield"
)

pyexceptions = (
    BaseException, GeneratorExit, KeyboardInterrupt,
    SystemExit, Exception, StopIteration, OSError,
    EnvironmentError, IOError, WindowsError if sys.platform == "win32" else type("WindowsError", (OSError, )),
    ArithmeticError, AssertionError, AttributeError, BufferError,
    EOFError, ImportError, LookupError, MemoryError,
    NameError, ReferenceError, RuntimeError, StopAsyncIteration,
    SyntaxError, SystemError, TypeError, ValueError,
    FloatingPointError, OverflowError, ZeroDivisionError,
    ModuleNotFoundError, IndexError, KeyError, UnboundLocalError,
    BlockingIOError, ChildProcessError, ConnectionError,
    BrokenPipeError, ConnectionAbortedError, ConnectionRefusedError,
    ConnectionResetError, FileExistsError, FileNotFoundError,
    InterruptedError, IsADirectoryError, NotADirectoryError,
    PermissionError, ProcessLookupError, TimeoutError,
    NotImplementedError, RecursionError, IndentationError,
    TabError, UnicodeError, UnicodeDecodeError, UnicodeEncodeError,
    UnicodeTranslateError
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
            name = f"_{name}"
            # raise ValueError(f"Variable name cannot be a reserved keyword: {name}")
        
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
        return f"({self.op}{tojseval(self.operand)})"

class JsAst_Not(JsAst_PrecededUnaryOp): op = "!"
class JsAst_BitNot(JsAst_PrecededUnaryOp): op = "~"
class JsAst_Pos(JsAst_PrecededUnaryOp): op = "+"
class JsAst_Neg(JsAst_PrecededUnaryOp): op = "-"
class JsAst_Typeof(JsAst_PrecededUnaryOp): op = "typeof "
class JsAst_Delete(JsAst_PrecededUnaryOp): op = "delete "
class JsAst_Inc(JsAst_PrecededUnaryOp): op = "++"
class JsAst_Dec(JsAst_PrecededUnaryOp): op = "--"
class JsAst_Unpack(JsAst_PrecededUnaryOp):
    op = "..."
    
    def __js_eval__(self) -> str:
        return f"{self.op}{tojseval(self.operand)}"

class JsAst_PostfixUnaryOp(PyJsVar):
    op: str

    def __init__(self, operand: PyJsVar):
        if not hasattr(self, "op"):
            raise TypeError("JsAst_UnaryOp cannot be instantiated")

        self.operand = operand

    def __js_eval__(self) -> str:
        return f"({tojseval(self.operand)}{self.op})"

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
class JsAst_NotIn(JsAst_BinOp):
    op = "in"
    
    def __js_eval__(self):
        return f"!({tojseval(self.left)} {self.op} {tojseval(self.right)})"
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

class JsAst_For(JsAst_Statement):
    def __init__(self, start: PyJsVar, end: PyJsVar, step: PyJsVar, code: JsAst_Block):
        self.start = start
        self.end = end
        self.step = step
        self.code = code

    def __js_eval__(self) -> str:
        return f"for ({tojseval(self.start)}; {tojseval(self.end)}; {tojseval(self.step)}) {tojseval(self.code)}"

class JsAst_InFor(JsAst_Statement):
    def __init__(self, name: PyJsVar, iterable: PyJsVar, code: JsAst_Block):
        self.name = name
        self.iterable = iterable
        self.code = code

    def __js_eval__(self) -> str:
        return f"for ({tojseval(self.name)} in {tojseval(self.iterable)}) {tojseval(self.code)}"

class JsAst_OfFor(JsAst_Statement):
    def __init__(self, name: PyJsVar, iterable: PyJsVar, code: JsAst_Block):
        self.name = name
        self.iterable = iterable
        self.code = code

    def __js_eval__(self) -> str:
        return f"for ({tojseval(self.name)} of {tojseval(self.iterable)}) {tojseval(self.code)}"

class JsAst_While(JsAst_Statement):
    def __init__(self, condition: PyJsVar, code: JsAst_Block):
        self.condition = condition
        self.code = code
    
    def __js_eval__(self) -> str:
        return f"while ({tojseval(self.condition)}) {tojseval(self.code)}"

class JsAst_Try(JsAst_Statement):
    def __init__(
        self,
        code: JsAst_Block, catch: JsAst_Block,
        catch_name: typing.Optional[JsAst_Variable] = None,
        finally_: typing.Optional[JsAst_Block] = None
    ):
        self.code = code
        self.catch = catch
        self.catch_name = catch_name
        self.finally_ = finally_

    def __js_eval__(self) -> str:
        result = f"try {tojseval(self.code)} catch"
        if self.catch_name is not None:
            result += f" ({tojseval(self.catch_name)})"
        result += f" {tojseval(self.catch)}"
        if self.finally_ is not None:
            result += f" finally {tojseval(self.finally_)}"
        return result

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

class JsAst_SetVal(PyJsVar):
    def __init__(self, name: PyJsVar, value: JsAst_Variable):
        self.name = name
        self.value = value

    def __js_eval__(self) -> str:
        return f"{self.name.__js_eval__()}={tojseval(self.value)}"
    
class JsAst_Attribute(PyJsVar):
    def __init__(self, name: PyJsVar, attr: PyJsVar):
        self.name = name
        self.attr = attr

    def __js_eval__(self) -> str:
        return f"{tojseval(self.name)}.{tojseval(self.attr)}"

class JsAst_New(PyJsVar):
    def __init__(self, val: PyJsVar):
        self.val = val

    def __js_eval__(self) -> str:
        return f"new {tojseval(self.val)}"

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

class JsAst_CallKwArg(PyJsVar):
    def __init__(self, name: PyJsVar, val: PyJsVar):
        self.name = name
        self.val = val
    
    def __js_eval__(self) -> str:
        return f"{tojseval(self.name)} = {tojseval(self.val)}"

class JsAst_Await(PyJsVar):
    def __init__(self, val: PyJsVar):
        self.val = val

    def __js_eval__(self) -> str:
        return f"await {tojseval(self.val)}"

class JsAst_Throw(JsAst_Statement):
    def __init__(self, value: PyJsVar):
        self.value = value

    def __js_eval__(self) -> str:
        return f"throw {tojseval(self.value)};"

class JsAst_FunctionArg(PyJsVar):
    def __init__(self, name: JsAst_Variable, default: typing.Optional[PyJsVar] = None):
        self.name = name
        self.default = default
    
    def __js_eval__(self) -> str:
        return f"{self.name.__js_eval__()}={tojseval(self.default)}"

class JsAst_Function(PyJsVar):
    def __init__(
        self,
        body: JsAst_Block|PyJsVar, name: typing.Optional[JsAst_Variable] = None, args: typing.Optional[list[JsAst_FunctionArg]] = None,
        has_ellipsis: bool = False, ellipsis_name: typing.Optional[JsAst_Variable] = None,
        is_async: bool = False
    ):
        if not isinstance(body, JsAst_Block):
            body = JsAst_Block([JsAst_Return(body)])
            
        self.name = name
        self.args = args
        self.body = body
        self.has_ellipsis = has_ellipsis
        self.ellipsis_name = ellipsis_name
        self.is_async = is_async
        
    def __js_eval__(self) -> str:
        arg_string = ", ".join(map(tojseval, self.args)) if self.args is not None else ""
        
        if self.has_ellipsis:
            ellipsis_str = f"...{tojseval(self.ellipsis_name)}"
            if self.args:
                arg_string += ", "
            arg_string += ellipsis_str
            
        body_string = tojseval(self.body)
        function_header = f"{"async " if self.is_async else ""}function"
        
        if self.name is None:
            return f"{function_header}({arg_string}){body_string}"
        else:
            return f"{function_header} {self.name}({arg_string}){body_string}"

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

class JsAst_Subscript(PyJsVar):
    def __init__(self, name: PyJsVar, index: PyJsVar):
        self.name = name
        self.index = index

    def __js_eval__(self) -> str:
        return f"{tojseval(self.name)}[{tojseval(self.index)}]"

class JsAst_TernaryOp(PyJsVar):
    def __init__(self, condition: PyJsVar, true_val: PyJsVar, false_val: PyJsVar):
        self.condition = condition
        self.true_val = true_val
        self.false_val = false_val

    def __js_eval__(self) -> str:
        return f"({tojseval(self.condition)}?{tojseval(self.true_val)}:{tojseval(self.false_val)})"

class JsAst_MoreOp(PyJsVar):
    op: str
    
    def __init__(self, vals: list[PyJsVar]):
        self.vals = vals

    def __js_eval__(self) -> str:
        if not hasattr(self, "op"):
            raise NotImplementedError("JsAst_MoreOp cannot be instantiated")
        
        op = f" {self.op} "
        return f"({op.join(map(tojseval, self.vals))})"

class JsAst_MoreOp_Add(JsAst_MoreOp): op = "+"
class JsAst_MoreOp_Mul(JsAst_MoreOp): op = "*"
class JsAst_MoreOp_BoolAnd(JsAst_MoreOp): op = "&&"
class JsAst_MoreOp_BoolOr(JsAst_MoreOp): op = "||"

class JsAst_FormatString(PyJsVar):
    def __init__(self, values: list[PyJsVar]):
        self.values = values
    
    def __js_eval__(self) -> str:
        result = ["`"]
        
        for i in self.values:
            if isinstance(i, str):
                result.append(i)
            else:
                result.append("${")
                result.append(tojseval(i))
                result.append("}")
        
        result.append("`")
        return "".join(result)

class JsAst_Nop(JsAst_Statement):
    def __init__(self):
        pass

    def __js_eval__(self) -> str:
        return ""

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
        if "__js_unpacks__" in val:
            unpack_str = ", ".join(map(lambda x: tojseval(x), val["__js_unpacks__"]))
        else:
            unpack_str = ""
        
        items = list(filter(lambda i: i[0] != "__js_unpacks__", val.items()))
        if items and unpack_str:
            unpack_str = f", {unpack_str}"
            
        return f"{{{", ".join(map(lambda x: f"{tojseval(x[0])}: {tojseval(x[1])}", items)) + unpack_str}}}"

    elif isinstance(val, typing.Iterable):
        return f"[{", ".join(map(tojseval, val))}]"

    elif val is None:
        return "null"
    
    elif isinstance(val, type(Ellipsis)):
        return "(new function (){}())"
    
    else:
        raise TypeError(f"Cannot convert {type(val)} to js eval")
    
def pyast2jsast(pyast: ast.AST, need_somepyvar: bool = True) -> PyJsVar:
    inner_pyast2jsast = lambda x: pyast2jsast(x, False)
    
    if isinstance(pyast, (ast.Module, list)):
        block = JsAst_Block(list(map(inner_pyast2jsast, pyast.body if isinstance(pyast, ast.Module) else pyast)))
        if isinstance(pyast, ast.Module) and need_somepyvar:
            block.statements[:0] = inner_pyast2jsast(ast.parse("""
def _nouse_new(cls):
    return lambda *args: eval(f"new cls(...args)")

print = console.log
list = Array
str = String
int = Number
float = Number
bytes = _nouse_new(Uint8Array)
bytearray = _nouse_new(Uint8Array)
memoryview = _nouse_new(Uint8Array)
set = _nouse_new(Set)

len = lambda obj: obj.length
getattr = lambda obj, attr: obj[attr]
setattr = lambda obj, attr, value: Relect.set(obj, attr, value)
hasattr = lambda obj, attr: attr in obj
repr = lambda obj: obj.toString()

Object.prototype.keys = lambda: Object.keys(this)

def isinstance(obj, cls):
    if not eval("cls instanceof Array"):
        cls = [cls]
    
    for i in cls:
        if eval("obj.__proto__ === i.prototype"):
            return True
    
    return False

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

def _protytype_2_class(cls, names):
    for i in names:
        cls[i] = cls["prototype"][i]

def _array_extend(arr):
    for i in arr:
        this.push(i)
    
def _toofrom_bytes_setbyteorder(bs, byteorder):
    return bs.reverse() if byteorder == "little" else bs

def _set_to_global(valname, val):
    eval(f"{valname} = val")

Array.prototype._jssort = Array.prototype.sort
Array.prototype.copy = lambda: this.slice()
Array.prototype.append = Array.prototype.push
Array.prototype.extend = _array_extend
Array.prototype.pop = lambda: this.splice(this.length - 1, 1)[0]
Array.prototype.index = lambda value: this.indexOf(value)
Array.prototype.count = lambda value: this.filter(lambda x: x == value).length
Array.prototype.insert = lambda index, value: this.splice(index, 0, value)
Array.prototype.remove = lambda value: this.splice(this.indexOf(value), 1)
Array.prototype.sort = lambda reverse, key=(lambda x: x): this._jssort(lambda a, b: key(a) - key(b) if reverse is undefined else key(b) - key(a))
Array.prototype.clear = lambda: Reflect.set(this, "length", 0)

_protytype_2_class(Array, [
    "copy",
    "extend",
    "pop",
    "index",
    "count",
    "insert",
    "remove",
    "sort",
    "clear"
])

Number.prototype.real = lambda: this
Number.prototype.imag = lambda: 0
Number.prototype.numerator = lambda: this
Number.prototype.denominator = lambda: 1
Number.prototype.conjugate = lambda: this
Number.prototype.bit_length = lambda: this.toString(2).length
Number.prototype.to_bytes = lambda length, byteorder = "big", signed = False: _toofrom_bytes_setbyteorder(Array(length).fill(0).map(lambda x: this >> (8 * x) & 0xFF), byteorder)
Number.prototype.from_bytes = lambda bytes, byteorder = "big", signed = False: _toofrom_bytes_setbyteorder(bytes, byteorder).reduce(lambda x, y: x << 8 | y, 0)

_protytype_2_class(Number, [
    "real",
    "imag",
    "numerator",
    "denominator",
    "conjugate",
    "bit_length",
    "to_bytes",
    "from_bytes"
])

_python_packages = {}

_python_packages.time = {
    "time": lambda: Date.now() / 1000,
    "sleep": lambda seconds: _nouse_new(Promise)(lambda resolve: setTimeout(resolve, seconds * 1000)),
    "perf_counter": lambda: Date.now() / 1000,
    "perf_counter_ns": lambda: Date.now() * 1000
}

_python_packages.random = {
    "random": lambda: Math.random(),
    "randint": lambda a, b: Math.floor(Math.random() * (b - a + 1)) + a,
    "choice": lambda arr: arr[Math.floor(Math.random() * arr.length)],
    "shuffle": lambda arr: arr.sort(lambda: Math.random() - 0.5),
    "seed": lambda seed: Math.seedrandom(seed),
    "uniform": lambda a, b: Math.random() * (b - a) + a,
    "gauss": lambda mu, sigma: Math.random() * (high - low) + low,
}

def _import_from_python_package(package_name: str, varnames: list[list[str, str|None]], is_all: bool = False):
    if package_name not in _python_packages:
        raise ImportError(f"Package {package_name} not found")
    
    if is_all:
        for i in _python_packages[package_name].keys():
            _set_to_global(i, _python_packages[package_name][i])
    else:
        for i in varnames:
            [varname, alias] = i
            _set_to_global(alias if alias is not None else varname, _python_packages[package_name][varname])

def _import_python_package(package_name: str, alias: str|None = None):
    if package_name not in _python_packages:
        raise ImportError(f"Package {package_name} not found")
    _set_to_global(alias if alias is not None else package_name, _python_packages[package_name])
""" + f"""
{"\n".join(map(lambda e: f"{e.__name__} = Error", pyexceptions))}
""")).statements
        return block
    
    elif isinstance(pyast, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return JsAst_Function(
            inner_pyast2jsast(pyast.body), pyast.name,
            inner_pyast2jsast(pyast.args),
            pyast.args.vararg is not None,
            JsAst_Variable(pyast.args.vararg.arg) if pyast.args.vararg is not None else None,
            isinstance(pyast, ast.AsyncFunctionDef)
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
            ...
            # raise NotImplementedError("Keyword arguments are not supported")
            
        return result
    
    elif isinstance(pyast, ast.Constant):
        return pyast.value
    
    elif isinstance(pyast, ast.Call):
        return JsAst_Call(
            inner_pyast2jsast(pyast.func),
            list(map(inner_pyast2jsast, pyast.args)) +
            list(map(inner_pyast2jsast, pyast.keywords))
        )
    
    elif isinstance(pyast, ast.keyword):
        return JsAst_CallKwArg(
            JsAst_Variable(pyast.arg),
            inner_pyast2jsast(pyast.value)
        )
    
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
    
    elif isinstance(pyast, ast.Subscript):
        if not isinstance(pyast.slice, ast.Slice):
            return JsAst_Subscript(inner_pyast2jsast(pyast.value), inner_pyast2jsast(pyast.slice))
        
        s = pyast.slice
        if s.step is None:
            return JsAst_Call(
                JsAst_Attribute(inner_pyast2jsast(pyast.value), JsAst_Variable("slice")),
                [inner_pyast2jsast(s.lower), inner_pyast2jsast(s.upper)]
            )
    
    elif isinstance(pyast, ast.IfExp):
        return JsAst_TernaryOp(
            inner_pyast2jsast(pyast.test),
            inner_pyast2jsast(pyast.body),
            inner_pyast2jsast(pyast.orelse)
        )
    
    elif isinstance(pyast, ast.ClassDef):
        statements = []
        class_init = inner_pyast2jsast(pyast.body).statements
        after_init = []
        has_initfunc = False
        initfunc = None
        method_map = {}
        
        for stmt in class_init.copy():
            if isinstance(stmt, (JsAst_DefineVar, JsAst_SetVal)):
                v = JsAst_Variable(tojseval(stmt.name))
                after_init.append(JsAst_SetVal(
                    JsAst_Attribute(JsAst_Variable("cls"), v),
                    v
                ))
                method_map[stmt.name] = stmt
            
            elif isinstance(stmt, JsAst_Function):
                if stmt.name is None: continue
                
                if stmt.name == "__init__":
                    has_initfunc = True
                    initfunc = stmt
                else:
                    stmt.body.statements.insert(0, JsAst_SetVal(
                        JsAst_Variable("self"), JsAst_Variable("this")
                    ))
                
                method_map[stmt.name] = stmt
                
                v = JsAst_Variable(stmt.name)
                after_init.append(JsAst_SetVal(
                    JsAst_Attribute(JsAst_Variable("cls"), v),
                    v
                ))
                
                if not stmt.args: continue
                if tojseval(stmt.args[0].name) == "self":
                    stmt.args.pop(0)
        
        if "__str__" in method_map:
            toString = method_map["__str__"]
        elif "__repr__" in method_map:
            toString = method_map["__repr__"]
        else:
            toString = JsAst_Function(
                JsAst_Block([
                    JsAst_Return(f"<python {pyast.name} object at unknow_address>")
                ]), "__str__"
            )
            method_map["__str__"] = toString
            class_init.append(toString)
        
        if toString is not None:
            toString: JsAst_Function|JsAst_SetVal|JsAst_DefineVar
            after_init.append(JsAst_SetVal(
                JsAst_Subscript(JsAst_Variable("cls"), JsAst_Attribute(
                    JsAst_Variable("Symbol"), JsAst_Variable("toPrimitive")
                )),
                JsAst_Variable(toString.name)
            ))
        
        if not has_initfunc:
            initfunc = JsAst_Function(JsAst_Block(), "__init__")
            class_init.append(initfunc)

        initfunc.body.statements.insert(0, JsAst_SetVal(
            JsAst_Variable("self"),
            {"__js_unpacks__": [JsAst_Unpack(JsAst_Variable("cls"))]}
        ))
        initfunc.body.statements.append(JsAst_Return(JsAst_Variable("self")))
        
        after_init.insert(0, JsAst_SetVal(
            JsAst_Variable("cls"), JsAst_Variable("__init__")
        ))
        
        statements.extend(class_init)
        statements.extend(after_init)
        statements.append(JsAst_Return(JsAst_Variable("cls")))
        
        return JsAst_SetVal(
            JsAst_Variable(pyast.name),
            JsAst_Call(JsAst_Function(JsAst_Block(statements)), [])
        )
    
    elif isinstance(pyast, (ast.Global, ast.Nonlocal)):
        return JsAst_Nop()
    
    elif isinstance(pyast, ast.JoinedStr):
        return JsAst_FormatString(list(map(inner_pyast2jsast, pyast.values)))
    
    elif isinstance(pyast, ast.FormattedValue):
        return inner_pyast2jsast(pyast.value)
    
    elif isinstance(pyast, ast.Raise):
        return JsAst_Throw(inner_pyast2jsast(pyast.exc))
    
    elif isinstance(pyast, ast.Try):
        jstry = JsAst_Try(inner_pyast2jsast(pyast.body), JsAst_Block())
        if len(pyast.handlers) > 1:
            pyast.handlers = pyast.handlers[:1]
            # raise NotImplementedError("Multiple except clauses not supported")
        
        jstry.catch = inner_pyast2jsast(pyast.handlers[0].body)
        if pyast.handlers[0].name is not None:
            jstry.catch_name = JsAst_Variable(pyast.handlers[0].name)
        
        if pyast.finalbody:
            jstry.finally_ = inner_pyast2jsast(pyast.finalbody)
        
        return jstry
    
    elif isinstance(pyast, ast.BoolOp):
        boolop_map = {
            ast.And: JsAst_MoreOp_BoolAnd,
            ast.Or: JsAst_MoreOp_BoolOr
        }
        r = boolop_map[type(pyast.op)]
        return r(list(map(inner_pyast2jsast, pyast.values)))
    
    elif isinstance(pyast, ast.Pass):
        return JsUndefined()
    
    elif isinstance(pyast, ast.Starred):
        return JsAst_Unpack(inner_pyast2jsast(pyast.value))
    
    elif isinstance(pyast, ast.NamedExpr):
        return JsAst_SetVal(inner_pyast2jsast(pyast.target), inner_pyast2jsast(pyast.value))
    
    elif isinstance(pyast, ast.With):
        def _get_wi_varname(wi: ast.withitem):
            return JsAst_Variable(f"withvar_{hash(wi)}")
        
        return JsAst_Block([
            *(JsAst_DefineVar(
                _get_wi_varname(wi),
                inner_pyast2jsast(wi.context_expr)
            ) for wi in pyast.items),
            *(JsAst_DefineVar(
                inner_pyast2jsast(wi.optional_vars) if wi.optional_vars is not None else JsAst_Variable("_"), JsAst_Call(
                JsAst_Attribute(_get_wi_varname(wi), JsAst_Variable("__enter__")),
                []
            )) for wi in pyast.items),
            *[
                JsAst_Try(inner_pyast2jsast(pyast.body), JsAst_Block([
                    JsAst_Throw(JsAst_Variable("e"))
                ]), JsAst_Variable("e"), JsAst_Block([
                    JsAst_Call(
                        JsAst_Attribute(_get_wi_varname(wi), JsAst_Variable("__exit__")),
                        [None, None, None]
                    ) for wi in pyast.items
                ]))
            ]
        ])
    
    elif isinstance(pyast, ast.Import):
        result = JsAst_Block()
        for i in pyast.names:
            result.statements.append(JsAst_Call(
                JsAst_Variable("_import_python_package"),
                [i.name, i.asname]
            ))
        return result
    
    elif isinstance(pyast, ast.ImportFrom):
        result = JsAst_Block()
        for i in pyast.names:
            result.statements.append(JsAst_Call(
                JsAst_Variable("_import_from_python_package"),
                [pyast.module, [[i.name, i.asname]], i.name == "*"]
            ))
        return result
    
    elif isinstance(pyast, ast.AnnAssign):
        return JsAst_SetVal(inner_pyast2jsast(pyast.target), inner_pyast2jsast(pyast.value))
    
    elif isinstance(pyast, ast.ListComp):
        def _warp_if(statement):
            if gen.ifs:
                return JsAst_If(
                    JsAst_MoreOp_BoolAnd(map(inner_pyast2jsast, gen.ifs)),
                    JsAst_Block([statement])
                )
            return statement
        
        gen = pyast.generators.pop()
        compval = JsAst_Variable("master_iter") if not pyast.generators else inner_pyast2jsast(gen.iter)
        targetval = inner_pyast2jsast(gen.target)
        temparr = JsAst_Variable("listcomp_temparr")
        push_call = JsAst_Call(JsAst_Attribute(temparr, JsAst_Variable("push")), [inner_pyast2jsast(pyast.elt)])
        
        for_loop = JsAst_OfFor(targetval, compval, JsAst_Block([_warp_if(push_call)]))
        
        while pyast.generators:
            gen = pyast.generators.pop()
            compval = JsAst_Variable("master_iter") if not pyast.generators else inner_pyast2jsast(gen.iter)
            targetval = inner_pyast2jsast(gen.target)
            for_loop = JsAst_OfFor(targetval, compval, JsAst_Block([_warp_if(for_loop)]))
        
        result = JsAst_Call(
            JsAst_Function(
                JsAst_Block([
                    JsAst_DefineVar(temparr, []),
                    for_loop,
                    JsAst_Return(temparr)
                ]),
                args=[JsAst_FunctionArg(JsAst_Variable("master_iter"))]
            ),
            [pyast2jsast(gen.iter)]
        )
        return result

    elif isinstance(pyast, ast.Await):
        return JsAst_Await(inner_pyast2jsast(pyast.value))
    
    elif isinstance(pyast, type(None)):
        return None
    
    else:
        print(f"Cannot convert {type(pyast)} to js ast")
