#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# build.py: cythonize
"""Cython compile-time constants."""
# Everything Cython needs is defined in the .pxd
from typing import TYPE_CHECKING

try:
    assert not TYPE_CHECKING
    import cython as c
except ModuleNotFoundError:
    from . import cython as c


if not c.compiled:
    ###### ALPHABET ######
    ### Preliminary definitions: character sets
    _CHARS_BIN = b"01"
    _CHARS_OCT = b"01234567"
    _CHARS_DIGITS = b"0123456789"
    _CHARS_HEX = b"0123456789ABCDEF"
    _CHARS_LETTERS_L = b"abcdefghijklmnopqrstuvwxyz"  # lowercase
    _CHARS_LETTERS_U = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # uppercase
    _CHARS_LETTERS = _CHARS_LETTERS_L + _CHARS_LETTERS_U
    _CHARS_MISC = b"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"  # other characters
    _CHARS_SPACE = b" "
    _CHARS_ORDINARY = _CHARS_DIGITS + _CHARS_LETTERS
    _CHARS_PRINTABLE = _CHARS_ORDINARY + _CHARS_MISC
    _CHARS_ALL = _CHARS_PRINTABLE + _CHARS_SPACE
    ### The alphabet we have chosen
    ALPHABET: c.p_char = _CHARS_BIN
    # ALPHABET: c.p_char = _CHARS_OCT
    # ALPHABET: c.p_char = _CHARS_DIGITS
    # ALPHABET: c.p_char = _CHARS_HEX
    # ALPHABET: c.p_char = _CHARS_ORDINARY
    # ALPHABET: c.p_char = _CHARS_PRINTABLE
    # ALPHABET: c.p_char = _CHARS_ALL
    ### The length of the alphabet
    ALPHABET_LEN: c.int = len(ALPHABET)
    ###### COLORS ######
    COLORS: list[c.p_char] = [
        b"white bold",
        b"color(46) bold",
        *[b"color(46)"]*3,
        *[b"color(40)"]*5,
        *[b"color(34)"]*7,
        *[b"color(28)"]*9,
        *[b"color(22)"]*11,
        b"black",
    ]
    COLORS_LEN: c.int = len(COLORS)
