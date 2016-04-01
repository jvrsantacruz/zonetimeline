# -*- coding: utf-8 -*-
import io
import datetime

import click


@click.command()
def cli():
    """zone time line"""
    utc = datetime.datetime.utcnow()
    local = datetime.datetime.now()
    ar = utc - datetime.timedelta(hours=3)  # UTC-3

    ctx = Context()

    ctx.add_header(local, utc, local=True)
    ctx.add_header(ar, utc)
    ctx.add_header(utc, utc)

    ctx.add_marker(u'↓↓')
    ctx.add_timeline(local, utc, local=True)
    ctx.add_timeline(ar, utc)
    ctx.add_timeline(utc, utc)
    ctx.add_marker(u'↑↑')
    ctx.render()


def render_header(d, utc, local=False):
    return (utc_name(d, utc, local=local) + u':').ljust(17, ' ')


def format_date(d, date_format=u'%Y-%m-%d %H:%M:%S'):
    return d.strftime(date_format)


def utc_name(d, utc, local=False):
    offset = utc_offset(d, utc)
    name = u'UTC'
    if offset:
        name += u'{:+02d}'.format(offset)
    if local:
        name += u' (local)'
    return name


def utc_offset(local, utc):
    return int(round((local - utc).total_seconds()) // 3600)


def render_date_timeline(d, utc, local=False):
    return render_times(render_header(d, utc, local=local), d)


def render_times(name, d):
    return render_line(
        header=lambda: name,
        tick=lambda h: u'{:02d} · '.format((d.hour + h) % 24))


def render_marker(marker):
    return render_line(
        header=lambda: u' ' * 17,
        tick=lambda h: u'{}   '.format(marker) if h == 0 else u'     ')


def render_line(header, tick):
    """click.echos a timeline line"""
    return header() + u''.join(tick(h) for h in range(-12, 12))


class Context(object):
    def __init__(self):
        self.buffer = io.StringIO()

    def add(self, text):
        self.buffer.write(text + u'\n')

    def add_marker(self, sign):
        self.add(render_marker(sign))

    def add_header(self, d, utc, local=False):
        header = render_header(d, utc, local=local)
        self.add(u'{} {}'.format(header, format_date(d)))

    def add_timeline(self, d, utc, local=False):
        self.add(render_date_timeline(d, utc, local=local))

    def render(self):
        click.echo(self.buffer.getvalue())


if __name__ == '__main__':
    cli()
