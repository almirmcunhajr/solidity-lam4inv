class Op:
    _op: str

    def __eq__(self, other) -> bool:
        if not isinstance(other, Op):
            return False
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

class UnaryOp(Op):
    arg: str|Op

    def __init__(self, arg: str|Op):
        self.arg = arg

    def __str__(self) -> str:
        return f'({self._op} {self.arg})'

class BinaryOp(Op):
    left: str|Op
    right: str|Op

    def __init__(self, left: str|Op, right: str|Op):
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f'({self._op} {self.left} {self.right})'

class NaryOp(Op):
    args: list[str|Op]

    def __init__(self, *args: str|Op):
        self.args = list(args)

    def __str__(self) -> str:
        return f'({self._op} {" ".join([str(arg) for arg in self.args])})'

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

