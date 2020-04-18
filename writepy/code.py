import typing as t
import ast_compat as astc
import ast

T = t.TypeVar("T")


class ToString(t.Generic[T]):
    def __init__(self, string: t.Union["Expr", ast.expr, str]):
        if isinstance(string, Expr):
            string = string.repr
        self.string = string

    def __repr__(self):
        if isinstance(self.string, ast.expr):
            return astc.unparse(self.string)

        return self.string


def ast_from_repr(x: t.Any) -> ast.expr:
    return astc.Constant(ToString(repr(x)))


def ast_as_is(x: str) -> ast.expr:
    return astc.Constant(ToString(x))


def as_ast_expr(x: t.Union[ast.expr, "Expr"]):
    if isinstance(x, Expr):
        return getattr(x, "_repr")
    if isinstance(x, ast.expr):
        return x
    raise TypeError(x)


class Expr(t.Generic[T]):
    def __init__(self, repr: ast.expr):
        self._repr = repr

    def __getitem__(self, item) -> "Expr":
        item = as_ast_expr(item)
        return Expr(
            astc.Subscript(
                value=self._repr, slice=astc.Index(value=item), ctx=astc.Load()
            )
        )

    def META_ARGS(self):
        return (Expr(astc.Starred(self._repr, ctx=astc.Load())),)

    def META_KWS(self):
        return {"": Expr(astc.keyword(arg=None, value=self._repr))}

    def __getattr__(self, attr: str) -> "Expr":
        return Expr(astc.Attribute(value=self._repr, attr=attr, ctx=astc.Load()))

    def __call__(self, *args, **kwargs) -> "Expr":

        kw = kwargs.pop("", None)
        args = list(map(as_ast_expr, args))
        kws = [astc.keyword(arg=k, value=as_ast_expr(v)) for k, v in kwargs.items()]
        if kw:
            kws.append(as_ast_expr(kw))

        return Expr(astc.Call(func=self._repr, args=args, keywords=kws))

    def __str__(self):
        return astc.unparse(self._repr)


def expr_from_repr(v: T) -> Expr[T]:
    return Expr[T](ast_from_repr(v))


def expr_as_is(_: t.Type[T], code: str) -> Expr[T]:
    return Expr[T](ast_as_is(code))
