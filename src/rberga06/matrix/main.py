#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# build.py: cythonize
from typing import TYPE_CHECKING
from rich import get_console
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
    from cython.cimports.rberga06.matrix.utils import happens, choice
else:
    import random as _random
    def choice(array: c.p_char, len: c.int):
        return _random.choice(array)
    def happens(p: c.double):
        return _random.random() <= p


### Alphabet: Bin ###
# ALPHABET_LEN = c.declare(c.size_t, 2)
# ALPHABET     = c.declare(c.p_char, "01")
### Alphabet: Oct ###
# ALPHABET_LEN = c.declare(c.size_t, 8)
# ALPHABET     = c.declare(c.p_char, "01234567")
### Alphabet: Dec ###
# ALPHABET_LEN = c.declare(c.size_t, 10)
# ALPHABET     = c.declare(c.p_char, "0123456789")
### Alphabet: Hex ###
# ALPHABET_LEN = c.declare(c.size_t, 16)
# ALPHABET     = c.declare(c.p_char, "0123456789ABCDEF")
### Alphabet: Eng ###
# ALPHABET_LEN = c.declare(c.size_t, 62)
# ALPHABET     = c.declare(c.p_char,
#   "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
# )
### Alphabet: All ###
ALPHABET_LEN = c.declare(c.size_t, 94)
ALPHABET     = c.declare(c.p_char,
    b"0123456789"
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    b"abcdefghijklmnopqrstuvwxyz"
    b"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
)
### Colors ###
COLORS = c.declare(list[str], [
    "white bold",
    "color(46) bold",
    *["color(46)"]*3,
    *["color(40)"]*5,
    *["color(34)"]*7,
    *["color(28)"]*9,
    *["color(22)"]*11,
    "black"
])
COLORS_LEN    = c.declare(c.int, 37)
WIDTH         = c.declare(c.int)
HEIGHT        = c.declare(c.int)
WIDTH, HEIGHT = get_console().size
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
def get_color(i: c.size_t) -> str:
    return COLORS[min(i, len(COLORS) - 1)]


@c.cclass
class Column:
    __slots__ = ("chars_len", "chars", "drops")
    chars_len: c.int
    chars: list[c.char]
    drops: list[c.int]

    def __init__(self, length: c.size_t, /) -> c.void:
        self.chars_len = length
        self.chars = [randchar() for _ in range(length)]
        self.drops = [-1]

    @c.ccall
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
        drops: list[int] = [*self.drops]
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
            color = get_color(delta)
            bchr = c.address(chr)
            rich += f"[{color}]{bchr.decode()}[/{color}]\n"
        return rich[:-1]


@app.command()
@c.locals(
    columns=list[Column],
    column=Column,
)
def matrix():
    columns = [Column(COL_LENGTH) for _ in range(COL_NUMBER)]
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
        print("Hello, Matrix! It's c!")
    else:
        print("Hello, Matrix! It's Python!")
