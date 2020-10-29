"""
The textual (Step) plist library.
"""
__all__ = [
    "TextPlistTypes",
    "TextPlistDialects",
    "TextPlistParser",
    "TextPlistWriter",
    "patch",
    "plistlib",
]

from .impl import (
    TextPlistTypes,
    TextPlistDialects,
    TextPlistParser,
    TextPlistWriter,
)
from .patch import patch
