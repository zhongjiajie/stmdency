from typing import Dict

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
]


@pytest.mark.parametrize("name, source, expects", import_cases)
def test_import(name: str, source: str, expects: Dict[str, str]) -> None:
    assert_extract(name, source, expects)
