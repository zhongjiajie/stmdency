from __future__ import annotations

import pytest

from tests.testing import assert_extract

import_cases = [
    (
        "simple class with init",
        """
        class Foo:
            def __init__(self, arg1):
                self.arg1 = arg1
        def foo():
            f = Foo(arg1=1)
            print(f)
        """,
        {
            "foo": """\
                    class Foo:
                        def __init__(self, arg1):
                            self.arg1 = arg1\n\n
                    def foo():
                        f = Foo(arg1=1)
                        print(f)
                            """,
        },
    ),
]


@pytest.mark.parametrize("name, source, expects", import_cases)
def test_import(name: str, source: str, expects: dict[str, str]) -> None:
    """Test import statement."""
    assert_extract(name, source, expects)
