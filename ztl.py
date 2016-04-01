# -*- coding: utf-8 -*-
import io
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

    def add_markers(self, upper, lower):
        self.markers = [upper, lower]

    def add_zone(self, offset):
        self.zones.append(self.time.zone(offset))


class Render(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.buffer = io.StringIO()

    def render(self):
        if not self.buffer.tell():
            self.build()
        return self.buffer.getvalue()

    def build(self):
        for name, date in self.ctx.zones:
            self.add_header(name, date)
        self.render_marker(self.ctx.markers[0])
        for name, date in self.ctx.zones:
            self.add_timeline(name, date)
        self.render_marker(self.ctx.markers[1])

    def add(self, text):
        self.buffer.write(text + u'\n')

    def add_header(self, name, d):
        self.add(u'{} {}'.format(self.render_name(name), self.render_date(d)))

    def add_timeline(self, name, d):
        self.add(self.render_times(self.render_name(name), d))

    def render_name(self, name):
        return (name + u':').ljust(17, ' ')

    def render_date(self, d, date_format=u'%Y-%m-%d %H:%M:%S'):
        return d.strftime(date_format)

    def render_times(self, name, d):
        return self.render_line(
            header=lambda: name,
            tick=lambda h: u'{:02d} · '.format((d.hour + h) % 24))

    def render_marker(self, sign):
        self.add(self.render_line(
            header=lambda: u' ' * 17,
            tick=lambda h: u'{}   '.format(sign) if h == 0 else u'     '
        ))

    def render_line(self, header, tick):
        """click.echos a timeline line"""
        return header() + u''.join(tick(h) for h in range(-12, 12))


if __name__ == '__main__':
    cli()
