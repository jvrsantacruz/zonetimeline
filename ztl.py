# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime

import click


@click.command()
def cli():
    """zone time line"""
    utc = datetime.datetime.utcnow()
    local = datetime.datetime.now()

    print(u'UTC time:   {}'.format(utc))
    print(u'local time: {}'.format(local))
    print()

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
    """Prints a timeline line"""
    print(header(), end='')
    for h in range(-12, 12):
        print(tick(h), end='')
    print()


if __name__ == '__main__':
    cli()
