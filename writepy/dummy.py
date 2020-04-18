import typing as t
from writepy.code import Expr
T = t.TypeVar("T")


class _Q:
    def __getitem__(self, item: T) -> Expr[T]:
        raise RuntimeError("calling a compile time thing!")


Q = _Q()


class _UNQ:
    def __setitem__(self, key: Expr[T], value: T):
        raise RuntimeError("calling a compile time thing!")

    def __getitem__(self, item: Expr[T]) -> T:
        raise RuntimeError("calling a compile time thing!")


UNQ = _UNQ()


class _CG:
    def __rshift__(self, other: list):
        raise RuntimeError("calling a compile time thing!")


CG = _CG()
