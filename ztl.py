# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime

import click


@click.command()
def cli():
    """zone time line"""
    utc = datetime.datetime.utcnow()
    local = datetime.datetime.now()

    print('UTC time: {}'.format(utc))
    print('local time: {}'.format(local))
    print()

    print('UTC:        ', end='')
    for h in range(24):
        print('{:2d}   '.format((utc.hour + h) % 24), end='')
    print()
    print('local time: ', end='')
    for h in range(24):
        print('{:2d}   '.format((local.hour + h) % 24), end='')
    print()


    print()


if __name__ == '__main__':
    cli()
