from __future__ import annotations

import pytest

from tests.testing import assert_extract

import_cases = [
    (
        "simple statement from import",
        """
        from datetime import datetime
        now = datetime.now()
        """,
        {
            "now": """\
                    from datetime import datetime\n
                    now = datetime.now()""",
        },
    ),
    (
        "simple function",
        """
        from datetime import datetime
        def foo():
            print(datetime.now())
        """,
        {
            "foo": """\
                    from datetime import datetime\n
                    def foo():
                        print(datetime.now())
                    """,
        },
    ),
    (
        "function use outside variable",
        """
        from datetime import datetime
        now = datetime.now()
        def foo():
            print(now)
        """,
        {
            "now": """\
                    from datetime import datetime\n
                    now = datetime.now()""",
            "foo": """\
                    from datetime import datetime\n
                    now = datetime.now()\n
                    def foo():
                        print(now)
                    """,
        },
    ),
    (
        "nested function call",
        """
        from datetime import datetime
        def foo():
            print(datetime.now())
        def bar():
            foo()
        """,
        {
            "foo": """\
                    from datetime import datetime\n
                    def foo():
                        print(datetime.now())
                    """,
            "bar": """\
                    from datetime import datetime\n
                    def foo():
                        print(datetime.now())\n\n
                    def bar():
                        foo()
                    """,
        },
    ),
    (
        "nested function call",
        """
        from datetime import datetime
        import time
        t = 1
        def foo(t):
            print(datetime.now())
            print(t)
        def bar():
            t = time.time()
            foo(t)
        """,
        {
            "foo": """\
                    from datetime import datetime\n
                    def foo(t):
                        print(datetime.now())
                        print(t)
                    """,
            "bar": """\
                    import time\n
                    from datetime import datetime\n
                    def foo(t):
                        print(datetime.now())
                        print(t)\n\n
                    def bar():
                        t = time.time()
                        foo(t)
                    """,
        },
    ),
    (
        "alias",
        """
        import pandas as pd
        df = pd.DataFrame()
        """,
        {
            "df": """\
                   import pandas as pd\n
                   df = pd.DataFrame()""",
        },
    ),
]


@pytest.mark.parametrize("name, source, expects", import_cases)
def test_import(name: str, source: str, expects: dict[str, str]) -> None:
    """Test import statement."""
    assert_extract(name, source, expects)
