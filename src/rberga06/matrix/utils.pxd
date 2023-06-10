# -*- coding: utf-8 -*-
"""Utilities (for Cython mode)."""

ctypedef char** p_p_char

cdef bint happens(double p) noexcept nogil  # type: ignore

cdef char choice(const char *array, size_t len) noexcept nogil  # type: ignore

cdef char *char2ptr(const char c) noexcept nogil  # type: ignore
