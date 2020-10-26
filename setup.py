#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open
import os
import sys

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""


def with_default(f, exception, default):
    def realfun(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except exception:
            return default

    return realfun


new_mtime = with_default(os.path.getmtime, FileNotFoundError, float("+inf"))
old_mtime = with_default(os.path.getmtime, FileNotFoundError, float("-inf"))


def make_rule(source, target):
    def realdec(f):
        def realfun(*args, **kwargs):
            sourcetime = max(map(new_mtime, source))
            targettime = min(map(old_mtime, target))
            if sourcetime > targettime:
                return f(*args, **kwargs)

        return realfun

    return realdec


PARSER = "text_plistlib/pparser.py"
GRAMMAR = "text_plistlib/openstep.ebnf"


@make_rule([GRAMMAR], [PARSER])
def build_parser():
    import tatsu

    grammar = open("text_plistlib/openstep.ebnf").read()
    with open(PARSER, "w") as f:
        f.write(tatsu.to_python_sourcecode(grammar, filename=PARSER))


build_parser()

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "tatsu":
    exit(0)

setup(
    name="text_plistlib",
    version="0.1.0",
    description="Parser and dumper for ASCII plists from GNUStep and OpenStep",
    license="MIT",
    author="Mingye Wang",
    packages=find_packages(),
    install_requires=["tatsu"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
