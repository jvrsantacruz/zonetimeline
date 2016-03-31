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

    local_header = render_header(local, utc, local=True)
    ar_header = render_header(ar, utc)
    utc_header = render_header(utc, utc)

    ctx = Context()
    ctx.add(u'{} {}'.format(local_header, format_date(local)))
    ctx.add(u'{} {}'.format(ar_header, format_date(ar)))
    ctx.add(u'{} {}'.format(utc_header, format_date(utc)))
    ctx.add('')

    ctx.add(render_marker(u'↓↓'))
    ctx.add(render_date_timeline(local, utc, local=True))
    ctx.add(render_date_timeline(ar, utc))
    ctx.add(render_date_timeline(utc, utc))
    ctx.add(render_marker(u'↑↑'))
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

    def render(self):
        click.echo(self.buffer.getvalue())


if __name__ == '__main__':
    cli()
