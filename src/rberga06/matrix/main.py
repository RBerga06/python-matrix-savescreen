#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# build.py: cythonize
from os import get_terminal_size
from typing import TYPE_CHECKING
from rich.columns import Columns
from rich.live import Live
from typer import Typer

try:
    assert not TYPE_CHECKING
    import cython as c
except ModuleNotFoundError:
    from . import cython as c


if c.compiled:
    assert not TYPE_CHECKING
    from cython.cimports.rberga06.matrix.constants import (
        ALPHABET, ALPHABET_LEN, COLORS, COLORS_LEN,
    )
    from cython.cimports.rberga06.matrix.utils import (
        happens, choice, char2ptr, p_p_char
    )
else:
    from .constants import (
        ALPHABET, ALPHABET_LEN, COLORS, COLORS_LEN
    )
    import random as _random
    p_p_char = list[c.p_char]
    def choice(array: c.p_char, len: c.int) -> c.char:
        return _random.choice(array)
    def happens(p: c.double) -> bool:
        return _random.random() <= p
    def char2ptr(c: c.char) -> c.p_char:
        return bytes([c])


WIDTH         = c.declare(c.int)
HEIGHT        = c.declare(c.int)
WIDTH, HEIGHT = get_terminal_size()
MAX_LEN_DROP  = c.declare(c.int, WIDTH + COLORS_LEN)
P_CHR_CHANGE  = c.declare(c.double, .10)
P_NEW_DROP    = c.declare(c.double, 1 / WIDTH)
COL_NUMBER    = c.declare(c.int, WIDTH // 2)
COL_LENGTH    = c.declare(c.int, HEIGHT)


app = Typer()


@c.cfunc
@c.nogil
@c.exceptval(check=False)
def randchar() -> c.char:
    """Generate a random character."""
    return choice(ALPHABET, ALPHABET_LEN)


@c.cfunc
@c.nogil
@c.exceptval(check=False)
def get_color(i: c.size_t) -> c.p_char:
    return c.cast(c.p_char, COLORS[min(i, COLORS_LEN - 1)])


@c.cclass
class Column:
    __slots__ = ("chars_len", "chars", "drops")
    chars_len: c.int
    chars: list[c.char]
    drops: list[c.int]

    if not c.compiled:
        def __new__(cls, length: c.int, /) -> "Column":
            obj = super().__new__(cls)
            obj.__cinit__(length)
            return obj

    def __cinit__(self, length: c.int, /) -> c.void:
        self.chars_len = length
        self.chars = [randchar() for _ in range(length)]
        self.drops = [-1]

    @c.cfunc
    @c.locals(
        drop=c.int,
        i=c.int,
    )
    def update(self, /) -> c.void:
        # Move all drops by 1 character. Also remove dead drops
        self.drops = drops = [
            drop + 1
            for drop in self.drops
            if drop < MAX_LEN_DROP
        ]
        # There is some probability of creating a new drop
        if happens(P_NEW_DROP):
            drops.insert(0, 0)
        # Every character might change; new drops' heads *must* change
        self.chars = [
            randchar()
            if (i in drops) or happens(P_CHR_CHANGE)
            else chr
            for i, chr in enumerate(self.chars)
        ]

    def __rich__(self, /) -> str:
        rich:  str = ""
        drops: list[c.int] = [*self.drops]
        color: str
        i:     c.int
        chr:   c.char
        bchr:  c.p_char
        delta: c.int
        for i in range(self.chars_len):
            chr = self.chars[i]
            if drops:
                delta = c.cast(c.int, drops[0]) - i
                if delta == 0:  # last character of the drop
                    drops.pop(0)  # pass to the next drop
            else:
                delta = -1
            color = get_color(delta).decode()
            bchr = char2ptr(chr)
            rich += f"[{color}]{bchr.decode()}[/{color}]\n"
        return rich[:-1]


@app.command()
def matrix():
    columns: list[Column] = [
        Column.__new__(Column, COL_LENGTH)
        for _ in range(COL_NUMBER)
    ]
    column: Column
    with Live(Columns(columns, width=1, align="left", expand=True), screen=True) as live:
        while True:
            try:
                for column in columns:
                    column.update()
                live.refresh()
            except KeyboardInterrupt:
                break
        live.stop()
    if c.compiled:
        print("Hello, Matrix! It's Cython!")
    else:
        print("Hello, Matrix! It's Python!")
