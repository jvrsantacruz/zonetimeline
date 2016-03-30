# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime

import click


@click.command()
def cli():
    """zone time line"""
    utc = datetime.datetime.utcnow()
    local = datetime.datetime.now()

    print(u'UTC time: {}'.format(utc))
    print(u'local time: {}'.format(local))
    print()

    print(u'            ', end='')
    for h in range(24):
        if h == 0:
            print(u'↓↓   ', end='')
        else:
            print(u'     ', end='')
    print()

    print(u'UTC:        ', end='')
    for h in range(24):
        print(u'{:2d}   '.format((utc.hour + h) % 24), end='')
    print()

    print(u'local time: ', end='')
    for h in range(24):
        print(u'{:2d}   '.format((local.hour + h) % 24), end='')
    print()

    print(u'            ', end='')
    for h in range(24):
        if h == 0:
            print(u'↑↑   ', end='')
        else:
            print(u'     ', end='')
    print()

    print()


if __name__ == '__main__':
    cli()
