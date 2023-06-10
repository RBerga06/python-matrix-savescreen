# -*- coding: utf-8 -*-
"""Compile-time constants."""

cdef extern from *:
    """
    /****** ALPHABET ******/
    /* Preliminary definitions: character sets */
    #define CHARS_BIN "01"
    #define CHARS_OCT "01234567"
    #define CHARS_DIGITS "0123456789"
    #define CHARS_HEX "0123456789ABCDEF"
    #define CHARS_LETTERS_L "abcdefghijklmnopqrstuvwxyz"  // lowercase
    #define CHARS_LETTERS_U "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  // uppercase
    #define CHARS_LETTERS CHARS_LETTERS_L+CHARS_LETTERS_U
    #define CHARS_MISC "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"  // other characters
    #define CHARS_SPACE " "
    #define CHARS_ORDINARY CHARS_DIGITS+CHARS_LETTERS
    #define CHARS_PRINTABLE CHARS_ORDINARY+CHARS_MISC
    #define CHARS_ALL CHARS_PRINTABLE+CHARS_SPACE
    /* The alphabet we've chosen */
    #define ALPHABET CHARS_BIN
    // #define ALPHABET CHARS_OCT
    // #define ALPHABET CHARS_DIGITS
    // #define ALPHABET CHARS_HEX
    // #define ALPHABET CHARS_ORDINARY
    // #define ALPHABET CHARS_PRINTABLE
    // #define ALPHABET CHARS_ALL
    /* The length of the alphabet
     *   digits=10, letters=26, misc=32, space=1
     */
    #define ALPHABET_LEN 2
    // #define ALPHABET_LEN 8
    // #define ALPHABET_LEN 10
    // #define ALPHABET_LEN 16
    // #define ALPHABET_LEN 10+26+26
    // #define ALPHABET_LEN 10+26+26+32
    // #define ALPHABET_LEN 10+26+26+32+1

    /****** COLORS ******/
    #define COLORS_LEN 37
    const char *COLORS[COLORS_LEN] = {
        //
        "white bold",
        "color(46) bold",
        //
        "color(46)",
        "color(46)",
        "color(46)",
        //
        "color(40)",
        "color(40)",
        "color(40)",
        "color(40)",
        "color(40)",
        //
        "color(34)",
        "color(34)",
        "color(34)",
        "color(34)",
        "color(34)",
        "color(34)",
        "color(34)",
        //
        "color(28)",
        "color(28)",
        "color(28)",
        "color(28)",
        "color(28)",
        "color(28)",
        "color(28)",
        "color(28)",
        "color(28)",
        //
        "color(22)",
        "color(22)",
        "color(22)",
        "color(22)",
        "color(22)",
        "color(22)",
        "color(22)",
        "color(22)",
        "color(22)",
        "color(22)",
        "color(22)",
        //
        "black",
    }
    */
    """
    const int ALPHABET_LEN
    const char *ALPHABET
    const int COLORS_LEN
    const char COLORS[]
