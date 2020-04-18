import abc

__all__ = ["Shape", "obj", "val", "pred", "seq", "isa"]


class Shape:
    @abc.abstractmethod
    def match(self, value) -> bool:
        raise NotImplementedError

    def __add__(self, x: "Shape"):
        return ShapeAnd(self, x)


class ShapeAnd(Shape):
    def __init__(self, a: Shape, b: Shape):
        self.a = a
        self.b = b

    def match(self, value) -> bool:
        return self.a.match(value) and self.b.match(value)


class ObjectShape(Shape):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def match(self, value):
        unset = object()
        for k, v in self.kwargs.items():
            v_ = getattr(value, k, unset)
            if v_ is unset:
                return False
            if isinstance(v, Shape):
                if not v.match(v_):
                    return False
            elif v_ != v:
                return False

        return True


class PredicateShape(Shape):
    def __init__(self, func):
        self.func = func

    def match(self, value) -> bool:
        return self.func(value)


class EqShape(Shape):
    def __init__(self, v):
        self.v = v

    def match(self, value) -> bool:
        return self.v == value


class PartialSeqShape(Shape):
    def __init__(self, *shapes):
        self.shapes = shapes

    def match(self, value) -> bool:
        return all(
            a.match(b) if isinstance(a, Shape) else a == b
            for a, b in zip(self.shapes, value)
        )


obj = ObjectShape
seq = PartialSeqShape
val = EqShape
pred = PredicateShape


def isa(t: type):
    return PredicateShape(lambda x: isinstance(x, t))
