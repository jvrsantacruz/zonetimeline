# -*- coding: utf-8 -*-
import io
import os
import re
import math
import datetime
import itertools
import collections

import pytz
import click
import pytoml
import tzlocal


DEFAULT_CONFIG = os.path.join(click.get_app_dir('zonetimeline'), 'config')


class List(click.ParamType):
    """Comma separated list"""
    name = 'list'

    def convert(self, value, param, ctx):
        if not value:
            return tuple()

        try:
            return tuple(value.split(','))
        except ValueError:
            self.fail(u'%s is not a comma separated list' % value, param, ctx)


class TimeParam(click.ParamType):
    """Time in command line"""
    name = 'time'

    def convert(self, value, param, ctx):
        if value and not re.match(r'\d{1,2}(:\d\d)?', value):
            self.fail(u'%s is not valid time HH[:MM]' % value, param, ctx)
        return value


@click.group(invoke_without_command=True)
@click.option('-t', '--time', type=TimeParam(),
              help=u"Set current time HH[:MM]")
@click.option('-n', '--nhours', default=24, show_default=True,
              help=u"Number of hours to display")
@click.option('-z', '--zone', multiple=True,
              help=u"Add extra timezone [repeat]")
@click.option('-Z', '--zones', type=List(), default=tuple(),
              help=u"Comma separated list of timezones")
@click.option('-c', '--config', type=click.Path(dir_okay=False, exists=True),
              help=u"Configuration file [default: %s]" % DEFAULT_CONFIG)
@click.option('-w', '--width', default=click.get_terminal_size()[0],
              show_default=True, help=u"Screen width")
def cli(config, **options):
    """zone time line"""
    update_no_override(options, parse_config(config or DEFAULT_CONFIG))
    options.update(marker_top=u'↓↓', marker_bottom=u'↑↑')
    ctx = Context(Times(), **options)
    ctx.validate()
    click.echo(Render(ctx).render(), nl=False)


@cli.command('list')
def list_timezones():
    """list all available timezones"""
    click.echo('IANA Time Zone Database {}'.format(pytz.OLSON_VERSION))
    click.echo('\n'.join(pytz.all_timezones))


def update_no_override(d, defaults):
    d.update((k, v) for k, v in defaults.items()
             if d.get(k) in (None, tuple()))


def parse_config(path):
    if path is None or not os.path.exists(path):
        return {}

    try:
        with io.open(path, 'r', encoding='utf-8') as stream:
            return pytoml.load(stream)['general']
    except IOError as error:
        raise click.ClickException(error)


Zone = collections.namedtuple('Zone', ['label', 'date', 'name'])


class Times(object):
    def __init__(self):
        self.utc = pytz.utc.localize(datetime.datetime.utcnow())
        self.local = self.utc.astimezone(tzlocal.get_localzone())
        self.offset_parser = Matcher(r'^(UTC|GMT)?([+-]\d+)')

    def zone(self, name):
        d = self.time(name)
        label = self.label(name, d)
        return Zone(label, d, name)

    def time(self, name):
        return self.utc.astimezone(self.parse_timezone(name))

    def parse_timezone(self, name):
        if name == 'local':
            return tzlocal.get_localzone()
        elif name in ('UTC', 'GMT'):
            return pytz.UTC
        elif self.offset_parser(name):
            ref, offset = self.offset_parser.match.groups()
            ref = (ref or 'GMT').replace('UTC', 'GMT')
            offset = int(self._reverse_offset_sign(offset or 0))
            return pytz.timezone('Etc/{}{:+d}'.format(ref, offset))
        elif name in pytz.all_timezones:
            return pytz.timezone(name)

        raise click.BadArgumentUsage(u'Unknown timezone: "{}"'.format(name))

    def label(self, name, d):
        label = str(d.tzinfo)

        # Fix offset based dates
        if label.startswith('Etc/GMT') and not name.startswith('Etc/'):
            # Remove pytz specific part
            label = label.replace('Etc/', '')
            # Revert POSIX name to the expected one
            label = self._reverse_offset_sign(label.replace('Etc/', ''))
            # Use UTC instead of GMT when user used UTC or not given
            if not name.startswith('GMT'):
                label = label.replace('GMT', 'UTC')

        # mark local time
        if d.isoformat() == self.local.isoformat():
            label += u' (local)'

        return label

    def _reverse_offset_sign(self, name):
        """Pytz POSIX behaviour have the sign reversed for compatibility"""
        return name.replace('-', '|').replace('+', '-').replace('|', '+')


