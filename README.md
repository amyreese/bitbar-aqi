# bitbar-aqi

[BitBar][] plugin for displaying current AQI from one or more nearby
[PurpleAir][] sensors.

# Setup

This plugin requires Python 3.7 or newer to be available on `$PATH` as `python3`.

1) Clone this repo, or download [aqi.5m.py][], and then copy [aqi.5m.py][] into
   your BitBar plugins directory.

2) Add your local sensor IDS to a `.purple-sensors.json` file next to
   your [aqi.5m.py][]:

```json
{"sensor_ids": [6014, 16943, 58743]}
```

   OR: Edit [aqi.5m.py][] to add local sensor IDs directly to `SENSOR_IDS`:

```python
SENSOR_IDS = [6014, 16943, 58743]
```

3) Refresh BitBar

4) Profit!

![Screenshot of bitbar-aqi results showing "AQI 41"](https://github.com/jreese/bitbar-aqi/blob/main/screenshot.png)

# License

bitbar-aqi is copyright John Reese, and licensed under the MIT license.
I am providing code in this repository to you under an open source license.
This is my personal repository; the license you receive to my code is from
me and not from my employer. See the LICENSE file for details.

[aqi.5m.py]: https://github.com/jreese/bitbar-aqi/blob/main/aqi.5m.py
[BitBar]: https://github.com/matryer/bitbar
[PurpleAir]: https://www.purpleair.com/map?opt=1/mAQI/a10/cC0#6.76/37.018/-121.629
