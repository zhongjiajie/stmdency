from __future__ import annotations

import textwrap

from stmdency.extractor import Extractor


def assert_extract(name: str, source: str, expects: dict[str, str]) -> None:
    wrap_source = textwrap.dedent(source)
    extractor = Extractor(source=wrap_source)
    for expect in expects:
        actual = extractor.get_code(expect)
        expect_wrap = textwrap.dedent(expects[expect])
        assert (
            actual == expect_wrap
        ), f"Case `{name}` key `{expect}` error:\nexcept:\n{expect_wrap}\nbut got:\n{actual}"
