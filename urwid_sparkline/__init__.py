#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import urwid
from urwid.display_common import _CUBE_256_LOOKUP_16, _CUBE_STEPS_256_16
from urwid_utils.palette import *
from collections import deque
import random
import math
import operator
import itertools
import collections

BLOCK_VERTICAL = [ unichr(x) for x in range(0x2581, 0x2589) ]
BLOCK_HORIZONTAL = [ unichr(x) for x in range(0x258F, 0x2587, -1) ]

# DISTINCT_COLORS_16 = [
#             "white", "light red", "light blue", "light magenta",
#             "light green", "light cyan", "yellow", "dark gray",
#             "dark blue", "dark magenta", "dark green", "light gray",
#             "dark cyan", "brown", "dark red" ]

DISTINCT_COLORS_16 = urwid.display_common._BASIC_COLORS[1:]

DISTINCT_COLORS_256 = [
    '#f00', '#080', '#00f', '#d6f', '#0ad', '#f80', '#8f0', '#666',
    '#f88', '#808', '#0fd', '#66f', '#aa8', '#060', '#faf', '#860',
    '#60a', '#600', '#ff8', '#086', '#8a6', '#adf', '#88a', '#f60',
    '#068', '#a66', '#f0a', '#fda'
]

DISTINCT_COLORS_TRUE = [
    '#ff0000', '#008c00', '#0000ff', '#c34fff',
    '#01a5ca', '#ec9d00', '#76ff00', '#595354',
    '#ff7598', '#940073', '#00f3cc', '#4853ff',
    '#a6a19a', '#004301', '#edb7ff', '#8a6800',
    '#6100a3', '#5c0011', '#fff585', '#007b69',
    '#92b853', '#abd4ff', '#7e79a3', '#ff5401',
    '#0a577d', '#a8615c', '#e700b9', '#ffc3a6'
]

COLOR_SCHEMES = {
    "mono": {
        "mode": "mono"
    },
    "rotate_16": {
        "mode": "rotate",
        "colors": DISTINCT_COLORS_16
    },
    "rotate_256": {
        "mode": "rotate",
        "colors": DISTINCT_COLORS_256
    },
    "rotate_true": {
        "mode": "rotate",
        "colors": DISTINCT_COLORS_TRUE
    },
    "signed": {
        "mode": "rules",
        "colors": {
            "nonnegative": "default",
            "negative": "dark red"
        },
        "rules": [
            ( "<", 0, "negative" ),
            ( "else", "nonnegative" ),
        ]
    }
}

def get_palette_entries():

    NORMAL_FG_MONO = "white"
    NORMAL_FG_16 = "light gray"
    NORMAL_BG_16 = "black"
    NORMAL_FG_256 = "light gray"
    NORMAL_BG_256 = "black"

    palette_entries = {}

    for fcolor in (urwid.display_common._BASIC_COLORS
                   + DISTINCT_COLORS_256
                   + DISTINCT_COLORS_TRUE):

        palette_entries.update({
            fcolor: PaletteEntry(
                mono = NORMAL_FG_MONO,
                foreground = (fcolor
                              if fcolor in urwid.display_common._BASIC_COLORS
                              else NORMAL_FG_16),
                background = NORMAL_BG_16,
                foreground_high = fcolor,
                background_high = NORMAL_BG_256
            ),
        })

        for bcolor in (urwid.display_common._BASIC_COLORS
                       + DISTINCT_COLORS_256
                       + DISTINCT_COLORS_TRUE):

            palette_entries.update({
                "%s:%s" %(fcolor, bcolor): PaletteEntry(
                    mono = NORMAL_FG_MONO,
                    foreground = (fcolor
                                  if fcolor in urwid.display_common._BASIC_COLORS
                                  else NORMAL_FG_16),
                    background = (bcolor
                                  if bcolor in urwid.display_common._BASIC_COLORS
                                  else NORMAL_BG_16),
                    foreground_high = fcolor,
                    background_high = bcolor
                ),
            })

    return palette_entries

OPERATOR_MAP = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "=": operator.eq,
    "else": lambda a, b: True
}


