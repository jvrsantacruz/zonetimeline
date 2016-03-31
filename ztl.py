# -*- coding: utf-8 -*-
import datetime

import click


@click.command()
def cli():
    """zone time line"""
    utc = datetime.datetime.utcnow()
    local = datetime.datetime.now()

    local_header = render_header(local, utc, local=True)
    utc_header = render_header(local, utc)

    click.echo(u'{} {}'.format(utc_header, format_date(utc)))
    click.echo(u'{} {}'.format(local_header, format_date(local)))
    click.echo()

    render_marker(u'↓↓')
    render_date_timeline(local, utc, local=True)
    render_date_timeline(utc, utc)
    render_marker(u'↑↑')


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
    render_times(render_header(d, utc, local=local), d)


def render_times(name, d):
    render_line(
        header=lambda: name,
        tick=lambda h: u'{:02d}   '.format((d.hour + h) % 24))


def render_marker(marker):
    render_line(
        header=lambda: u' ' * 17,
        tick=lambda h: u'{}   '.format(marker) if h == 0 else u'     ')


def render_line(header, tick):
    """click.echos a timeline line"""
    click.echo(header(), nl=False)
    for h in range(-12, 12):
        click.echo(tick(h), nl=False)
    click.echo()


if __name__ == '__main__':
    cli()
