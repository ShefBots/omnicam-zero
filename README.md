# omnicam-zero
The Pi-Zero side of the sensor system for the omnicam communication platform.

This repository contains a the actual programs to run on-hardware as well as some other tools for debugging and configuration.

## Folder Structure

### Root
Where all the main executables are stored

### detectors
Where all the individual classes exist that handle image processing to detect task-specific semantic elements

### camera-configuration
When programs relating to image caputre, image configuration or else are run, images are generally stored here.
Also stored here are generated camera configuration files created by the camera setup wizard.

## Executable Scripts
### sensorServer.py
The actual server. When run with `-r` it is expected to be running on the real-world hardware at 192.168.22.1.
It is a websocket server with a simple set of one-character commands for switching modes.
Depending on it's mode, it'll transmit to all connected clients data suitable to that mode.
For instance, in "time" mode (command "T") it'll transmit the time every 1-3 seconds.
In "random" mode (command "R") it'll transmit a random number every 1-3 seconds.

Non-test modes are available for each PiWars task that requires camera data, such as the "minesweeper" mode (command "M") that'll transmit the mine's relative position after each camera frame acquisition and processing.

```
usage: sensorServer.py [-h] [-m MODE] [-r] [-p]

Launches a socket server that transmits task-specific sensor data data.

options:
  -h, --help            show this help message and exit
  -m MODE, --mode MODE  The mode to start the server in. Specified using the string types
                        of the protocol Mode class (i.e. T, R, M or S)
  -r, --remote          Use this flag to host a server at 192.168.22.1 (on the Pi Zero).
                        If not, it is hosted on localhost and placeholder data will be used
                        instead of camera data.
  -p, --explain-mode-protocols
                        Prints out descriptions of the data that each transmission mode produces.
```
Actual challenge-specific data acquiring routines are found in the "detectors" folder.

### debug-client.py, debug-client-threads.py
A simple debuging client to observe and interact with the socket connection. It is recommended that two instances of this are opened if actively being used for debugging: one with `-t` and one without. Again, `-r` connects to 192.168.22.1, while without it connects to localhost.

```
usage: debug-client.py [-h] [-r] [-t]

Listens for all broadcasts from a sensor server.

options:
  -h, --help           show this help message and exit
  -r, --remote         Use this flag to connect to a remote server at 192.168.22.1. If not,
                       localhost is used.
  -t, --transmit-mode  Use this flag to transmit commands to the server.
```
One uses the asyncio API, the other uses the threads API.

### camera-setup-wizard.py
A utility for configuring the pi zero's camera and generating config files for both sensor formatting and cropping (Soon, if we have time: configs for shutter speed and auto-focus).

```
usage: camera-setup-wizard.py [-h] [-s PREVIEW_SIZE] [-m MAX_SIZE MAX_SIZE] [-o]

Walks the user through configuring a camera for use with the omnicam-zero sensor server. Make sure
you're running this through X-forwarding SSH (ssh -X). Must be run on pi zero. To just get a snapshot
from the camera (saved as camera-configuration/snapshot.png, just run `camera-setup-wizard.py -o` then
hit yes.

options:
  -h, --help            show this help message and exit
  -s PREVIEW_SIZE, --preview-size PREVIEW_SIZE
                        The size of the width of the preview window (used as a lores downscale during
                        phase 1 configuration). Default: 840
  -m MAX_SIZE MAX_SIZE, --max-size MAX_SIZE MAX_SIZE
                        When running the formatting config, this is the size the capture starts at. If
                        you're getting crashes due to memory issues. Turn this down. Default:
                        (1500,1500)
  -o, --only-hardware   Use this to just load config files and skip all the format and crop
                        configuration.
```

### retrieve-capture.sh
NOTE: OUTDATED. Now Please use `camera-setup-wizard.py -o` to go directly to the sample photo section of the setup wizard.

A bash scrip to autonomously connect to the omnicam at 192.168.22.1, take a picture using the "rpicam-jpeg" utility app, copy it locally and then display it full-screen using feh:

```
$ sh ./retrieve-capture.sh <name to save retrieved file as (sans ".jpg")>
```

Image save file paths are relative to `configuration-images/retrieved-captures/`.

### install-rpi-dependencies.sh
A bash script to only be used on a raspberry pi zero to install the required python3 dependencies. I use this because python on the rpi0 is managed, and I figure retrieving the managed wheels is a better approach.

# TODO
- [X] Check again that new implementation works on hardware
- [ ] Get camera data into detectors
- [ ] Run detectors
- [ ] Think about using threads instead of asyncio to avoid requiring pause section on detectors.
