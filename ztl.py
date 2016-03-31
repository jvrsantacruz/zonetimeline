# -*- coding: utf-8 -*-
import datetime

import click


@click.command()
def cli():
    """zone time line"""
    utc = datetime.datetime.utcnow()
    local = datetime.datetime.now()

    click.echo(u'UTC time:   {}'.format(utc))
    click.echo(u'local time: {}'.format(local))
    click.echo()

    render_marker(u'↓↓')
    render_times(utc_name(local, utc) + u'  ', local)
    render_times(u'UTC:             ', utc)
    render_marker(u'↑↑')


def utc_name(local, utc):
    offset = utc_offset(local, utc)
    name = u'UTC'
    if offset:
        name += u'+{}'.format(offset).ljust(3, ' ')
    name += u' (local):'
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
