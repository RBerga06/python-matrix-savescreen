#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fake `cython` module for pure Python mode."""
import builtins
import types
from typing import Any, Callable, Literal, TypeVar, overload
_T = TypeVar("_T")
_F = TypeVar("_F", bound=Callable[..., Any])
_C = TypeVar("_C", bound=type[Any])

# Basic types
int    = builtins.int
bint   = builtins.bool
double = builtins.float
void   = types.NoneType
char   = builtins.int
# Pointer types
p_char = builtins.bytes

compiled: Literal[False] = False

def cast(t: type[_T], x: Any, /) -> _T:
    """`cast(t, x)` <=> `<t>(x)`"""
    return x  # type: ignore

def nogil(f: _F, /) -> _F:
    """`nogil` in `cdef` or `cpdef` function defs"""
    return f

def cfunc(f: _F, /) -> _F:
    """`cdef` function definition"""
    return f

def ccall(f: _F, /) -> _F:
    """`cpdef` function definition"""
    return f

def cclass(f: _C, /) -> _C:
    """`cdef class` definition"""
    return f

def locals(**cdefs: type) -> Callable[[_F], _F]:
    """`cdef:` block for function local variables."""
    def inner(f: _F) -> _F:
        return f
    return inner

def declare(t: type[_T], v: Any = None, /) -> _T:
    """`x = declare(t, v)` <=> `cdef t x = v`"""
    return cast(t, v)

@overload
def address(x: char, /) -> p_char: ...
@overload
def address(x: _T, /) -> list[_T]: ...
def address(x: char, /) -> p_char:
    """`address(x)` <=> `&x`"""
    if isinstance(x, char):
        return bytes([x])
    return [x]
