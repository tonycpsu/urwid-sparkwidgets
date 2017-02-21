#!/usr/bin/python
from __future__ import division
import urwid
from urwid_utils.palette import *
import random

from urwid_sparkline import *

screen = urwid.raw_display.Screen()
screen.set_terminal_properties(1<<24)
# screen.set_terminal_properties(256)

entries = get_palette_entries()

all_colors = [ urwid.display_common._color_desc_256(x)
                   for x in range(16,255) ]
random_colors = [ random.choice(all_colors) for i in range(16) ]

for fcolor in random_colors:

    entries.update({
        fcolor: PaletteEntry(
            mono = "white",
            foreground = (fcolor
                          if fcolor in urwid.display_common._BASIC_COLORS
                          else "white"),
            background = "black",
            foreground_high = fcolor,
            background_high = "black"
        ),
    })

    for bcolor in random_colors:

        entries.update({
            "%s:%s" %(fcolor, bcolor): PaletteEntry(
                mono = "white",
                foreground = (fcolor
                              if fcolor in urwid.display_common._BASIC_COLORS
                              else "white"),
                background = (bcolor
                              if bcolor in urwid.display_common._BASIC_COLORS
                              else "black"),
                foreground_high = fcolor,
                background_high = bcolor
            ),
        })


# raise Exception(entries)
palette = Palette("default", **entries)

spark1 = urwid.Filler(SparkColumnWidget(range(0, 8)))
spark2 = urwid.Filler(SparkColumnWidget(range(0, 100), color_scheme="rotate_16", ))
spark3 = urwid.Filler(SparkColumnWidget(range(0, 100), color_scheme="rotate_256"))
spark4 = urwid.Filler(SparkColumnWidget(range(0, 100), color_scheme="rotate_true"))
spark5 = urwid.Filler(SparkColumnWidget(range(-5, 100), color_scheme="signed", underline="negative"))
spark6 = urwid.Filler(SparkColumnWidget([
        (random_colors[i%len(random_colors)],
         random.randint(1, 100)
        )
        for i in range(64)
    ], underline="min", overline="max"))

# bark1 = urwid.Filler(SparkBarWidget([40, 30, 20, 10], 20, color_scheme=DISTINCT_COLORS_HEX))
# bark2 = urwid.Filler(SparkBarWidget([3, 2, 1], 28, color_scheme=DISTINCT_COLORS_HEX))
# bark3 = urwid.Filler(SparkBarWidget([55, 15, 35, 12, 19, 10, 10, 10], 19, color_scheme=DISTINCT_COLORS_RGB))

pile = urwid.Pile([
    (2, spark1),
    (2, spark2),
    (2, spark3),
    (2, spark4),
    (2, spark5),
    (2, spark6),
    # (2, bark1),
    # (2, bark2),
    # (2, bark3),
])

main = urwid.MainLoop(
    pile,
    palette = palette,
    screen = screen
)

main.run()
