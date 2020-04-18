# writepy

A library for easing boilerplates in writing Python, with static checking support.

## Working with types

- UNQ: `Expr[T] -> T`, anti-quotation
- Q: `T -> Expr[T]`, quotation


## Code Generation

Q: what does `with CG >> seq: stmts...` mean?

A: Generating statically checked `stmts...` to variable `seq`, where `seq` shall have `.extend` method.

## Example: A Family of Variables with Index-concerned Initialization

```python
from writepy import *
import ast
import ast_compat as astc


def f(base: str):
    seq = []
    for each in range(5):
        lhs = expr_as_is(object, base + str(each))
        rhs = expr_from_repr(each)
        call = Q[base + 1](lhs, rhs)            
        with CG >> seq:
            UNQ[call]
            UNQ[lhs] = (UNQ[rhs], UNQ[expr_from_repr(base)])
    return seq


mk_cg(f)

seq_ = f("base")
print(astc.unparse(ast.Module(seq_)))
``` 

codegen:

```python
(base + 1)(base0, 0)
base0 = (0, 'base')
(base + 1)(base1, 1)
base1 = (1, 'base')
(base + 1)(base2, 2)
base2 = (2, 'base')
(base + 1)(base3, 3)
base3 = (3, 'base')
(base + 1)(base4, 4)
base4 = (4, 'base')
```
