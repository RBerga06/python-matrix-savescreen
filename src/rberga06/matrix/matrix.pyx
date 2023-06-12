# -*- coding: utf-8 -*-
# cython: cdivision=True
cimport cython
from libc.stdlib cimport rand, RAND_MAX
from libc.math cimport floor
from libcpp.string cimport string
from rberga06.matrix.constants cimport (
    ALPHABET, ALPHABET_LEN,
    COLORS, COLORS_LEN,
)
import os
import numpy as np

cdef int WIDTH = 10
cdef int HEIGHT = 50
WIDTH, HEIGHT = os.get_terminal_size()
cdef double P_NEW_DROP = <double>.1
cdef double P_NEW_CHAR = (<double>1) / (<double>WIDTH*2)


cdef double random() noexcept nogil:  # type: ignore
    return <double>rand() / (<double>RAND_MAX)

cdef bint happens(double p) noexcept nogil:  # type: ignore
    return random() <= p

cdef int random_index(int len) noexcept nogil:  # type: ignore
    return <int>floor(random() * len)

cdef char choice(const char *array, int len) noexcept nogil:  # type: ignore
    return array[random_index(len)]

cdef char randchar() noexcept nogil:  # type: ignore
    return choice(ALPHABET, ALPHABET_LEN)

cdef char *get_color(int i) noexcept nogil:  # type: ignore
    return <char *>COLORS[min(i, COLORS_LEN - 1)]


cdef class Matrix:
    cdef readonly int width
    cdef readonly int height
    cdef char[:, :] chars
    cdef int[:, :] colors

    cdef void init(self, int width, int height, char[:, :] chars, int[:, :] colors) noexcept nogil:  # type: ignore
        self.width = width
        self.height = height
        self.chars = chars
        self.colors = colors

    @cython.boundscheck(False)
    cdef void update(self) noexcept nogil:  # type: ignore
        cdef int i
        cdef int j
        cdef bint drop_head
        cdef char chr
        cdef int color
        for i in range(self.height-1, -1, -1):
            for j in range(self.width):
                chr = self.chars[i][j]
                color = self.colors[i][j]  # type: ignore
                # Check if here we should have a drop head
                if i == 0:
                    drop_head = happens(P_NEW_DROP)
                else:
                    # Since i - 1 < i, self.colors[i - 1][j] has not yet been visited
                    drop_head = (self.colors[i - 1][j] == 0)  # type: ignore
                # Update color & chr
                if drop_head:
                    color = 0
                    chr = randchar()
                else:
                    color += 1
                    if happens(P_NEW_CHAR):
                        chr = randchar()
                # Set new color & chr
                self.chars[i][j] = chr
                self.colors[i][j] = color  # type: ignore

    @cython.boundscheck(False)
    cdef string rich(self) noexcept nogil:  # type: ignore
        cdef char *color
        cdef char chr
        cdef string row
        cdef string rich = string(<char *>b"")
        for i in range(self.height):
            row = string(<char *>b"")
            for j in range(self.width):
                color = get_color(self.colors[i][j])  # type: ignore
                chr   = self.chars[i][j]
                row += <char *>b"["
                row += color
                row += <char *>b"]"
                row += chr
                row += <char *>b"[/"
                row += color
                row += <char *>b"] "
            row.pop_back()  # Remove last ' ' character
            rich += row
            rich += <char>b'\n'
        rich.pop_back()  # Remove last '\n' character
        return rich

    def __rich__(self) -> str:
        return self.rich().decode()


cpdef int main():
    from time import sleep
    from rich.live import Live
    cdef Matrix m = Matrix.__new__(Matrix)
    m_chars = np.full((HEIGHT, WIDTH), b'0', dtype=np.dtype("c"))
    m_colors = np.array([
        [0]*WIDTH,
        *[[COLORS_LEN - 1]*WIDTH]*(HEIGHT-1)
    ], dtype=np.dtype("i"))
    m.init(WIDTH, HEIGHT, m_chars, m_colors)  # type: ignore
    # m_chars = np.zeros((3, 4), dtype=np.dtype("c"))
    # m_colors = np.array([
    #     [3, 3, 3],
    #     [2, 2, 2],
    #     [1, 1, 1],
    #     [0, 0, 0],
    # ], dtype=np.dtype("c"))
    # m = Matrix(m_chars, m_colors)
    with Live(m.rich().decode(), screen=True, auto_refresh=False) as live:
        while True:
            m.update()
            live.refresh()
            sleep(1)
    return 0
