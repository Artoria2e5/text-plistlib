#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Semantic actions for assembling the Plist AST into its Python form.
"""
from binascii import a2b_base64
from datetime import datetime
from plistlib import UID

one_char_esc = {
    "a": "\a",
    "b": "\b",
    "t": "\t",
    "r": "\r",
    "n": "\n",
    "v": "\v",
    "f": "\f",
}


def _unsur(s: str) -> str:
    """Merge surrogates."""
    return s.encode("utf-16", "surrogatepass").decode("utf-16", "surrogatepass")


class PlistSemantics(object):
    def __init__(self, dict_type=dict, cfuid=True):
        self._dict_type = dict_type
        self.cfuid = cfuid

    def start(self, ast, _=None):
        if ast.s is not None:
            return self.dict(ast.s)
        elif ast.v is not None:
            return ast.v

    def dict(self, ast, _=None):
        retval = self._dict_type()
        for entry in ast:
            retval[entry.k] = entry.v
        if self.cfuid and len(retval) == 1 and isinstance(retval.get("CF$UID"), int):
            return UID(retval["CF$UID"])
        return retval

    def array(self, ast, _=None):
        retval = list()
        for e in ast:
            retval.append(e)
        return retval

    def hexdata(self, ast, _=None):
        data = bytes.fromhex("".join(ast))
        return data

    def base64data(self, ast, _=None):
        data = a2b_base64(ast)
        return data

    def string(self, ast, _=None):
        if ast.sc:
            return ast.sc
        else:
            return _unsur("".join(ast.ec))

    def qchar(self, ast):
        if ast.r is not None:
            return ast.r
        elif ast.e is not None:
            body = ast.e[1]
            if isinstance(body, str):
                global one_char_esc
                if body in one_char_esc:
                    return one_char_esc[body]
                if body[0] in "01234567":
                    return chr(int(body, 8))
                else:
                    return body
            else:
                # assert body[0] in 'xUU'
                return chr(int(body[1], 16))

    def date(self, ast, _=None):
        return datetime.strptime(ast, "%Y-%m-%d %H:%M:%S %z")

    def uid(self, ast, _=None):
        return UID(ast)

    def int(self, ast, _=None):
        return int(ast)

    def float(self, ast, _=None):
        return float(ast)

    def bool(self, ast, _=None):
        return ast == "Y"

    def nil(self, ast, _=None):
        return None

    def _default(self, ast, _=None):
        return ast
