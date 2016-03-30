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

    render_timeline(
        header=lambda: u'            ',
        tick=lambda h: u'↓↓   ' if h == 0 else u'     ')

    render_timeline(
        header=lambda: u'UTC:        ',
        tick=lambda h: u'{:2d}   '.format((utc.hour + h) % 24))

    render_timeline(
        header=lambda: u'local time: ',
        tick=lambda h: u'{:2d}   '.format((local.hour + h) % 24))

    render_timeline(
        header=lambda: u'            ',
        tick=lambda h: u'↑↑   ' if h == 0 else u'     ')


def render_timeline(header, tick):
    """click.echos a timeline line"""
    click.echo(header(), nl=False)
    for h in range(-12, 12):
        click.echo(tick(h), nl=False)
    click.echo()


if __name__ == '__main__':
    cli()
