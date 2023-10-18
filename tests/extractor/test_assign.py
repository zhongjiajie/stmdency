from __future__ import annotations

import pytest

from tests.testing import assert_extract

assign_cases = [
    (
        "simple assignment",
        """
        a = 1
        b = a + 2
        """,
        {
            "a": "a = 1",
            "b": """\
                    a = 1\n
                    b = a + 2""",
        },
    ),
    (
        "assignment override",
        """
        a = 1
        b = a + 2
        a = 3
        """,
        {
            "b": """\
                    a = 1\n
                    b = a + 2""",
            "a": "a = 3",
        },
    ),
    (
        "nested assignment",
        """
        a = 1
        b = a + 2
        c = b + 3
        d = 4
        e = b + d
        f = c + e
        """,
        {
            "a": "a = 1",
            "b": """\
                    a = 1\n
                    b = a + 2""",
            "c": """\
                    a = 1\n
                    b = a + 2\n
                    c = b + 3""",
            "d": "d = 4",
            "e": """\
                    a = 1\n
                    b = a + 2\n
                    d = 4\n
                    e = b + d""",
            "f": """\
                    a = 1\n
                    b = a + 2\n
                    c = b + 3\n
                    d = 4\n
                    e = b + d\n
                    f = c + e""",
        },
    ),
    (
        "build-in function",
        """
        a = 1
        b = int("2") + 3
        """,
        {
            "a": "a = 1",
            "b": 'b = int("2") + 3',
        },
    ),
]


@pytest.mark.parametrize("name, source, expects", assign_cases)
def test_assign(name: str, source: str, expects: dict[str, str]) -> None:
    """Test assignment extraction."""
    assert_extract(name, source, expects)
