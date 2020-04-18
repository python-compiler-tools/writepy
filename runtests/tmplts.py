from writepy import *
import ast
import ast_compat as astc
import typing


def f(base: str):
    seq: typing.List = []
    for each in range(5):
        lhs = expr_as_is(int, base + str(each))
        rhs = expr_from_repr(each)
        call = Q[base + 1](lhs, rhs)
        with CG >> seq:
            UNQ[call]
            UNQ[lhs] = (UNQ[rhs], UNQ[expr_from_repr(base)])
    return seq


mk_cg(f)

seq_ = f("base")
print(astc.unparse(ast.Module(seq_)))
