class Op:
    _op: str

    def __eq__(self, other) -> bool:
        if not isinstance(other, Op):
            return False
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    def needs_expansion(self) -> bool:
        raise NotImplementedError()

    def pretty(self, indent_level: int = 0) -> str:
        raise NotImplementedError()

class UnaryOp(Op):
    arg: str|Op

    def __init__(self, arg: str|Op):
        self.arg = arg

    def needs_expansion(self) -> bool:
        return isinstance(self.arg, Op) and self.arg.needs_expansion()

    def pretty(self, indent_level: int = 0) -> str:
        indent = '  ' * indent_level

        if not self.needs_expansion():
            return f'{indent}( {self._op} {self.arg} )'

        inner = self.arg.pretty(indent_level=indent_level+1)
        return f'{indent}( {self._op}\n{inner}\n{indent})'

    def __str__(self) -> str:
        return self.pretty()

class BinaryOp(Op):
    left: str|Op
    right: str|Op

    def __init__(self, left: str|Op, right: str|Op):
        self.left = left
        self.right = right

    def needs_expansion(self) -> bool:
        return (isinstance(self.left, Op) and self.left.needs_expansion()) or (isinstance(self.right, Op) and self.right.needs_expansion())

    def pretty(self, indent_level: int = 0) -> str:
        indent = '  ' * indent_level

        if not self.needs_expansion():
            return f'{indent}( {self._op} {self.left} {self.right} )'

        left = self.left.pretty(indent_level=indent_level+1) if isinstance(self.left, NaryOp) else f'{indent}  {self.left}'
        right = self.right.pretty(indent_level=indent_level+1) if isinstance(self.right, NaryOp) else f'{indent}  {self.right}'

        return f'{indent}( {self._op}\n{left}\n{right}\n{indent})'

    def __str__(self) -> str:
        return self.pretty()

class NaryOp(Op):
    args: list[str|Op]

    def __init__(self, *args: str|Op):
        self.args = list(args)

    def needs_expansion(self) -> bool:
        return any(isinstance(arg, Op) for arg in self.args)

    def pretty(self, indent_level: int = 0) -> str:
        indent = '  ' * indent_level

        if len(self.args) == 0:
            return ''

        if not self.needs_expansion():
            return f'{indent}( {self._op} {" ".join([str(arg) for arg in self.args])} )'

        inner = f'\n'.join([str(arg) if isinstance(arg,str) else arg.pretty(indent_level=indent_level+1) for arg in self.args])
        return f'{indent}( {self._op}\n{inner}\n{indent})'

    def __str__(self) -> str:
        return self.pretty()

    def append(self, arg: str|Op):
        self.args.append(arg)

    def insert(self, index: int, arg: str|Op):
        self.args.insert(index, arg)

    def __iter__(self):
        return iter(self.args)

class Or(NaryOp):
    _op = 'or'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class And(NaryOp):
    _op = 'and'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class Not(UnaryOp):
    _op = 'not'

    def __init__(self, arg: str|Op):
        super().__init__(arg)

class Addition(NaryOp):
    _op = '+'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class Subtraction(NaryOp):
    _op = '-'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class Multiplication(NaryOp):
    _op = '*'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class Division(NaryOp):
    _op = 'div'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class Modulo(NaryOp):
    _op = 'mod'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class Less(BinaryOp):
    _op = '<'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class Greater(BinaryOp):
    _op = '>'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class LessEqual(BinaryOp):
    _op = '<='

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class GreaterEqual(BinaryOp):
    _op = '>='

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class Equal(BinaryOp):
    _op = '='

    def __init__(self, *args: str|Op):
        super().__init__(*args)

class NotEqual(BinaryOp):
    _op = 'distinct'

    def __init__(self, *args: str|Op):
        super().__init__(*args)

