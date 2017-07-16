# Cast Viewer - Digital Signage for the Raspberry Pi

The tl;dr for installing Cast Viewer on [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) [Jessie Lite](https://downloads.raspberrypi.org/raspbian_lite_latest) is:

```
$ wget https://raw.githubusercontent.com/enflow-nl/cast-viewer/master/bin/install.sh
$ sudo bash install.sh
```

(The installation will take 15-25 minutes or so depending on your connectivity and the speed of your SD card.)

This code is mostly based on the source provided by the lovely people at Screenly. Please visit the official website at [Screenly.io](http://www.screenly.io). Original source can be found at https://github.com/wireload/screenly-ose

## Significant changes
- Removed all web interface code
- Removed the `image` asset
- Renamed `assets` to `slides`
- Added templates for setup etc.
- Added installation scripts
- Added heartbeat call to server

## Development
Enable debug mode when developing which outputs everything to stdout: `touch /boot/debug` and enabled dual-mode in the chromium window to debug preloading.

### Template editing
Templates are generated with [Harp](http://harpjs.com/). This enables template inherence and static asset generation out of the box.
Recompile the templates by running `harp compile` in the project directory.

