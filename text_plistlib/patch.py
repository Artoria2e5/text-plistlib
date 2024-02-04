"""
Patching utilities.
"""
import warnings
from types import FunctionType, ModuleType
from enum import Enum

from .impl import FMT_TEXT_HANDLER


def patch(plistlib: ModuleType, *, handler=FMT_TEXT_HANDLER) -> ModuleType:
    """
    Monkey patch the plistlib module passed in. Things could go very wrong...

    FIXME: convince the mypy we are dealing with plistlib in particular.
    """
    assert type(plistlib) == ModuleType
    if plistlib.__name__ != "plistlib":
        warnings.warn("Patch called on non-plistlib module?", RuntimeWarning)

    PF = Enum("PlistFormat", "FMT_XML FMT_BINARY FMT_TEXT", module=__name__)

    plistlib._FORMATS = {
        PF.FMT_XML: plistlib._FORMATS[plistlib.FMT_XML],
        PF.FMT_BINARY: plistlib._FORMATS[plistlib.FMT_BINARY],
        PF.FMT_TEXT: handler,
    }

    translation = {
        plistlib.FMT_XML: PF.FMT_XML,
        plistlib.FMT_BINARY: PF.FMT_BINARY,
    }

    plistlib.PlistFormat = PF
    plistlib.__dict__.update(PF.__members__)

    # TODO: Do a proper rewrite for passing all of **kwargs
    # TODO: Maybe write a non-patch wrapper version too??
    # For now we are just allowing people to change the handler -- by subclassing
    # they should be able to set some defaults.
    for _, f in plistlib.__dict__.items():
        if isinstance(f, FunctionType):
            if f.__defaults__ is not None:
                f.__defaults__ = tuple(translation.get(x, x) for x in f.__defaults__)
            if f.__kwdefaults__ is not None:
                f.__kwdefaults__ = {
                    k: translation.get(v, v) for k, v in f.__kwdefaults__.items()
                }

    return plistlib
