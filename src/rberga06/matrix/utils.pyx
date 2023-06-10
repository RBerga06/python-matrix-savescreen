# -*- coding: utf-8 -*-
"""Utilities (for Cython mode)."""
cimport cython
from libc.math cimport floor
from libc.stdlib cimport rand, RAND_MAX

@cython.cdivision(True)
cdef double random() noexcept nogil:  # type: ignore
    return <double>rand() / (<double>RAND_MAX)

cdef bint happens(double p) noexcept nogil:  # type: ignore
    return random() <= p

cdef size_t random_index(size_t len) noexcept nogil:  # type: ignore
    return <size_t>floor(random() * len)

cdef char choice(const char* array, size_t len) noexcept nogil:  # type: ignore
    return array[random_index(len)]
