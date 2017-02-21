#!/usr/bin/python
from __future__ import division
import urwid
from urwid_utils.palette import *
import random
from itertools import chain, izip, repeat, islice
from urwid_sparkline import *


screen = urwid.raw_display.Screen()
screen.set_terminal_properties(1<<24)

entries = get_palette_entries()

all_colors = [ urwid.display_common._color_desc_256(x)
                   for x in range(32,255) ]
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


def intersperse(delimiter, seq):
    return islice(chain.from_iterable(izip(repeat(delimiter), seq)), 1, None)


# raise Exception(entries)
palette = Palette("default", **entries)

spark1 = urwid.Filler(SparkColumnWidget(range(0, 8)))
spark2 = urwid.Filler(SparkColumnWidget(range(0, 100), color_scheme="rotate_16"))
spark3 = urwid.Filler(SparkColumnWidget(range(0, 100), color_scheme="rotate_true"))
spark4 = urwid.Filler(SparkColumnWidget(range(-5, 100), color_scheme="signed", underline="negative"))
spark_random_text = urwid.Filler(urwid.Text(""))
spark_random_ph = urwid.WidgetPlaceholder(urwid.Text(""))

bark1 = urwid.Filler(SparkBarWidget([30, 30, 30], 41, color_scheme="rotate_16"))
bark2 = urwid.Filler(SparkBarWidget([40, 30, 20, 10], 20, color_scheme="rotate_true"))
bark3 = urwid.Filler(SparkBarWidget([3, 2, 1], 28, color_scheme="rotate_true"))
bark4 = urwid.Filler(SparkBarWidget([19, 42, 17], 9, color_scheme="rotate_true"))
bark_random_text = urwid.Filler(urwid.Text(""))
bark_random_ph = urwid.WidgetPlaceholder(urwid.Text(""))


def get_random_spark():
    return SparkColumnWidget([
        (random_colors[i%len(random_colors)],
         random.randint(1, 100)
        )
        for i in range(32)
    ], underline="min", overline="max")

def get_random_bark():
    return SparkBarWidget([
        (random_colors[i%len(random_colors)],
         random.randint(1, 30)
        )
        for i in range(1, random.randint(4, 30))
    ], 80)


pile = urwid.Pile([
    (2, spark1),
    (2, spark2),
    (2, spark3),
    (2, spark4),
    (2, spark_random_text),
    (2, spark_random_ph),
    (2, bark1),
    (2, bark2),
    (2, bark3),
    (2, bark4),
    (2, bark_random_text),
    (2, bark_random_ph),
])

def randomize_spark():
    spark = get_random_spark()
    filler = urwid.Filler(spark)
    values = list(intersperse(",", [(i[0], "%s" %(i[1])) for i in spark.items]))
    spark_random_text.original_widget.set_text(values)
    spark_random_ph.original_widget = filler

def randomize_bark():
    bark = get_random_bark()
    filler = urwid.Filler(bark)
    values = list(intersperse(",", [(i[0], "%s" %(i[1])) for i in bark.items]))
    bark_random_text.original_widget.set_text(values)
    bark_random_ph.original_widget = filler

randomize_bark()
randomize_spark()

def keypress(key):

    if key == "b":
        randomize_bark()
    elif key == "s":
        randomize_spark()
    elif key == " ":
        randomize_bark()
        randomize_spark()
    else:
        return key


main = urwid.MainLoop(
    pile,
    palette = palette,
    screen = screen,
    unhandled_input = keypress
)

main.run()
