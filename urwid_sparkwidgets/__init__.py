#!/usr/bin/python
# -*- coding: utf-8 -*-
#

"""
```urwid-sparkwidgets```
========================

A set of sparkline-ish widgets for urwid

This module contains a set of urwid text-like widgets for creating tiny but
hopefully useful sparkline-like visualizations of data.
"""


from __future__ import division
import urwid
from urwid_utils.palette import *
from collections import deque
import math
import operator
import itertools
import collections

BLOCK_VERTICAL = [ unichr(x) for x in range(0x2581, 0x2589) ]
BLOCK_HORIZONTAL = [ unichr(x) for x in range(0x258F, 0x2587, -1) ]

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


    def parse_scheme(self, scheme):

        if isinstance(scheme, dict):
            color_scheme = scheme
        else:
            try:
                color_scheme = COLOR_SCHEMES[scheme]
            except:
                raise Exception("Unknown color scheme: %s" %(scheme))

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

    :param items: A list of items to be charted in the widget.  Items can be
    either numeric values or tuples, the latter of which must be of the form
    ('attribute', value) where attribute is an urwid text attribute and value
    is a numeric value.

    :param color_scheme: A string or dictionary containing the name of or
    definition of a color scheme for the widget.

    :param underline: one of None, "negative", or "min", specifying values that
    should be marked in the chart.  "negative" shows negative values as little
    dots at the bottom of the chart, while "min" uses a unicode combining
    three dots character to indicate minimum values.  Results of this and the
    rest of these parameters may not look great with all terminals / fonts,
    so if this looks weird, don't use it.

    :param overline: one of None or "max" specfying values that should be marked
    in the chart.  "max" draws three dots above the max value.  See underline
    description for caveats.

    :param scale_min: Set a minimum scale for the chart.  By default, the range
    of the chart's Y axis will expand to show all values, but this parameter
    can be used to restrict or expand the Y-axis.

    :param scale_max: Set the maximum for the Y axis. -- see scale_min.
    """

    chars = BLOCK_VERTICAL

    def __init__(self, items,
                 color_scheme = "mono",
                 scale_min = None,
                 scale_max = None,
                 underline = None,
                 overline = None,
                 *args, **kwargs):

        self.items = items
        self.colors = self.parse_scheme(color_scheme)

        self.underline = underline
        self.overline = overline

        self.values = [ i[1] if isinstance(i, tuple) else i for i in self.items ]

        v_min = min(self.values)
        v_max = max(self.values)


        def normalize(v, a, b, scale_min=None, scale_max=None):

            if not scale_min:
                scale_min = v_min

            if not scale_max:
                scale_max = v_max

            return max(
                a,
                min(
                    b,
                    (((v - scale_min) / (scale_max - scale_min) ) * (b - a) + a)
                )
            )


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


                # idx = scale_value(value, scale_min=scale_min, scale_max=scale_max)
                idx = normalize(value, 0, len(self.chars)-1,
                                  scale_min=scale_min, scale_max=scale_max)

                glyph = self.chars[int(round(idx))]

                if self.underline == "min" and value == v_min:
                    glyph = u"%s\N{COMBINING TRIPLE UNDERDOT}" %(glyph)

                if self.overline == "max" and value == v_max:
                    glyph = u"%s\N{COMBINING THREE DOTS ABOVE}" %(glyph)

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

    This widget graphs a set of values in a horizontal bar style.

    :param items: A list of items to be charted in the widget.  Items can be
    either numeric values or tuples, the latter of which must be of the form
    ('attribute', value) where attribute is an urwid text attribute and value
    is a numeric value.

    :param width: Width of the widget in characters.

    :param color_scheme: A string or dictionary containing the name of or
    definition of a color scheme for the widget.
    """

    chars = BLOCK_HORIZONTAL

    def __init__(self, items, width,
                 color_scheme = "mono",
                 *args, **kwargs):

        self.items = items
        self.width = width

        values = None
        total = None

        filtered_items = [ i for i in self.items ]
        # ugly brute force method to eliminate values too small to display
        while True:
            values = [ i[1] if isinstance(i, tuple) else i
                       for i in filtered_items ]
            total = sum(values)
            charwidth = total / self.width
            try:
                i = itertools.ifilter(
                    lambda i: (i[1] if isinstance(i, tuple) else i) < charwidth,
                    filtered_items).next()
                filtered_items.remove(i)
            except StopIteration:
                break

        self.colors = self.parse_scheme(color_scheme)

        charwidth = total / self.width
        stepwidth = charwidth / len(self.chars)

        self.sparktext = []

        position = 0
        carryover = 0
        nchars = len(self.chars)
        lastcolor = None


        for i, item in enumerate(filtered_items):

            if isinstance(item, tuple):
                color = item[0]
                v = item[1]
            else:
                color = self.current_color
                self.next_color()
                v = item

            b = position + v + carryover
            if(carryover > 0):
                idx = int(carryover/charwidth * nchars)
                char = self.chars[idx]
                c = ("%s:%s" %(lastcolor, color), char)
                position += charwidth
                self.sparktext.append(c)

            rangewidth = b - position# + carryover
            rangechars = int(round(rangewidth/charwidth))

            for i in range(rangechars):
                position += charwidth
                char = self.chars[-1]
                c = ("%s:%s" %(color, color), char)
                self.sparktext.append(c)

            carryover = b - position
            lastcolor = color

        super(SparkBarWidget, self).__init__(self.sparktext, *args, **kwargs)

