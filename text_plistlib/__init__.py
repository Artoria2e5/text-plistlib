"""
The textual (Step) plist library.
"""
from .impl import (
    T as TextPlistTypes,
    TextPlistDialects,
    TextPlistParser,
    TextPlistWriter,
)
from .patch import patch

__all__ = [
    "TextPlistTypes",
    "TextPlistDialects",
    "TextPlistParser",
    "TextPlistWriter",
    "patch",
]
