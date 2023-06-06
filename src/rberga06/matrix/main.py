#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
import random
import string
from rich import get_console
from typer import Typer
from rich.columns import Columns
from rich.live import Live
import cython

print(f"{cython.compiled=}")

ALPHABET = dict[str, str](
    Bin="01",
    Oct="01234567",
    Dec="0123456789",
    Hex="0123456789ABCDEF",
    Eng=string.ascii_letters,
    Ascii=string.printable,
)["Bin"]
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
WIDTH, HEIGHT = get_console().size
MAX_LEN_DROP = WIDTH + len(COLORS)
P_CHR_CHANGE = .10
P_NEW_DROP   = 1/WIDTH
SPEED        = 1e5/(WIDTH*HEIGHT)
COL_NUMBER   = WIDTH // 2
COL_LENGTH   = HEIGHT

app = Typer()


# @cython.ccall
def happens(p: float) -> bool:
    """Return `True` with probability `p`."""
    return random.random() <= p


def get_color(i: int) -> str:
    return COLORS[min(i, len(COLORS) - 1)]


@dataclass(init=False, repr=True, slots=True, eq=False)
class Column:
    chars: list[str]
    drops: list[int]

    def __init__(self, length: int, /) -> None:
        self.chars = [random.choice(ALPHABET) for _ in range(length)]
        self.drops = [-1]

    def update(self, /) -> None:
        self.drops = [
            drop for drop in [
                # There is some probability of creating a new drop
                *([0] if random.random() <= P_NEW_DROP else []),
                # Move all drops by 1 character. Also remove died drops
                *[drop + 1 for drop in self.drops if drop < MAX_LEN_DROP],
            ]
        ]
        # Every character might change; new drops' heads *must* change
        self.chars = [
            random.choice(ALPHABET)
            if (i in self.drops) or random.random() <= P_CHR_CHANGE
            else chr
            for i, chr in enumerate(self.chars)
        ]

    def __rich__(self, /) -> str:
        rich = ""
        drops = self.drops.copy()
        for i, chr in enumerate(self.chars):
            delta = (drops or [i - 1])[0] - i
            if delta == 0:  # last character of the drop
                drops.pop(0)  # pass to the next drop
            rich += f"[{(color := get_color(delta))}]{chr}[/{color}]\n"
        return rich[:-1]


@app.command()
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
