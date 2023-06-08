#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cython: language=c++
from rich import get_console
from rich.columns import Columns
from rich.live import Live
from typer import Typer

try:
    import cython
except ModuleNotFoundError:
    from typing import TYPE_CHECKING
    assert not TYPE_CHECKING
    _dec = lambda _, x, **kw: x
    class _cython:
        compiled = False
        nogil = _dec
        cfunc = _dec
        ccall = _dec
        cclass = _dec
        locals = lambda _, *a, **kw: (lambda x, **kw: x)
    cython = _cython()


if cython.compiled:
    from typing import TYPE_CHECKING
    assert not TYPE_CHECKING
    from cython import address, cast, declare
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
        return cast(cdouble, rand()) / cast(cdouble, RAND_MAX)
    # floor()
    from cython.cimports.libc.math import floor
else:
    from random import random
    from typing import TYPE_CHECKING, Any, TypeVar, cast
    from types import NoneType
    _T = TypeVar("_T")
    # builtin types
    cint    = int
    cbool   = bool
    cdouble = float
    void    = NoneType
    cchar   = bytes
    p_cchar = bytes
    # vector
    class vector(list[_T]):
        """C++'s `std::vector<_T>` type"""
    # declare(...)
    def declare(t: type[_T], x: Any = None, /) -> _T:
        return x
    # address(...)
    def address(x: cchar) -> p_cchar:
        return x
    # For the static type checker
    if TYPE_CHECKING:
        def floor(_: float, /) -> float: ...
    else:
        from math import floor


### Alphabet: Bin ###
# ALPHABET_LEN = declare(cint, 2)
# ALPHABET     = declare(str, "01")
### Alphabet: Oct ###
# ALPHABET_LEN = declare(cint, 8)
# ALPHABET     = declare(str, "01234567")
### Alphabet: Dec ###
# ALPHABET_LEN = declare(cint, 10)
# ALPHABET     = declare(str, "0123456789")
### Alphabet: Hex ###
# ALPHABET_LEN = declare(cint, 16)
# ALPHABET     = declare(str, "0123456789ABCDEF")
### Alphabet: Eng ###
# ALPHABET_LEN = declare(cint, 62)
# ALPHABET     = declare(str,
#   "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
# )
### Alphabet: All ###
ALPHABET_LEN = declare(cint, 94)
ALPHABET     = declare(p_cchar,
    b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
)
### Colors ###
COLORS = declare(list[str], [
    "white bold",
    "color(46) bold",
    *["color(46)"]*3,
    *["color(40)"]*5,
    *["color(34)"]*7,
    *["color(28)"]*9,
    *["color(22)"]*11,
    "black"
])
COLORS_LEN    = declare(cint, 37)
WIDTH         = declare(cint)
HEIGHT        = declare(cint)
WIDTH, HEIGHT = get_console().size
MAX_LEN_DROP  = declare(cint, WIDTH + COLORS_LEN)
P_CHR_CHANGE  = declare(cdouble, .10)
P_NEW_DROP    = declare(cdouble, 1 / WIDTH)
COL_NUMBER    = declare(cint, WIDTH // 2)
COL_LENGTH    = declare(cint, HEIGHT)


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
def randchar() -> cchar:
    """Generate a random character."""
    return ALPHABET[rand_i(ALPHABET_LEN)]


@cython.cfunc
def get_color(i: cint) -> str:
    return COLORS[min(i, len(COLORS) - 1)]


@cython.cclass
class Column:
    __slots__ = ("chars", "drops")
    chars_len: cint
    chars: list[cchar]
    drops: list[cint]

    def __init__(self, length: cint, /) -> void:
        self.chars_len = length
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
                delta = cast(cint, drops[0]) - i
                if delta == 0:  # last character of the drop
                    drops.pop(0)  # pass to the next drop
            else:
                delta = -1
            color = get_color(delta)
            bchr = address(chr)
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
