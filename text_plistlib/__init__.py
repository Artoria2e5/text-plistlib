#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The parser and writer classes for text plists. Implements a format for plistlib.
"""
import plistlib
from .pparser import PlistParser
from .semantics import PlistSemantics
from datetime import datetime, timezone
from enum import IntEnum
from typing import TypeVar
from collections import OrderedDict
import binascii
from io import TextIOBase

TextPlistDialects = IntEnum("TextPlistDialects", "OpenStep GNUstep PyText")
# Plist types
T = TypeVar(
    "T",
    str,
    bytes,
    int,
    float,
    datetime,
    dict,
    list,
    tuple,
    plistlib.UID,
    plistlib.Data,
    bool,
)


class TextPlistParser:
    def __init__(
        self, use_builtin_types=True, dict_type=dict, cfuid=True, encoding="utf-8-sig"
    ):
        self.use_builtin_types = use_builtin_types
        self.dict_type = dict_type
        self.cfuid = cfuid
        self.encoding = encoding

    def parse(self, fp: TextIOBase) -> T:
        parser = PlistParser()
        data = fp.read()
        if isinstance(data, bytes):
            data = data.decode(self.encoding)
        model = parser.parse(
            data,
            semantics=PlistSemantics(
                self.use_builtin_types, self.dict_type, self.cfuid
            ),
        )
        return model


class TextPlistWriter:
    def __init__(
        self,
        file,
        indent_level=0,
        indent="\t",
        sort_keys=True,
        skipkeys=False,
        dialect=TextPlistDialects.GNUstep,
        escape_unicode=False,
        float_precision=None,
        fallback=True,
        strings=False,
        utc=True,
    ):
        self.buf = ""
        self.indent_level = 0
        self.indent = indent
        self.sort_keys = sort_keys
        self.dialect = dialect
        self.utc = utc
        self.strings = strings

    @staticmethod
    def _width(indentstr):
        return len(indentstr.replace("\t", " " * 8))

    def _indent(self):
        self.buf += self.indent * self.indent_level

    def write(self, value):
        if self.strings and isinstance(value, dict):
            self.write_dict(value, stringstop=True)
        else:
            self.write_value(value)

    def write_none(
        self,
        _,
    ):
        if self.dialect == TextPlistDialects.PyText:
            self.buf += ""
        elif self.fallback:
            self.buf += '""'
        else:
            raise TypeError(
                "None is not directly representable in dialect {f!s}.".format(
                    f=self.dialect
                )
            )

    def write_uid(self, val):
        if self.dialect == TextPlistDialects.PyText:
            self.buf += "<*U%d>" % val.data
        else:
            self.write_dict({"CF$UID": int(val.data)})

    def write_int(self, val):
        if self.dialect >= TextPlistDialects.GNUstep:
            self.buf += "<*I%d>" % val
        else:
            self.buf += "%d" % val

    def write_float(self, val):
        if self.dialect >= TextPlistDialects.GNUstep:
            self.buf += "<*R{v}>".format(v=val)
        else:
            self.buf += str(val)

    def write_data(self, val):
        if isinstance(val, plistlib.Data):
            val = val.data
        if self.dialect >= TextPlistDialects.GNUstep:
            self.buf += "<["
            self.buf += binascii.b2a_base64(val).decode("ascii")
            self.buf += "]>"
        else:
            self.buf += "<"
            self.buf += val.hex(" ", -4)
            self.buf += ">"

    def write_datetime(self, val):
        if self.utc:
            val = val.astimezone(timezone.utc)
        formatted = val.strftime("%Y-%m-%d %H:%M:%S %z")
        if self.dialect >= TextPlistDialects.GNUstep:
            self.buf += "<*D"
            self.buf += formatted
            self.buf += ">"
        else:
            self.buf += formatted

    def write_dict(self, val, stringstop=False):
        keys = val.keys()
        if self.sort_keys:
            keys = sorted(keys)
        if not stringstop:
            self.buf += "{\n"
            self.indent_level += 1
        for k in keys:
            v = val[k]
            self._indent()
            self.write_string(k)
            if v is None and (self.dialect == TextPlistDialects.PyText or stringstop):
                pass
            else:
                self.buf += " = "
                self.write_value(v)
            self.buf += ";\n"
        if not stringstop:
            self.indent_level -= 1
            self._indent()
            self.buf += "}"

    def write_list(self, val):
        self.buf += "(\n"
        self.indent_level += 1
        for v in val:
            self._indent()
            self.write_value(v)
            self.buf += ",\n"
        self.indent_level -= 1
        self._indent()
        self.buf += ")"

    def write_bool(self, val):
        if self.dialect >= TextPlistDialects.GNUstep:
            self.buf += "<*B"
            self.buf += "Y" if val else "N"
            self.buf += ">"
        else:
            self.buf += str(val)

    def write_value(self, val):
        if val is None:
            self.write_none(self)
        else:
            method = TextPlistWriter.dumpers.get(type(val))
            if method is None:
                for k, v in TextPlistWriter.dumpers:
                    if isinstance(val, k):
                        method = v
                        break
                else:
                    raise TypeError(
                        "{val!r} is not directly representable in a plist.".format(
                            val=val
                        )
                    )
            getattr(self, method)(self, val)

    # Dict[Type[T], Callable[[Any, T], None]]
    dumpers = OrderedDict(
        [
            (str, "write_string"),
            (bool, "write_bool"),
            (int, "write_int"),
            (float, "write_float"),
            (bytes, "write_data"),
            (plistlib.UID, "write_uid"),
            (plistlib.Data, "write_data"),
            (datetime, "write_datetime"),
            (dict, "write_dict"),
            (list, "write_list"),
            (tuple, "write_list"),
        ]
    )


def _is_fmt_text(header):
    prefixes = (b"{", b"{", b"/*", b"//")

    for pfx in prefixes:
        if header.startswith(pfx) or header.startswith(b"\xEF\xBB\xBF" + pfx):
            return True

    return (
        not header.startswith(b"<?xml")
        and not header.startswith(b"<plist")
        and "=" in header
    )


FMT_TEXT_HANDLER = {
    "detect": _is_fmt_text,
    "parser": TextPlistParser,
    "writer": TextPlistWriter,
}


def patch(plistlib):
    """Monkey patch the plistlib module passed in. Things could go very wrong..."""
    import enum
    PF = enum.Enum('PlistFormat', 'FMT_XML FMT_BINARY FMT_TEXT', module=__name__)

    plistlib._FORMATS = {
        PF.FMT_XML: plistlib._FORMATS[plistlib.FMT_XML],
        PF.FMT_BINARY: plistlib._FORMATS[plistlib.FMT_BINARY],
        PF.FMT_TEXT: FMT_TEXT_HANDLER,
    }

    plistlib.PlistFormat = PF
    plistlib.__dict__.update(PF.__members__)

    # TODO: replace default vals in {load,dump}{,s} by __defaults__ wrigging

    return plistlib


if __name__ == "__main__":
    import sys
    from collections import OrderedDict

    if len(sys.argv) > 1:
        txp = TextPlistParser(dict_type=OrderedDict)
        print(txp.parse(open(sys.argv[1])))
