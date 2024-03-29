#!/usr/bin/env python

# CAVEAT UTILITOR
#
# This file was automatically generated by TatSu.
#
#    https://pypi.python.org/pypi/tatsu/
#
# Any changes you make to it will be overwritten the next time
# the file is generated.

from __future__ import annotations

import sys

from tatsu.buffering import Buffer
from tatsu.parsing import Parser
from tatsu.parsing import tatsumasu
from tatsu.parsing import leftrec, nomemo, isname # noqa
from tatsu.infos import ParserConfig
from tatsu.util import re, generic_main  # noqa


KEYWORDS = {}  # type: ignore


class PlistBuffer(Buffer):
    def __init__(self, text, /, config: ParserConfig = None, **settings):
        config = ParserConfig.new(
            config,
            owner=self,
            whitespace=None,
            nameguard=False,
            comments_re='/\\*.*?\\*/',
            eol_comments_re='//.*?$',
            ignorecase=False,
            namechars='',
            parseinfo=False,
        )
        config = config.replace(**settings)
        super().__init__(text, config=config)


class PlistParser(Parser):
    def __init__(self, /, config: ParserConfig = None, **settings):
        config = ParserConfig.new(
            config,
            owner=self,
            whitespace=None,
            nameguard=False,
            comments_re='/\\*.*?\\*/',
            eol_comments_re='//.*?$',
            ignorecase=False,
            namechars='',
            parseinfo=False,
            keywords=KEYWORDS,
            start='start',
        )
        config = config.replace(**settings)
        super().__init__(config=config)

    @tatsumasu()
    def _start_(self):  # noqa
        with self._choice():
            with self._option():
                with self._group():
                    self._value_()
                    self.name_last_node('v')
                    self._check_eof()

                    self._define(
                        ['v'],
                        []
                    )
            with self._option():
                with self._group():

                    def block3():
                        self._entry_()
                    self._closure(block3)
                    self.name_last_node('s')
                    self._check_eof()

                    self._define(
                        ['s'],
                        []
                    )
            self._error(
                'expecting one of: '
                '<array> <base64data> <dict> <entry>'
                '<hexdata> <string> <typed> <value>'
            )

    @tatsumasu('Entry')
    def _entry_(self):  # noqa
        self._string_()
        self.name_last_node('k')
        with self._optional():
            self._token('=')
            self._value_()
            self.name_last_node('v')

            self._define(
                ['v'],
                []
            )
        self._token(';')

        self._define(
            ['k', 'v'],
            []
        )

    @tatsumasu()
    def _value_(self):  # noqa
        with self._choice():
            with self._option():
                self._dict_()
            with self._option():
                self._array_()
            with self._option():
                self._string_()
            with self._option():
                self._hexdata_()
            with self._option():
                self._base64data_()
            with self._option():
                self._typed_()
            self._error(
                'expecting one of: '
                '\'"\' \'(\' \'<\' \'<*\' \'<[\' \'{\' <array>'
                '<base64data> <dict> <hexdata> <safechar>'
                '<string> <typed>'
                '[-#!$%&*+./0-9:?@A-Z^_a-z|~]+'
            )

    @tatsumasu('DictType')
    def _dict_(self):  # noqa
        self._token('{')

        def block1():
            self._entry_()
        self._closure(block1)
        self.name_last_node('@')
        self._token('}')

    @tatsumasu('ArrayType')
    def _array_(self):  # noqa
        self._token('(')

        def sep1():
            self._token(',')

        def block1():
            self._value_()
        self._gather(block1, sep1)
        self.name_last_node('@')
        with self._optional():
            self._token(',')
        self._token(')')

    @tatsumasu('BinType')
    def _hexdata_(self):  # noqa
        self._token('<')

        def block1():
            self._hexpairs_()
        self._closure(block1)
        self.name_last_node('@')
        self._token('>')

    @tatsumasu('BinType')
    def _base64data_(self):  # noqa
        self._token('<[')
        self._pattern('[^\\]]*')
        self.name_last_node('@')
        self._token(']>')

    @tatsumasu()
    def _typed_(self):  # noqa
        self._token('<*')
        self._typed_belly_()
        self.name_last_node('@')
        self._token('>')

    @tatsumasu()
    def _hexpairs_(self):  # noqa
        self._pattern('(?i)([0-9a-f]{2})+')

    @tatsumasu()
    def _safechar_(self):  # noqa
        self._pattern('[-#!$%&*+./0-9:?@A-Z^_a-z|~]+')

    @tatsumasu('StringType')
    def _string_(self):  # noqa
        with self._choice():
            with self._option():
                with self._group():
                    self._safechar_()
                    self.name_last_node('sc')
            with self._option():
                with self._group():
                    self._token('"')
                    self._cut()

                    def block3():
                        self._qchar_()
                    self._closure(block3)
                    self.name_last_node('ec')
                    self._token('"')
                    self._cut()

                    self._define(
                        ['ec'],
                        []
                    )
            self._error(
                'expecting one of: '
                '\'"\' <safechar>'
                '[-#!$%&*+./0-9:?@A-Z^_a-z|~]+'
            )

    @tatsumasu()
    def _qchar_(self):  # noqa
        with self._choice():
            with self._option():
                with self._group():
                    self._pattern('[^"\\\\]+')
                self.name_last_node('r')
            with self._option():
                with self._group():
                    self._pattern('\\\\')
                    self._esc_seq_()
                self.name_last_node('e')
            self._error(
                'expecting one of: '
                '[^"\\]+ \\'
            )

    @tatsumasu()
    def _esc_seq_(self):  # noqa
        with self._choice():
            with self._option():
                self._pattern('[abtrnvf]')
            with self._option():
                with self._group():
                    self._pattern('(?i)u')
                    self._pattern('(?i)[0-9a-f]{4}')
            with self._option():
                with self._group():
                    self._pattern('x')
                    self._pattern('(?i)[0-9a-f]{2}')
            with self._option():
                self._pattern('[0-7]{,3}')
            with self._option():
                self._pattern('.')
            self._error(
                'expecting one of: '
                '(?i)u . [0-7]{,3} [abtrnvf] x'
            )

    @tatsumasu()
    def _number_(self):  # noqa
        self._pattern('[0-9]+')

    @tatsumasu('int')
    def _int_(self):  # noqa
        with self._optional():
            self._token('-')
        self._number_()

    @tatsumasu()
    def _uid_(self):  # noqa
        self._number_()

    @tatsumasu('float')
    def _float_(self):  # noqa
        with self._optional():
            self._token('-')
        with self._group():
            with self._choice():
                with self._option():
                    self._pattern('(?i)nan')
                with self._option():
                    self._pattern('(?i)inf')
                with self._option():
                    with self._group():
                        with self._choice():
                            with self._option():
                                self._number_()
                                with self._optional():
                                    self._token('.')
                                    with self._optional():
                                        self._number_()
                            with self._option():
                                self._token('.')
                                self._number_()
                            self._error(
                                'expecting one of: '
                                "'.' <number>"
                            )
                    with self._optional():
                        self._token('e')
                        with self._optional():
                            self._token('[+-]')
                            self._number_()
                self._error(
                    'expecting one of: '
                    "'.' (?i)inf (?i)nan <number>"
                )

    @tatsumasu('DateType')
    def _date_(self):  # noqa
        self._pattern('[^>"]+')

    @tatsumasu()
    def _bool_(self):  # noqa
        self._pattern('[YN]')

    @tatsumasu()
    def _nil_(self):  # noqa
        self._pattern('[N]')

    @tatsumasu()
    def _typed_belly_(self):  # noqa
        with self._choice():
            with self._option():
                self._pattern('I')
                with self._optional():
                    self._pattern('"')
                self._int_()
                self.name_last_node('@')
                with self._optional():
                    self._pattern('"')
            with self._option():
                self._pattern('U')
                with self._optional():
                    self._pattern('"')
                self._uid_()
                self.name_last_node('@')
                with self._optional():
                    self._pattern('"')
            with self._option():
                self._pattern('R')
                with self._optional():
                    self._pattern('"')
                self._float_()
                self.name_last_node('@')
                with self._optional():
                    self._pattern('"')
            with self._option():
                self._pattern('B')
                with self._optional():
                    self._pattern('"')
                self._bool_()
                self.name_last_node('@')
                with self._optional():
                    self._pattern('"')
            with self._option():
                self._pattern('D')
                with self._optional():
                    self._pattern('"')
                self._date_()
                self.name_last_node('@')
                with self._optional():
                    self._pattern('"')
            with self._option():
                self._nil_()
                self.name_last_node('@')
            self._error(
                'expecting one of: '
                '<nil> B D I R U [N]'
            )


