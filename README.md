# zonetimeline

Compare several timezones in the command line

The `ztl` command will display a timeline for each timezone. They're stacked one onto so they can
be easily compared. The timeline is centered at the current time.

This tool can get handy when constantly comparing changing timezones, as it provides a quick way to
see which time correspond in different places, making meeting scheduling or thinking about events
in several locations a lot easier.

```
$ ztl

Europe/Madrid:           2016-03-31 12:38:41
America/Buenos_Aires:    2016-03-31 06:38:41
UTC:                     2016-03-31 10:38:41

                                                                             ↓↓
Europe/Madrid:         00   01   02   03   04   05   06   07   08   09   10   11   12   13   14   15   16   17   18   19   20   21   22   23
America/Buenos_Aires:  18   19   20   21   22   23   00   01   02   03   04   05   06   07   08   09   10   11   12   13   14   15   16   17
UTC:                   22   23   00   01   02   03   04   05   06   07   08   09   10   11   12   13   14   15   16   17   18   19   20   21
                                                                             ↑↑
```

2016-06-28 18:33:26
2016-06-28 13:33:26
2016-06-28 16:33:26
                                     ↓↓ 
06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 00 01 02 03 04 05 
01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 00 
04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 00 01 02 03 
                                                             ↑↑ 

## Usage

```
Usage: ztl [OPTIONS]

  zone time line

Options:
  -t, --time TIME       Change selected time in UTC: HH[:MM]
  -n, --nhours INTEGER  Number of hours to display  [default: 24]
  -z, --zone TEXT       Add extra timezone [repeat]
  -Z, --zones LIST      Comma separated list of timezones
  -c, --config PATH     Configuration file [default:
                        /home/javier/.config/zonetimeline/config]
  -w, --width INTEGER   Screen width  [default: 272]
  --help                Show this message and exit.
```

## Configuration

Configuration is read by default from `~/.config/zonetimeline/config` in Linux.
A file containing the basic config can be found at
`/usr/share/docs/zonetimeline/config.default.toml` and can be copied to the default place to start
modifying.

The example configuration can be seen below. Uncomment the desired fields to set the different
options. Present config settings matches the command line options.

```
[general]
# Number of hours to display in the timeline
# nhours = 24

# List of timezones for which create a timeline
# zones = ["Europe/Madrid", "America/Buenos_Aires", "UTC"]

# Extra timezones to add to the timezone list
# zone = []
```

## Timezones

Available timezones are the ones listed in the [IANA Time Zone
Database](https://www.iana.org/time-zones) (AKA *Olson tz database*).
