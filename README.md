urwid-sparkwidgets
==================

A set of sparkline-ish widgets for urwid.

This module contains a set of urwid text-like widgets for creating tiny but
hopefully useful sparkline-like visualizations of data using unicode block
elements.

Currently consists of two widgets:

* ```SparkColumnWidget``` is a column chart.  Segments can be explicitly
givenurwid display attributes, or can be assigned colors and other attributes
according to a rotating color scheme or based on rules (e.g. negative values in
red).  By default the Y-axis scales to fit all values, but minimum and maximum
values for the Y-axis scale can also be provided -- this might not seem useful
given the extremely limited resolution of these tiny charts (only eight possible
block elements) but makes sense if you want to use mulitple sparklines with the
same scale to show differences in values between them.

* ```SparkBarWidget``` is a stacked horizontal bar chart.  It will fill a text
widget of a given width with colored segments for each input value.  It supports
the same color scheme functionality as the column widget.

TODOs:
* Allow for user-defined character schemes for the bar widget.  Unicode block
elements are most useful for increasing the resolution of the chart over typical
ASCII block art, but it'd be nice to be able to do something like
```******@@@@@@@@#####%%%%" for compatibility with non-color displays.
* Support log scale.
* Labels in bar chart?
