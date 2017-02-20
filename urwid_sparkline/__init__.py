#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
import urwid
from urwid_utils.palette import *
from collections import deque
import random
import math

BLOCK_VERTICAL = [ unichr(x) for x in range(0x2581, 0x2589) ]
BLOCK_HORIZONTAL = [ unichr(x) for x in range(0x258F, 0x2587, -1) ]

class SparkColumnWidget(urwid.Text):
    """
    A sparkline-ish column widget for Urwid.

    Given a list of numeric values, this widget will draw a small text-based
    vertical bar graph of the values, one character per value.  Column segments
    can be colorized according to a color scheme or by assigning each
    value a color.
    """

    chars = BLOCK_VERTICAL

    def __init__(self, values, color_scheme = [], *args, **kwargs):

        self.color_scheme = deque(color_scheme)

        self.values = [ v[1] if isinstance(v, tuple) else v for v in values ]

        try:
            self.colors = deque([ v[0] if isinstance(v, tuple)
                                  else self.color_scheme.rotate()
                                  or self.color_scheme[0] for v in values ])
        except IndexError:
            self.colors = None

        def colorize(v, advance=True):
            if isinstance(v, tuple):
                return v
            elif self.colors:
                if advance:
                    self.colors.rotate(-1)
                return (self.colors[0], v)
            else:
                return v

        total = sum(self.values)

        self.sparktext = [
            colorize(self.chars[int(round(v))])
            for i, v in enumerate(self.scale_values(
                    self.values, (0, len(self.chars) - 1))
            )
        ]
        super(SparkColumnWidget, self).__init__(self.sparktext, *args, **kwargs)


    @staticmethod
    def scale_values(l, dstrange=[0, 1]):
        v_min = min(l)
        v_max = max(l)

        scale = int(v_max - v_min) * 1000 / (dstrange[1] - dstrange[0])
        if not scale:
            return ( dstrange[1] for i in range(len(l)) )
        return ( dstrange[0] + ((( + v - v_min) * 1000)) / scale for v in l)



class SparkBarWidget(urwid.Text):
    """
    A sparkline-ish horizontal stacked bar widget for Urwid.


    """

    chars = BLOCK_HORIZONTAL

    def __init__(self, values, width, color_scheme = [],
                 *args, **kwargs):


        self.color_scheme = deque(color_scheme)

        self.values = [ v[1] if isinstance(v, tuple) else v for v in values ]

        self.width = width

        try:
            self.colors = deque([ v[0] if isinstance(v, tuple)
                                  else self.color_scheme.rotate()
                                  or self.color_scheme[0] for v in values ])
        except IndexError:
            self.colors = None

        def colorize(v, advance=True):
            if isinstance(v, tuple):
                return v
            elif self.colors:
                if advance:
                    self.colors.rotate(-1)
                return (self.colors[0], v)
            else:
                return v

        total = sum(self.values)

        scaled_values = [
            max((n/total*self.width), 1)
            for n in self.values
        ]

        self.sparktext = []

        charwidth = total / self.width
        nchars = len(self.chars)

        for i, v in enumerate(self.values):

            v_scaled = max((v/total*self.width), 1)
            chars = [ colorize(self.chars[-1]) ]
            chars[0:1] += [ colorize(self.chars[n], advance=False) for n in range(0, nchars-1)]

            charcount = int(v_scaled) if v_scaled.is_integer() else int(math.ceil(v_scaled))

            for n in range(0, charcount):
                if n >= charcount - 1  and (v % charwidth):
                    idx = int((v % charwidth)/charwidth * nchars)
                    c = chars[idx]
                    if i < len(self.values) - 1:
                        c = ("%s:%s" %(c[0], self.colors[i+1]), c[1])
                else:
                    c = chars[0]
                    c = ("%s:%s" %(c[0], c[0]), c[1])
                self.sparktext.append(c)

        super(SparkBarWidget, self).__init__(self.sparktext, *args, **kwargs)

