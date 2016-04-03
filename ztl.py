# -*- coding: utf-8 -*-
import io
import math
import datetime

import click


@click.command()
def cli():
    """zone time line"""
    ctx = Context(Time())
    ctx.add_markers(u'↓↓', u'↑↑')
    ctx.add_zone('local')
    ctx.add_zone(-3)
    ctx.add_zone('utc')

    click.echo(Render(ctx).render())


class Time(object):
    def __init__(self):
        self.utc = datetime.datetime.utcnow()
        self.local = datetime.datetime.now()

    def zone(self, offset):
        d = self.time(offset)
        name = self.name(d)
        return name, d

    def time(self, offset):
        if offset == 'local':
            return self.local
        elif offset == 0 or offset == 'utc':
            return self.utc
        else:
            return self.utc + datetime.timedelta(hours=offset)

    def name(self, d):
        offset = self.utc_offset(d, self.utc)
        name = u'UTC'
        if offset:
            name += u'{:+02d}'.format(offset)
        if d == self.local:
            name += u' (local)'
        return name

    def utc_offset(self, d, utc):
        return int(round((d - utc).total_seconds()) // 3600)


class Context(object):
    def __init__(self, time):
        self.time = time
        self.zones = []
        self.markers = []
        self.timeline_start = -12
        self.timeline_end = 12
        self.timeline_range = range(self.timeline_start, self.timeline_end)
        self.marker_progress_ratio = self.time.utc.hour / 60.

    def add_markers(self, upper, lower):
        self.markers = [upper, lower]

    def add_zone(self, offset):
        self.zones.append(self.time.zone(offset))


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
        self._marker_offset = min(self._tick_width, offset)

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
