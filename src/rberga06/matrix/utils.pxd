# -*- coding: utf-8 -*-
"""Utilities (for Cython mode)."""

cdef bint happens(double p) noexcept nogil  # type: ignore

cdef char choice(const char* array, size_t len) noexcept nogil  # type: ignore
