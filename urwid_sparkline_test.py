#!/usr/bin/python
from __future__ import division
import urwid
from urwid_utils.palette import *
from collections import deque
import random

from urwid_sparkline import *

screen = urwid.raw_display.Screen()
screen.set_terminal_properties(1<<24)
# screen.set_terminal_properties(256)

NORMAL_FG_MONO = "white"
NORMAL_FG_16 = "light gray"
NORMAL_BG_16 = "black"
NORMAL_FG_256 = "light gray"
NORMAL_BG_256 = "g0"

DISTINCT_COLORS = [
    [0, 0, 0],
    [255, 0, 0],
    [0, 140, 0],
    [0, 0, 255],
    [195, 79, 255],
    [1, 165, 202],
    [236, 157, 0],
    [118, 255, 0],
    [89, 83, 84],
    [255, 117, 152],
    [148, 0, 115],
    [0, 243, 204],
    [72, 83, 255],
    [166, 161, 154],
    [0, 67, 1],
    [237, 183, 255],
    [138, 104, 0],
    [97, 0, 163],
    [92, 0, 17],
    [255, 245, 133],
    [0, 123, 105],
    [146, 184, 83],
    [171, 212, 255],
    [126, 121, 163],
    [255, 84, 1],
    [10, 87, 125],
    [168, 97, 92],
    [231, 0, 185],
    [255, 195, 166]
]

DISTINCT_COLORS_HEX = [ "#%1x%1x%1x" %tuple(i>>4 for i in c) for c in DISTINCT_COLORS[1:] ]

DISTINCT_COLORS_RGB = ["dark red", "dark blue", "dark green"]

# DISTINCT_COLORS_HEX = [ "#%02x%02x%02x" %tuple(i for i in c) for c in DISTINCT_COLORS[1:] ]
palette_entries = {}

for fcolor in (urwid.display_common._BASIC_COLORS
               + [ urwid.display_common._color_desc_256(x)
                   for x in range(16,255) ]
               + DISTINCT_COLORS_HEX):

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
                   + [ urwid.display_common._color_desc_256(x)
                       for x in range(16,255) ]
                   + DISTINCT_COLORS_HEX):
        palette_entries.update({
            "%s:%s" %(fcolor, bcolor): PaletteEntry(
                mono = NORMAL_FG_MONO,
                foreground = NORMAL_FG_16,
                background = NORMAL_BG_16,
                foreground_high = fcolor,
                background_high = bcolor
            ),
        })


random_colors = [
    "#%02x%02x%02x" %(random.randint(20, 255),
                      random.randint(20, 255),
                      random.randint(20, 255))
    for i in range(20)
]

palette = Palette("default", **palette_entries)

spark1 = urwid.Filler(SparkColumnWidget(range(0, 8)))
spark2 = urwid.Filler(SparkColumnWidget(range(0, 100), color_scheme=DISTINCT_COLORS_HEX))
spark3 = urwid.Filler(SparkColumnWidget([30,1,44,2,11,99,-3,56], color_scheme=DISTINCT_COLORS_HEX))
spark4 = urwid.Filler(
    SparkColumnWidget([
        (random_colors[i],
         random.randint(-100, 1000)
        )
        for i in range(20)
    ])
)

bark1 = urwid.Filler(SparkBarWidget([40, 30, 20, 10], 20, color_scheme=DISTINCT_COLORS_HEX))
bark2 = urwid.Filler(SparkBarWidget([3, 2, 1], 28, color_scheme=DISTINCT_COLORS_HEX))
bark3 = urwid.Filler(SparkBarWidget([55, 15, 35, 12, 19, 10, 10, 10], 19, color_scheme=DISTINCT_COLORS_RGB))

pile = urwid.Pile([
    (2, spark1),
    (2, spark2),
    (2, spark3),
    (2, spark4),
    (2, bark1),
    (2, bark2),
    (2, bark3),
])

main = urwid.MainLoop(
    pile,
    palette = palette,
    screen = screen
)

main.run()
