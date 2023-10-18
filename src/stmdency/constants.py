from enum import Enum
from typing import Final


class TOKEN(str, Enum):
    """Constants Token."""

    EXTRACTOR_NEW_LINE: Final[str] = "\n\n"
