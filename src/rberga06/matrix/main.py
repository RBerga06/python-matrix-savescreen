#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cython: language=c++
import cython
from rich import get_console
from rich.columns import Columns
from rich.live import Live
from typer import Typer


if cython.compiled:
    from cython import cast
    # builtin types
    cint    = cython.typedef(cython.int)
    cbool   = cython.typedef(cython.bint)
    cdouble = cython.typedef(cython.double)
    void    = cython.typedef(cython.void)
    from cython.cimports.libcpp.vector import vector
    # random()
    from cython.cimports.libc.stdlib import rand, RAND_MAX
    @cython.nogil
    @cython.cfunc
    def random() -> cdouble:
        return rand() / RAND_MAX
    # floor()
    from cython.cimports.libc.math import floor
else:
    from random import random
    from typing import TYPE_CHECKING, TypeVar, cast
    from types import NoneType
    # builtin types
    cint    = int
    cbool   = bool
    cdouble = float
    void    = NoneType
    # vector
    _T = TypeVar("_T")
    class vector(list[_T]):
        pass
    # For the static type checker
    if TYPE_CHECKING:
        def floor(_: float, /) -> float: ...
    else:
        from math import floor


ALPHABET: str = "01"  # bin
# ALPHABET: str = "01234567"  # oct
# ALPHABET: str = "0123456789"  # dec
# ALPHABET: str = "0123456789ABCDEF"  # hex
# ALPHABET: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"  # eng
# ALPHABET: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"  # all
ALPHABET_LEN: cint = len(ALPHABET)
COLORS: list[str] = [
    "white bold",
    "color(46) bold",
    *["color(46)"]*3,
    *["color(40)"]*5,
    *["color(34)"]*7,
    *["color(28)"]*9,
    *["color(22)"]*11,
    "black"
]
COLORS_LEN:    cint = len(COLORS)
WIDTH:         cint
HEIGHT:        cint
WIDTH, HEIGHT = get_console().size
MAX_LEN_DROP:  cint = WIDTH + COLORS_LEN
P_CHR_CHANGE:  cdouble = .10
P_NEW_DROP:    cdouble = 1 / WIDTH
COL_NUMBER:    cint = WIDTH // 2
COL_LENGTH:    cint = HEIGHT

app = Typer()


@cython.nogil
@cython.cfunc
def rand_i(n: cint) -> cint:
    return cast(cint, floor(random() * n))


@cython.nogil
@cython.cfunc
def happens(p: cdouble) -> cbool:
    """Return `True` with probability `p`."""
    return random() <= p


@cython.cfunc
def randchar() -> str:
    """Generate a random character."""
    return ALPHABET[rand_i(ALPHABET_LEN)]


@cython.cfunc
def get_color(i: cint) -> str:
    return COLORS[min(i, len(COLORS) - 1)]


@cython.cclass
class Column:
    __slots__ = ("chars", "drops")
    chars: list[str]
    drops: list[cint]

    def __init__(self, length: cint, /) -> void:
        self.chars = [randchar() for _ in range(length)]
        self.drops = [-1]

    @cython.ccall
    @cython.locals(
        drop=cint,
        i=cint,
    )
    def update(self, /) -> void:
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

    @cython.locals(
        rich=str,
        drops=list[int],
        i=cint,
        chr=str,
        delta=cint,
        color=str,
    )
    def __rich__(self, /) -> str:
        rich = ""
        drops = [*self.drops]
        for i, chr in enumerate(self.chars):
            if drops:
                delta = drops[0] - i
                if delta == 0:  # last character of the drop
                    drops.pop(0)  # pass to the next drop
            else:
                delta = -1
            color = get_color(delta)
            rich += f"[{color}]{chr}[/{color}]\n"
        return rich[:-1]


@app.command()
@cython.locals(
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