class Context(object):
    def __init__(self, times, time, zone, zones, nhours, marker_top, marker_bottom,
                 width):
        self.time = time
        self.times = times
        self.zones = tuple(map(self.times.zone, itertools.chain(zones, zone)))
        self.markers = [marker_top, marker_bottom]
        self.timeline_start = -1 * (nhours // 2)
        self.timeline_end = (nhours // 2)
        self.timeline_range = range(self.timeline_start, self.timeline_end)
        self.marker_progress_ratio = self.times.utc.minute / 60.
        self.screen_width = width

    def validate(self):
        if not self.zones:
            raise click.BadOptionUsage(
                'No timezones given. Use the options --zone or --zones')


class Render(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.buffer = io.StringIO()
        self._header_sep = u':   '
        self._header_width = None
        self._tick_width = 3

    def render(self):
        if not self.buffer.tell():
            self.build()
        return self.buffer.getvalue()

    def build(self):
        self.compute_header_width()
        self.compute_tick_width(self._header_width)
        self.compute_marker_offset(self._tick_width)

        # headers
        for zone in self.ctx.zones:
            self.add_header(zone.label, zone.date)

        # timelines
        self.render_marker(self.ctx.markers[0])
        for zone in self.ctx.zones:
            self.add_timeline(zone.label, zone.date)
        self.render_marker(self.ctx.markers[1])

    def add(self, text):
        self.buffer.write(text + u'\n')

    def add_header(self, name, d):
        self.add(u'{}{}'.format(self.render_name(name), self.render_date(d)))

    def add_timeline(self, name, d):
        self.add(self.render_times(self.render_name(name), d))

    def compute_header_width(self):
        longest_header = max(len(zone.label) for zone in self.ctx.zones)
        self._header_width = longest_header + len(self._header_sep)

    def compute_tick_width(self, header_width):
        width = self.ctx.screen_width - header_width  # timeline space
        # compute max fixed width a tick can be given the available space
        spaces_per_tick = float(width) / len(self.ctx.timeline_range)
        self._tick_width = int(math.floor(spaces_per_tick))

    def compute_marker_offset(self, tick_width):
        offset = int(math.floor(self.ctx.marker_progress_ratio * tick_width))
        self._marker_offset = min(tick_width, offset)

    def render_name(self, name):
        return (name + self._header_sep).ljust(self._header_width, ' ')

    def render_date(self, d, date_format=u'%Y-%m-%d %H:%M:%S'):
        return d.strftime(date_format)

    def render_times(self, name, d):
        def render_tick(h):
            text = u'{:02d}'.format((d.hour + h) % 24)
            text = text.ljust(self._tick_width)
            if h == 0:
                text = click.style(text, bold=True)
            return text

        return self.render_line(header=lambda: name, tick=render_tick)

    def render_marker(self, sign):
        def render_tick(h):
            if h == 0:
                return click.style(' ' * self._marker_offset +
                                   sign.ljust(self._tick_width), bold=True)
            elif h < 0:
                return u' ' * self._tick_width
            else:
                return u''

        self.add(self.render_line(
            header=lambda: u' ' * self._header_width, tick=render_tick))

    def render_line(self, header, tick):
        """click.echos a timeline line"""
        return header() + u''.join(tick(h) for h in self.ctx.timeline_range)


class Matcher(object):
    def __init__(self, source):
        self.regex = re.compile(source)
        self.match = None

    def __call__(self, string):
        self.match = self.regex.match(string)
        return self.match
