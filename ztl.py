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
    render_times(local_header, local)
    render_times(utc_header, utc)
    render_marker(u'↑↑')


def render_header(d, utc, local=True):
    return (utc_name(d, utc, local=local) + u':').ljust(17, ' ')


def format_date(d, date_format=u'%Y-%m-%d %H:%M:%S'):
    return d.strftime(date_format)


def utc_name(d, utc, local=False):
    offset = utc_offset(d, utc)
    name = u'UTC'
    if offset:
        name += u'+{}'.format(offset).ljust(3, ' ')
    if local:
        name += u' (local)'
    return name


def utc_offset(local, utc):
    return int(round((local - utc).total_seconds()) // 3600)


def render_times(name, now):
    render_timeline(
        header=lambda: name,
        tick=lambda h: u'{:2d}   '.format((now.hour + h) % 24))


def render_marker(marker):
    render_timeline(
        header=lambda: u'            ',
        tick=lambda h: u'{}   '.format(marker) if h == 0 else u'     ')


def render_timeline(header, tick):
    """click.echos a timeline line"""
    click.echo(header(), nl=False)
    for h in range(-12, 12):
        click.echo(tick(h), nl=False)
    click.echo()


if __name__ == '__main__':
    cli()
