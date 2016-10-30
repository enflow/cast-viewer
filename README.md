# Cast Viewer - Digital Signage for the Raspberry Pi

The tl;dr for installing Cast Viewer on [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) Jessie is:

```
$ bash <(curl -sL https://raw.githubusercontent.com/enflow-nl/cast-viewer/master/bin/install.sh)
```

(The installation will take 15-20 minutes or so depending on your connectivity and the speed of your SD card.)

This code is mostly based on the source provided by the lovely people at Screenly. Please visit the official website at [Screenly.io](http://www.screenly.io). Original source can be found at https://github.com/wireload/screenly-ose

## Significant changes
- Removed all web based code
- Removed the `image` asset
- Renamed `assets` to `slides`
- Added templates for setup etc.
