"""
Wrapper providing a plistlib interface. Better than a patch?
"""
__all__ = [
    "InvalidFileException",
    "FMT_XML",
    "FMT_BINARY",
    "FMT_TEXT",
    "load",
    "dump",
    "loads",
    "dumps",
    "UID",
]

import plistlib as pl
from enum import Enum
from io import BytesIO
from typing import BinaryIO

from .impl import FMT_TEXT_HANDLER, T

UID = pl.UID
InvalidFileException = pl.InvalidFileException

PF = Enum("TextPlistFormat", "FMT_XML FMT_BINARY FMT_TEXT", module=__name__)
globals().update(PF.__members__)
translation = {
    PF.FMT_XML: pl.FMT_XML,
    PF.FMT_BINARY: pl.FMT_BINARY,
}


def load(fp: BinaryIO, *, fmt=None, **kwargs) -> T:
    """Read a .plist file (forwarding all arguments)."""
    if fmt is None:
        header = fp.read(32)
        fp.seek(0)
        if FMT_TEXT_HANDLER["detect"](header):
            fmt = PF.FMT_TEXT

    if fmt == PF.FMT_TEXT:
        return FMT_TEXT_HANDLER["parser"](**kwargs).parse(fp)
    else:
        # This one can fail a bit more violently like the original
        return pl.load(fp, fmt=translation[fmt], **kwargs)


def loads(value: bytes, **kwargs) -> T:
    """Read a .plist file from a bytes object."""
    return load(BytesIO(value), **kwargs)


def dump(value: T, fp, *, fmt=PF.FMT_TEXT, **kwargs):
    if fmt == PF.FMT_TEXT:
        FMT_TEXT_HANDLER["writer"](fp, **kwargs)
    else:
        # ignore type -- let the real plistlib complain about None :)
        return pl.dump(value, fp, fmt=translation.get(fmt), **kwargs)  # type: ignore


def dumps(value: T, **kwargs) -> bytes:
    fp = BytesIO()
    dump(value, fp, **kwargs)
    return fp.getvalue()
