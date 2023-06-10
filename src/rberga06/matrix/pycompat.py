#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compatibility layer & stdlib definitions for pure Python mode."""
from types import NoneType
from typing import Any, Callable, ClassVar, Literal, TypeVar, overload
_T = TypeVar("_T")
_F = TypeVar("_F", bound=Callable[..., Any])
_C = TypeVar("_C", bound=type[Any])

# Basic types
cint    = int
cbool   = bool
cdouble = float
cvoid   = NoneType
cchar   = int
# Pointer types
p_cchar = bytes

# Fake Cython module
class cython:
    compiled: ClassVar[Literal[False]] = False

    @staticmethod
    def cast(t: type[_T], x: Any, /) -> _T:
        """`cast(t, x)` <=> `<t>(x)`"""
        return x  # type: ignore

    @staticmethod
    def nogil(f: _F, /) -> _F:
        """`nogil` in `cdef` or `cpdef` function defs"""
        return f

    @staticmethod
    def cfunc(f: _F, /) -> _F:
        """`cdef` function definition"""
        return f

    @staticmethod
    def ccall(f: _F, /) -> _F:
        """`cpdef` function definition"""
        return f

    @staticmethod
    def cclass(f: _C, /) -> _C:
        """`cdef class` definition"""
        return f

    @staticmethod
    def locals(**cdefs: type) -> Callable[[_F], _F]:
        """`cdef:` block for function local variables."""
        def inner(f: _F) -> _F:
            return f
        return inner

    @staticmethod
    def declare(t: type[_T], v: Any = None, /) -> _T:
        """`x = declare(t, v)` <=> `cdef t x = v`"""
        return cython.cast(t, v)

    @staticmethod
    @overload
    def address(x: cchar, /) -> p_cchar: ...
    @overload
    def address(x: _T, /) -> list[_T]: ...
    def address(x: cchar, /) -> p_cchar:
        """`address(x)` <=> `&x`"""
        if isinstance(x, cchar):
            return bytes([x])
        return [x]

# Standard library functions
