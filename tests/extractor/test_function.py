from __future__ import annotations

import pytest

from tests.testing import assert_extract

func_cases = [
    (
        "simple function",
        """
        def foo():
            print('a')
        """,
        {
            "foo": """\
                    def foo():
                        print('a')
                    """,
        },
    ),
    (
        "simple function, start with multiple leading lines",
        """
        a = 1\n\n\n
        def foo():
            print('a')
        """,
        {
            "a": "a = 1",
            "foo": """\
                    def foo():
                        print('a')
                    """,
        },
    ),
    (
        "function use outside variable",
        """
        a = 1\n
        def foo():
            print(a)
        """,
        {
            "a": "a = 1",
            "foo": """\
                    a = 1\n
                    def foo():
                        print(a)
                    """,
        },
    ),
    (
        "function use same name outside variable and argument name",
        """
        a = 1\n
        def foo(a):
            print(a)
        """,
        {
            "a": "a = 1",
            "foo": """\
                    def foo(a):
                        print(a)
                    """,
        },
    ),
    (
        "function use outside variable as argument default value",
        """
        a = 1\n
        def foo(a=a):
            print(a)
        """,
        {
            "foo": """\
                    a = 1\n
                    def foo(a=a):
                        print(a)
                    """,
        },
    ),
    (
        "function have both same variable in different scope",
        """
        a = 1\n
        def foo():
            a = 2
            print(a)
        """,
        {
            # "a": "a = 1",
            "foo": """\
                    def foo():
                        a = 2
                        print(a)
                    """,
        },
    ),
    (
        "use both global and local variable",
        """
        a = 1\n
        def foo():
            b = 2
            c = a + b
            print(c)
        """,
        {
            # "a": "a = 1",
            "foo": """\
                    a = 1\n
                    def foo():
                        b = 2
                        c = a + b
                        print(c)
                    """,
        },
    ),
    (
        "nested function",
        """
        a = 1
        def bar():
            print('bar')
        def foo():
            bar()
        """,
        {
            # "a": "a = 1",
            # "bar": """\
            #         def bar():
            #             print('bar')
            #         """,
            "foo": """\
                    def bar():
                        print('bar')\n\n
                    def foo():
                        bar()
                    """,
        },
    ),
    (
        "nested function with parameter",
        """
        a = 1
        def bar():
            print(a)
        def foo():
            bar()
        """,
        {
            "a": "a = 1",
            "bar": """\
                    a = 1\n
                    def bar():
                        print(a)
                    """,
            "foo": """\
                    a = 1\n
                    def bar():
                        print(a)\n\n
                    def foo():
                        bar()
                    """,
        },
    ),
    (
        "nested function with two parameter",
        """
        a = 1
        b = 2
        def bar():
            print(a)
        def foo():
            bar(b)
        """,
        {
            "a": "a = 1",
            "b": "b = 2",
            "bar": """\
                    a = 1\n
                    def bar():
                        print(a)
                    """,
            "foo": """\
                    a = 1\n
                    def bar():
                        print(a)\n\n
                    b = 2\n
                    def foo():
                        bar(b)
                    """,
        },
    ),
    (
        "nested function with global and local parameter",
        """
        a = 1
        b = 2
        def bar(b):
            print(a, b)
        def foo():
            bar()
        """,
        {
            "a": "a = 1",
            "bar": """\
                    a = 1\n
                    def bar(b):
                        print(a, b)
                    """,
            "foo": """\
                    a = 1\n
                    def bar(b):
                        print(a, b)\n\n
                    def foo():
                        bar()
                    """,
        },
    ),
    (
        "nested function with nested global parameter",
        """
        a = 1
        b = 2
        def bar():
            b = a + 3
            print(a, b)
        def foo():
            bar(b)
        """,
        {
            "a": "a = 1",
            "b": "b = 2",
            "bar": """\
                    a = 1\n
                    def bar():
                        b = a + 3
                        print(a, b)
                    """,
            "foo": """\
                    a = 1\n
                    def bar():
                        b = a + 3
                        print(a, b)\n\n
                    b = 2\n
                    def foo():
                        bar(b)
                    """,
        },
    ),
    # FIXME: this case is not supported yet, we should add config module to do this
    # (
    #     "decorator",
    #     """
    #     from functools import wraps
    #     a = 1
    #     @wraps
    #     def foo():
    #         b = a + 3
    #         print(a, b)
    #     """,
    #     {
    #         # "a": "a = 1",
    #         "foo": """\
    #                 from functools import wraps\n
    #                 a = 1\n
    #                 @wraps
    #                 def foo():
    #                     b = a + 3
    #                     print(a, b)
    #                 """,
    #     },
    # ),
    (
        "decorator config ignore",
        """
        from functools import wraps
        a = 1
        @wraps
        def foo():
            b = a + 3
            print(a, b)
        """,
        {
            "a": "a = 1",
            "foo": """\
                    a = 1\n
                    def foo():
                        b = a + 3
                        print(a, b)
                    """,
        },
    ),
]


@pytest.mark.parametrize("name, source, expects", func_cases)
def test_func(name: str, source: str, expects: dict[str, str]) -> None:
    assert_extract(name, source, expects)
