# Cast Viewer - Digital Signage for the Raspberry Pi

@TODO: write resin.io docs

This code is mostly based on the source provided by the lovely people at Screenly. Please visit the official website at [Screenly.io](http://www.screenly.io). Original source can be found at https://github.com/wireload/screenly-ose

## Significant changes
- Removed all web interface code
- Removed the `image` asset
- Renamed `assets` to `slides`
- Added templates for setup etc.
- Added installation scripts
- Added heartbeat call to server

## Development
Enable debug mode when developing which outputs everything to stdout: `touch /boot/debug`. This will also enable dual-mode inthe chromium window to debug preloading.

### Template editing
Templates are generated with [Harp](http://harpjs.com/). This enables template inherence and static asset generation out of the box.
Recompile the templates by running `harp compile` in the project directory.

