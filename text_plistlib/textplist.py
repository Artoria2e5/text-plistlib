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
            skipkeys=False, gnustep=True, escape_unicode=False, float_precision=None,
            strings=False):
        pass

    def _width(indentstr):
        return len(indentstr.replace("\t", " " * 8))
    
    def write(self, value):
        self._write_dict(value)
    
    def _write_value(self, value):
        if isinstance(value, datetime):
            pass


def _is_fmt_text(header):
    prefixes = (b'{', b'\xEF\xBB\xBF', b'/*', b'//')

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
    if len(sys.argv) > 1:
        txp = TextPlistParser()
        print(txp.parse(open(sys.argv[1])))
