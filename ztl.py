# -*- coding: utf-8 -*-
import io
import math
import datetime

import pytz
import click
import tzlocal


@click.command()
@click.option('-n', '--nhours', default=24, show_default=True)
def cli(nhours):
    """zone time line"""
    ctx = Context(Time(), nhours=nhours, marker_top=u'↓↓', marker_bottom=u'↑↑',
                  zones=['local', -3, 'UTC'])
    click.echo(Render(ctx).render())


class Time(object):
    def __init__(self):
        self.utc = pytz.utc.localize(datetime.datetime.utcnow())
        self.local = tzlocal.get_localzone().localize(datetime.datetime.now())

    def zone(self, name):
        d = self.time(name)
        label = self.label(d)
        return label, d

    def time(self, name):
        if name == 'local':
            return self.local
        elif name in pytz.all_timezones:
            return self.utc.astimezone(pytz.timezone(name))
        else:
            return self.utc + datetime.timedelta(hours=int(name))

    def label(self, d):
        label = str(d.tzinfo)

        if label == 'UTC' and d != self.utc:  # calculated upon UTC
            label += u'{:+02d}'.format(self.utc_offset(d))

        if d == self.local:
            label += u' (local)'

        return label

    def utc_offset(self, d):
        return int((d - self.utc).total_seconds() // 3600)


class Context(object):
    def __init__(self, time, zones, nhours, marker_top, marker_bottom):
        self.time = time
        self.zones = tuple(map(self.time.zone, zones))
        self.markers = [marker_top, marker_bottom]
        self.timeline_start = -1 * (nhours // 2)
        self.timeline_end = (nhours // 2)
        self.timeline_range = range(self.timeline_start, self.timeline_end)
        self.marker_progress_ratio = self.time.utc.hour / 60.


class Render(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.buffer = io.StringIO()
        self._header_sep = u':   '
        self._header_width = None
        self._tick_width = 3

    def render(self):
        if not self.buffer.tell():
            self.build()
        return self.buffer.getvalue()

    def build(self):
        self.compute_header_width()
        self.compute_tick_width(self._header_width)
        self.compute_marker_offset(self._tick_width)

        # headers
        for name, date in self.ctx.zones:
            self.add_header(name, date)

        # timelines
        self.render_marker(self.ctx.markers[0])
        for name, date in self.ctx.zones:
            self.add_timeline(name, date)
        self.render_marker(self.ctx.markers[1])

    def add(self, text):
        self.buffer.write(text + u'\n')

    def add_header(self, name, d):
        self.add(u'{}{}'.format(self.render_name(name), self.render_date(d)))

    def add_timeline(self, name, d):
        self.add(self.render_times(self.render_name(name), d))

    def compute_header_width(self):
        longest_header = max(len(name) for name, _ in self.ctx.zones)
        self._header_width = longest_header + len(self._header_sep)

    def compute_tick_width(self, header_width):
        width, height = click.get_terminal_size()
        width -= header_width  # available timeline space
        # compute max fixed width a tick can be given the available space
        spaces_per_tick = float(width) / len(self.ctx.timeline_range)
        self._tick_width = int(math.floor(spaces_per_tick))

    def compute_marker_offset(self, tick_width):
        offset = int(math.floor(self.ctx.marker_progress_ratio * tick_width))
        self._marker_offset = min(tick_width, offset)

    def render_name(self, name):
        return (name + self._header_sep).ljust(self._header_width, ' ')

    def render_date(self, d, date_format=u'%Y-%m-%d %H:%M:%S'):
        return d.strftime(date_format)

    def render_times(self, name, d):
        def render_tick(h):
            text = u'{:02d}'.format((d.hour + h) % 24)
            text = text.ljust(self._tick_width)
            if h == 0:
                text = click.style(text, bold=True)
            return text

        return self.render_line(header=lambda: name, tick=render_tick)

    def render_marker(self, sign):
        def render_tick(h):
            if h == 0:
                return click.style(' ' * self._marker_offset +
                                   sign.ljust(self._tick_width), bold=True)
            return u' ' * self._tick_width

        self.add(self.render_line(
            header=lambda: u' ' * self._header_width, tick=render_tick))

    def render_line(self, header, tick):
        """click.echos a timeline line"""
        return header() + u''.join(tick(h) for h in self.ctx.timeline_range)
