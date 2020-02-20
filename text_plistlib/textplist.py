#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The parser and writer classes for text plists. Implements a format for plistlib.
"""
import tatsu
import plistlib
from pparser import PlistParser
from semantics import PlistSemantics
from datetime import datetime
from enum import IntEnum
from typing import List, Dict, TypeVar, Union, Type, Callable, Any

TextPlistDialects = IntEnum('TextPlistDialects', 'OpenStep GNUstep PyText')
# Plist types
T = TypeVar('T', str, bytes, int, float, datetime, dict, list, tuple, plistlib.UID, plistlib.Data, None)

class TextPlistParser:
    def __init__(self, use_builtin_types=True, dict_type=dict, encoding='utf-8-sig'):
        self._use_builtin_types = use_builtin_types
        self._dict_type = dict_type
        self.encoding = encoding
    
    def parse(self, fp):
        parser = PlistParser()
        data = fp.read()
        if isinstance(data, bytes):
            data = data.decode(self.encoding)
        model = parser.parse(data, semantics=PlistSemantics(self._use_builtin_types, self._dict_type))
        return model

class TextPlistWriter:
    def __init__(
            self, file, indent_level=0, indent="\t", sort_keys=True,
            skipkeys=False, dialect=TextPlistDialects.GNUstep, escape_unicode=False, float_precision=None,
            fallback=True, strings=False):
        self.buf = ''
        pass

    def _width(indentstr):
        return len(indentstr.replace("\t", " " * 8))
    
    def _indent(self):
        self.buf += indent * indent_level
    
    def write(self, value):
        self.write_value(value)
    
    def write_none(self, _):
        if dialect == TextPlistDialects.PyText:
            self.buf += ''
        elif self.fallback:
            self.buf += '""'
    
    def write_int\

    def write_value(self, value):
        self._indent()
        if value is None:
            self.write_none(value)

        if isinstance(value, datetime):
            pass
    
    dumpers: Dict[Union[Type[T], None], Callable[[Any, Union[T, None]], None]] = {
        str: write_string,
        None: write_none,
        dict: write_dict,
        int: write_int,
        float: write_float,
        plistlib.UID: write_uid,
        plistlib.Data: write_data,
        bytes: write_data,
        datetime: write_datetime,
        list: write_list,
        tuple: write_tuple
    }


def _is_fmt_text(header):
    prefixes = (b'{', b'{', b'\xEF\xBB\xBF', b'/*', b'//')

    for pfx in prefixes:
        if header.startswith(pfx):
            return True
    
    return not header.startswith(b'<') and '=' in header;

FMT_TEXT_HANDLER = {
    'detect': _is_fmt_text,
    'parser': TextPlistParser,
    'writer': TextPlistWriter,
}

if __name__ == '__main__':
    import sys
    from collections import OrderedDict
    if len(sys.argv) > 1:
        txp = TextPlistParser(dict_type=OrderedDict)
        print(txp.parse(open(sys.argv[1])))