class SparkWidget(urwid.Text):

    @staticmethod
    def make_rule_function(scheme):

        rules = scheme["rules"]
        def rule_function(value):
            return scheme["colors"].get(
                itertools.ifilter(
                    lambda rule: all(
                        OPERATOR_MAP[cond[0]](value, cond[1] if len(cond) > 1 else None)
                        for cond in [rule]
                    ), scheme["rules"]
                ).next()[-1]
            )
        return rule_function


    def parse_scheme(self, name):

        try:
            color_scheme = COLOR_SCHEMES[name]
        except:
            raise Exception("Unknown color scheme: %s" %(name))

        mode = color_scheme["mode"]
        if mode == "mono":
            return None

        elif mode == "rotate":
            return deque(color_scheme["colors"])

        elif mode == "rules":
            return self.make_rule_function(color_scheme)

        else:
            raise Exception("Unknown color scheme mode: %s" %(mode))

    @property
    def current_color(self):

        return self.colors[0]

    def next_color(self):
        self.colors.rotate(-1)
        return self.current_color

    def get_color(self, item):
        if not self.colors:
            color = None
        elif callable(self.colors):
            color = self.colors(item)
        elif isinstance(self.colors, collections.Iterable):
            color = self.current_color
            self.next_color()
            return color
        else:
            raise Exception(self.colors)

        return color


class SparkColumnWidget(SparkWidget):
    """
    A sparkline-ish column widget for Urwid.

    Given a list of numeric values, this widget will draw a small text-based
    vertical bar graph of the values, one character per value.  Column segments
    can be colorized according to a color scheme or by assigning each
    value a color.
    """

    chars = BLOCK_VERTICAL

    def __init__(self, items,
                 color_scheme = "mono",
                 underline = None,
                 overline = None,
                 midline = False,
                 *args, **kwargs):

        self.items = items
        self.colors = self.parse_scheme(color_scheme)

        self.underline = underline
        self.overline = overline
        self.midline = midline

        self.values = [ i[1] if isinstance(i, tuple) else i for i in self.items ]

        v_min = min(self.values)
        v_max = max(self.values)

        scale = int(v_max - v_min)  / (len(self.chars) - 1)

        def scale_value(v):

            if not scale:
                return len(self.chars) - 1
            return ((( v - v_min) )) / scale

        def item_to_glyph(item):

            color = None

            if isinstance(item, tuple):
                color = item[0]
                value = item[1]
            else:
                color = self.get_color(item)
                value = item

            if self.underline == "negative" and value < 0:
                glyph = u" \N{COMBINING DOT BELOW}"
            else:
                index = scale_value(value)
                glyph = self.chars[int(round(index))]

                if self.underline == "min" and value == v_min:
                    glyph = u"%s\N{COMBINING TRIPLE UNDERDOT}" %(glyph)

                if self.overline == "max" and value == v_max:
                    glyph = u"%s\N{COMBINING THREE DOTS ABOVE}" %(glyph)

                # if self.midline:
                #     glyph = u"%s\N{COMBINING LONG STROKE OVERLAY}" %(glyph)

            if color:
                return (color, glyph)
            else:
                return glyph

        self.sparktext = [
            item_to_glyph(i)
            for i in self.items
        ]
        super(SparkColumnWidget, self).__init__(self.sparktext, *args, **kwargs)



class SparkBarWidget(SparkWidget):
    """
    A sparkline-ish horizontal stacked bar widget for Urwid.
    """

    chars = BLOCK_HORIZONTAL

    def __init__(self, items, width,
                 color_scheme = "mono",
                 *args, **kwargs):

        self.items = items
        self.width = width
        self.colors = self.parse_scheme(color_scheme)

        self.values = [ i[1] if isinstance(i, tuple) else i for i in self.items ]

        total = sum(self.values)

        scaled_values = [
            max((n/total*self.width), 1)
            for n in self.values
        ]

        self.sparktext = []

        charwidth = total / self.width
        nchars = len(self.chars)

        for i, item in enumerate(self.items):

            if isinstance(item, tuple):
                color = item[0]
                v = item[1]
            else:
                color = self.current_color
                v = i

            nextidx = (i+1) % len(self.items)
            if isinstance(self.items[nextidx], tuple):
                nextcolor = self.items[nextidx][0]
            else:
                nextcolor = self.next_color()

            print v, total
            v_scaled = float(max((v/total*self.width), 1))

            # chars = [ ( self.get_color(v), self.chars[-1]) ]
            # chars[0:1] += [ (self.get_color(self.chars[n], advance=False),
            #                  self.chars[n]) for n in range(0, nchars-1)]

            charcount = int(v_scaled) if v_scaled.is_integer() else int(math.ceil(v_scaled))

            for n in range(0, charcount):

                if n >= charcount - 1  and (v % charwidth):
                    idx = int((v % charwidth)/charwidth * nchars)
                    char = self.chars[idx]
                    if i < len(self.values) - 1:
                        c = ("%s:%s" %(color, nextcolor), char)
                    print "partial"
                else:
                    char = self.chars[-1]
                    c = ("%s:%s" %(color, color), char)
                    print "full"
                self.sparktext.append(c)
        print
        super(SparkBarWidget, self).__init__(self.sparktext, *args, **kwargs)

