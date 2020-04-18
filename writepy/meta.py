from writepy.matcher import *
from writepy.code import Expr, ast_as_is, as_ast_expr
from inspect import getsource
import ast_compat as astc
import ast
import pickle

__all__ = ["mk_cg"]

UNQUOTE = "UNQ"  # unquote
QUOTE = "Q"  # quote
BUILD = "CG"  # codegen
valid_with = obj(
    items=seq(
        obj(
            context_expr=isa(astc.BinOp)
            + obj(left=isa(astc.Name) + obj(id=BUILD), op=isa(astc.RShift),)
        )
    )
)

valid_unq_sub = obj(value=isa(astc.Name) + obj(id=UNQUOTE), slice=isa(astc.Index))
valid_q_sub = obj(value=isa(astc.Name) + obj(id=QUOTE), slice=isa(astc.Index))


class SymbolSplicing(ast.NodeTransformer):
    def __init__(self, global_dict, local_dict, filename="<unknown>"):
        self.local_dict = local_dict
        self.global_dict = global_dict
        self.filename = filename

    def visit_Subscript(self, node: astc.Subscript):
        if valid_unq_sub.match(node):
            code = compile(astc.unparse(node.slice.value), self.filename, "eval")
            v = eval(code, self.global_dict, self.local_dict)
            assert isinstance(v, Expr)
            return getattr(v, '_repr')

        return self.generic_visit(node)

    def subst_exp(self, b):
        exp = pickle.loads(b)
        return self.visit(exp)
    

    def write_stmts_(self, bs: bytes, output: list):
        stmts = pickle.loads(bs)
        output.extend([self.visit(each) for each in stmts])


ast_call_globals = Expr(ast_as_is("globals"))()
ast_call_locals = Expr(ast_as_is("locals"))()
mk_splicing = Expr(
    ast_as_is("__import__('importlib').import_module('writepy.meta').SymbolSplicing")
)(ast_call_globals, ast_call_locals, Expr(ast_as_is('__file__')))
expr_mk = Expr(ast_as_is("__import__('importlib').import_module('writepy.code').Expr"))

class CodeTransform(ast.NodeTransformer):
    def visit_With(self, with_ast: ast.With):
        if valid_with.match(with_ast):
            output_to = self.visit(with_ast.items[0].context_expr.right)
            bs = pickle.dumps([self.visit(each) for each in with_ast.body])
            bs = astc.Constant(bs)
            return astc.Expr(as_ast_expr(mk_splicing.write_stmts_(bs, output_to)))
        else:
            return self.generic_visit(with_ast)

    def visit_Subscript(self, sub: astc.Subscript):
        if valid_q_sub.match(sub):
            b = pickle.dumps(self.visit(sub.slice.value))
            return as_ast_expr(expr_mk(mk_splicing.subst_exp(astc.Constant(b))))
        return self.generic_visit(sub)


def mk_cg(f):
    nd = ast.parse(getsource(f))
    nd2 = CodeTransform().visit(nd)
    exec(astc.unparse(nd2), f.__globals__)

