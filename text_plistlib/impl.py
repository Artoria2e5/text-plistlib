#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The parser and writer classes for text plists. Implements a format for plistlib.
"""
import binascii
import plistlib
from collections import OrderedDict
from datetime import datetime, timezone
from enum import IntEnum
from typing import IO, Union, Dict, Callable

from .pparser import PlistParser
from .semantics import PlistSemantics

Data = plistlib.__dict__.get("Data", None)
UID = plistlib.UID
TextPlistDialects = IntEnum("TextPlistDialects", "OpenStep GNUstep PyText")
# Plist types
T = Union[str, bytes, int, float, datetime, dict, list, tuple, UID, bool]


class TextPlistParser:
    def __init__(
        self,
        *,
        dict_type=dict,
        cfuid: bool = True,
        encoding: str = "utf-8-sig",
    ):
        self.dict_type = dict_type
        self.cfuid = cfuid
        self.encoding = encoding

    def parse(self, fp: IO) -> T:
        parser = PlistParser()
        data = fp.read()
        if isinstance(data, bytes):
            data = data.decode(self.encoding)
        model = parser.parse(
            data,
            semantics=PlistSemantics(dict_type=self.dict_type, cfuid=self.cfuid),
        )
        return model


class TextPlistWriter:
    def __init__(
        self,
        file: IO,
        *,
        indent_level: int = 0,
        indent: str = "\t",
        sort_keys: bool = True,
        skipkeys: bool = False,
        dialect: TextPlistDialects = TextPlistDialects.GNUstep,
        escape_unicode: bool = False,
        float_fmt: str = "{v}",
        fallback: bool = True,
        strings: bool = False,
        utc: bool = True,
    ):
        """
        Text Plist Writer.

        :param dialect: Which dialect to use.
        :param escape_unicode: Whether to escape every non-ASCII character, not
        just the unprintable ones.
        :param fallback: Whether to write not-really-exact values when the
        format does not support serializing something.
        :param strings: Whether we are writng a strings file.
        """
        self.fp = file
        self.indent_level = 0
        self.indent = indent
        self.sort_keys = sort_keys
        self.skipkeys = skipkeys
        self.dialect = dialect
        self.escape_unicode = escape_unicode
        self.float_fmt = float_fmt
        self.fallback = fallback
        self.strings = strings
        self.utc = utc

    @staticmethod
    def _width(indentstr):
        return len(indentstr.replace("\t", " " * 8))

    def _indent(self):
        self.fp.write(self.indent * self.indent_level)

    def write(self, value):
        """Write the value into the file IO."""
        if self.strings and isinstance(value, dict):
            self.write_dict(value, strings_top=True)
        else:
            self.write_value(value)

    def write_none(
        self,
        _,
    ):
        if self.dialect == TextPlistDialects.PyText:
            self.fp.write("")
        elif self.fallback:
            self.fp.write('""')
        else:
            raise TypeError(
                "None is not directly representable in dialect {f!s}.".format(
                    f=self.dialect
                )
            )

    def write_string(self, s):
        # I thought I wrote this before but apparently I didn't.
        # Anyway, let's cheat and use the JSON encoder. What can go wrong?
        import json

        self.fp.write(json.dumps(s, ensure_ascii=self.escape_unicode))

    def write_uid(self, val):
        if self.dialect == TextPlistDialects.PyText:
            self.fp.write("<*U%d>" % val.data)
        else:
            self.write_dict({"CF$UID": int(val.data)})

    def write_int(self, val):
        if self.dialect >= TextPlistDialects.GNUstep:
            self.fp.write("<*I%d>" % val)
        else:
            self.fp.write("%d" % val)

    def write_float(self, val):
        if self.dialect >= TextPlistDialects.GNUstep:
            self.fp.write("<*R{v}>".format(v=val))
        else:
            self.fp.write(str(val))

    def write_data(self, val):
        global Data
        if isinstance(val, Data):
            val: bytes = val.data
        # break-even at 3 and 4
        if self.dialect >= TextPlistDialects.GNUstep and len(val) < 5:
            self.fp.write("<[")
            self.fp.write(binascii.b2a_base64(val).decode("ascii"))
            self.fp.write("]>")
        else:
            self.fp.write("<")
            self.fp.write(val.hex(" ", -4))
            self.fp.write(">")

    def write_datetime(self, val):
        if self.utc:
            val = val.astimezone(timezone.utc)
        formatted = val.strftime("%Y-%m-%d %H:%M:%S %z")
        if self.dialect >= TextPlistDialects.GNUstep:
            self.fp.write("<*D")
            self.fp.write(formatted)
            self.fp.write(">")
        else:
            self.fp.write(formatted)

    def write_dict(self, val, strings_top=False):
        keys = val.keys()
        if self.sort_keys:
            keys = sorted(keys)
        if not strings_top:
            self.fp.write("{\n")
            self.indent_level += 1
        for k in keys:
            if not isinstance(k, str):
                if self._skipkeys:
                    continue
                raise TypeError("keys must be strings")
            v = val[k]
            self._indent()
            self.write_string(k)
            if v is None and (self.dialect == TextPlistDialects.PyText or strings_top):
                pass
            else:
                self.fp.write(" = ")
                self.write_value(v)
            self.fp.write(";\n")
        if not strings_top:
            self.indent_level -= 1
            self._indent()
            self.fp.write("}")

    def write_list(self, val):
        self.fp.write("(\n")
        self.indent_level += 1
        for v in val:
            self._indent()
            self.write_value(v)
            self.fp.write(",\n")
        self.indent_level -= 1
        self._indent()
        self.fp.write(")")

    def write_bool(self, val):
        if self.dialect >= TextPlistDialects.GNUstep:
            self.fp.write("<*B")
            self.fp.write("Y" if val else "N")
            self.fp.write(">")
        else:
            self.fp.write(str(val))

    def write_value(self, val):
        if val is None:
            self.write_none(self)
        else:
            method = TextPlistWriter.dumpers.get(type(val))
            if method is None:
                for k, v in TextPlistWriter.dumpers.items():
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

    global Data
    # Dict[Type[T], Callable[[Any, T], None]]
    dumpers = OrderedDict(
        [
            (str, "write_string"),
            (bool, "write_bool"),
            (int, "write_int"),
            (float, "write_float"),
            (bytes, "write_data"),
            (UID, "write_uid"),
            (Data, "write_data"),
            (datetime, "write_datetime"),
            (dict, "write_dict"),
            (list, "write_list"),
            (tuple, "write_list"),
        ]
    )


def is_fmt_text(header: bytes) -> bool:
    prefixes = (b"{", b"{", b"/*", b"//")

    for pfx in prefixes:
        if header.startswith(pfx) or header.startswith(b"\xEF\xBB\xBF" + pfx):
            return True

    return (
        not header.startswith(b"<?xml")
        and not header.startswith(b"<plist")
        and b"=" in header
    )


FMT_TEXT_HANDLER: Dict[str, Callable] = {
    "detect": is_fmt_text,
    "parser": TextPlistParser,
    "writer": TextPlistWriter,
}


if __name__ == "__main__":
    import sys
    from collections import OrderedDict

    if len(sys.argv) > 1:
        txp = TextPlistParser(dict_type=OrderedDict)
        print(txp.parse(open(sys.argv[1])))