class PlistSemantics:
    def start(self, ast):  # noqa
        return ast

    def entry(self, ast):  # noqa
        return ast

    def value(self, ast):  # noqa
        return ast

    def dict(self, ast):  # noqa
        return ast

    def array(self, ast):  # noqa
        return ast

    def hexdata(self, ast):  # noqa
        return ast

    def base64data(self, ast):  # noqa
        return ast

    def typed(self, ast):  # noqa
        return ast

    def hexpairs(self, ast):  # noqa
        return ast

    def safechar(self, ast):  # noqa
        return ast

    def string(self, ast):  # noqa
        return ast

    def qchar(self, ast):  # noqa
        return ast

    def esc_seq(self, ast):  # noqa
        return ast

    def number(self, ast):  # noqa
        return ast

    def int(self, ast):  # noqa
        return ast

    def uid(self, ast):  # noqa
        return ast

    def float(self, ast):  # noqa
        return ast

    def date(self, ast):  # noqa
        return ast

    def bool(self, ast):  # noqa
        return ast

    def nil(self, ast):  # noqa
        return ast

    def typed_belly(self, ast):  # noqa
        return ast


def main(filename, **kwargs):
    if not filename or filename == '-':
        text = sys.stdin.read()
    else:
        with open(filename) as f:
            text = f.read()
    parser = PlistParser()
    return parser.parse(
        text,
        filename=filename,
        **kwargs
    )


if __name__ == '__main__':
    import json
    from tatsu.util import asjson

    ast = generic_main(main, PlistParser, name='Plist')
    data = asjson(ast)
    print(json.dumps(data, indent=2))
