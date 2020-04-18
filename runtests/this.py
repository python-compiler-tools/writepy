import writepy.matcher as wm

check_if_length_greater_than_2 = wm.Shape(lambda x: len(x) > 2)
check_if_len_greater_than_2_and_the_2nd_elt_is_int = (check_if_length_greater_than_2[2](lambda x: isinstance(x, int)))
print(wm.match(check_if_len_greater_than_2_and_the_2nd_elt_is_int, [1, 2, "3"]))
print(wm.match(check_if_len_greater_than_2_and_the_2nd_elt_is_int, [1, 2, 3]))


class Foo:
    foo = 1


check_if_is_a_Foo = wm.Shape(lambda x: isinstance(x, Foo))
check_if_is_a_Foo_and_the_field_foo_less_than_2 = (check_if_is_a_Foo.foo(lambda x: x < 2))
print(wm.match(check_if_is_a_Foo_and_the_field_foo_less_than_2, Foo()))
