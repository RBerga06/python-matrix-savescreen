#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cython: language=c++
from typing import TYPE_CHECKING
from rich import get_console
from rich.columns import Columns
from rich.live import Live
from typer import Typer

try:
    assert not TYPE_CHECKING
    import cython as cy
except ModuleNotFoundError:
    from .pycompat import cython as cy


if cy.compiled:
    assert not TYPE_CHECKING
    # builtin types
    cint    = cython.typedef(cython.int)
    cbool   = cython.typedef(cython.bint)
    cdouble = cython.typedef(cython.double)
    void    = cython.typedef(cython.void)
    cchar   = cython.typedef(cython.char)
    p_cchar = cython.typedef(cython.p_char)
    from cython.cimports.libcpp.vector import vector
    # random()
    from cython.cimports.libc.stdlib import rand, RAND_MAX
    @cython.cfunc
    @cython.nogil
    @cython.cdivision(True)
    def random() -> cdouble:
        return cy.cast(cdouble, rand()) / cy.cast(cdouble, RAND_MAX)
    # floor()
    from cython.cimports.libc.math import floor
else:
    from random import random
    from .pycompat import *
    # For the static type checker
    if TYPE_CHECKING:
        def floor(_: float, /) -> float: ...
    else:
        from math import floor


### Alphabet: Bin ###
# ALPHABET_LEN = cy.declare(cint, 2)
# ALPHABET     = cy.declare(str, "01")
### Alphabet: Oct ###
# ALPHABET_LEN = cy.declare(cint, 8)
# ALPHABET     = cy.declare(str, "01234567")
### Alphabet: Dec ###
# ALPHABET_LEN = cy.declare(cint, 10)
# ALPHABET     = cy.declare(str, "0123456789")
### Alphabet: Hex ###
# ALPHABET_LEN = cy.declare(cint, 16)
# ALPHABET     = cy.declare(str, "0123456789ABCDEF")
### Alphabet: Eng ###
# ALPHABET_LEN = cy.declare(cint, 62)
# ALPHABET     = cy.declare(str,
#   "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
# )
### Alphabet: All ###
ALPHABET_LEN = cy.declare(cint, 94)
ALPHABET     = cy.declare(p_cchar,
    b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
)
### Colors ###
COLORS = cy.declare(list[str], [
    "white bold",
    "color(46) bold",
    *["color(46)"]*3,
    *["color(40)"]*5,
    *["color(34)"]*7,
    *["color(28)"]*9,
    *["color(22)"]*11,
    "black"
])
COLORS_LEN    = cy.declare(cint, 37)
WIDTH         = cy.declare(cint)
HEIGHT        = cy.declare(cint)
WIDTH, HEIGHT = get_console().size
MAX_LEN_DROP  = cy.declare(cint, WIDTH + COLORS_LEN)
P_CHR_CHANGE  = cy.declare(cdouble, .10)
P_NEW_DROP    = cy.declare(cdouble, 1 / WIDTH)
COL_NUMBER    = cy.declare(cint, WIDTH // 2)
COL_LENGTH    = cy.declare(cint, HEIGHT)


app = Typer()


@cython.nogil
@cython.cfunc
def rand_i(n: cint) -> cint:
    return cy.cast(cint, floor(random() * n))


@cython.nogil
@cython.cfunc
def happens(p: cdouble) -> cbool:
    """Return `True` with probability `p`."""
    return random() <= p


@cython.cfunc
def randchar() -> cchar:
    """Generate a random character."""
    return ALPHABET[rand_i(ALPHABET_LEN)]


@cython.cfunc
def get_color(i: cint) -> str:
    return COLORS[min(i, len(COLORS) - 1)]


@cython.cclass
class Column:
    __slots__ = ("chars_len", "chars", "drops")
    chars_len: cint
    chars: list[cchar]
    drops: list[cint]

    def __init__(self, length: cint, /) -> cvoid:
        self.chars_len = length
        self.chars = [randchar() for _ in range(length)]
        self.drops = [-1]

    @cython.ccall
    @cython.locals(
        drop=cint,
        i=cint,
    )
    def update(self, /) -> cvoid:
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
        i:     cint
        chr:   cchar
        bchr:  p_cchar
        delta: cint
        for i in range(self.chars_len):
            chr = self.chars[i]
            if drops:
                delta = cy.cast(cint, drops[0]) - i
                if delta == 0:  # last character of the drop
                    drops.pop(0)  # pass to the next drop
            else:
                delta = -1
            color = get_color(delta)
            bchr = cy.address(chr)
            rich += f"[{color}]{bchr.decode()}[/{color}]\n"
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
    if cython.compiled:
        print("Hello, Matrix! It's Cython!")
    else:
        print("Hello, Matrix! It's Python!")
