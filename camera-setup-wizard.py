import time
from picamera2 import Picamera2, Preview
from cameraUtils import ConfigType, FMT_CONFIG_FIELDS
import cameraUtils
import numpy as np
import json
from pprint import *
import argparse
import os


args = argparse.ArgumentParser(description="Walks the user through configuring a camera for use with the omnicam-zero sensor server. Make sure you're running this through X-forwarding SSH (ssh -X). Must be run on pi zero.")
args.add_argument("-s", "--preview_size", type=int, nargs=2, help="The size of the preview window (used as a lores downscale during preview). Will default to maximum size if not specified")
args = args.parse_args()

if not args.preview_size:
    print("No preview size specified.")

def ask_b(s, invert=False):
    yn_string = "Y/n" if not invert else "y/N"
    answer = input(f"{s} [{yn_string}]: ").lower()
    if invert and answer == "":
        return False
    return answer == "y" or answer == ""

# Initialise the camera
picam2 = Picamera2()

# Get data
sensor_modes = picam2.sensor_modes
camera_controls = picam2.camera_controls
camera_properties = picam2.camera_properties

if ask_b("Would you like to see the sensor modes, controls and properties?")
    print("SENSOR MODES:")
    pprint(sensor_modes)
    print("CAMERA CONTROLS:")
    # Note: Fully json.dumps-able
    pprint(camera_controls)
    print("CAMERA PROPERTIES:")
    pprint(camera_properties) # cam_props["pixelArraySize"] indicates the maximum size

loaded_format_config = None
if ask_b("Would you like to attempt to load a formatting configuration file?"):
    loaded_format_config = cameraUtils.get_config_data(ConfigType.FMT)
    if loaded_format_config == None:
        print("Error: No formatting config file found.")

format_config = None
if loaded_format_config == None:
    print("Creating default formatting config file...")
    max_size = camera_properties["pixelArraySize"]
    format_config = picam2.create_preview_configuration(buffer_count=4,
                                                         queue=False,
                                                         main={"size": max_size},#, format:"YUV420"},
                                                         lores={"size": args.preview_size if args.preview_size else max_size},#, format:"YUV420"},
                                                         display="lores",
                                                         #sensor={"output_size":mode["size"], "bit_depth":mode["bit_depth"]}
                                                        )
else:
    format_config = picam2.create_preview_configuration(buffer_count=format_config[FMT_CONFIG_FIELDS.BUFFER_COUNT,
                                                        queue=format_config[FMT_CONFIG_FIELDS.QUEUE],
                                                        main={"size": format_config[FMT_CONFIG_FIELDS.MAIN_SIZE]},#, format:"YUV420"},
                                                        lores={"size": format_config[FMT_CONFIG_FIELDS.LORES_SIZE]},#, format:"YUV420"},
                                                        display="lores",
                                                        #sensor={"output_size":mode["size"], "bit_depth":mode["bit_depth"]}
                                                       )

picam2.configure(format_config)
picam2.start_preview(Preview.QT) # For transmitting over the network when connected over ssh -X
time.sleep(15)

picam2.close()


###### OLD
#
#
## Initialise the camera
#picam2 = Picamera2()
#
#
#print("SENSOR MODES:")
#mode = picam2.sensor_modes[1]
#pprint(picam2.sensor_modes)
#
#print("CAMERA CONTROLS:")
#pprint(picam2.camera_controls)
#print(json.dumps(picam2.camera_controls, indent=2))
#pprint(json.loads(json.dumps(picam2.camera_controls)))
#
#print("CAMERA PROPERTIES:")
#pprint(picam2.camera_properties) # cam_props["pixelArraySize"] indicates the maximum size
#
#config = cameraUtils.getDefaultFormatConfig()
#
#target_size = (240,240)
#
## Configuring
## Buffer count is 4 by default for preview, but more will eliminate jitter at the expense of RAM
## queue is set to False so that we don't queue up any frames and only get the latest frame
## lowres sets lowres
## display sets which buffer is displayed
#config = picam2.create_preview_configuration(buffer_count=4,
#                                             queue=False,
#                                             main={"size": (1080, 1080)},#, format:"YUV420"},
#                                             lores={"size": target_size},#, format:"YUV420"},
#                                             display="lores",
#                                             #sensor={"output_size":mode["size"], "bit_depth":mode["bit_depth"]}
#                                            )
#picam2.align_configuration(config) # Auto-configure to most optimal resolution
#                                   # After this has happened, a new config["lores"/"main"] size will have been selected automagically
#print("CONFIG:")
#pprint(config)
#config["lores"]["size"] = (240,240) # Force the lores size to be 240x240 (maybe we shouldn't do this? We should probably just take a crop ourselves
#picam2.configure(config)
##picam22.start_preview(Preview.DRM) # If we want to display a preview
#picam2.start_preview(Preview.QT) # For transmitting over the network when connected over ssh -X
##picam22.start_preview(Preview.NULL) # No preview (not required, but included for clarity
#
#picam2.title_fields = ["ExposureTime", "AnalogueGain"]
#
## Notes:
## 9.4 Manipulate camera buffers in place
##  - Better for output?
## 8.1 Display overlays
## lores outputs probably *have* to be in YUV format on the zero 2
##  - This prolly means that so does the main buffer
## It's very much worth having two streams - the main one at a higher resolution that captures the entire image at the correct crop
##                                         - and the lower one that is just the high-res one but down-scaled
## We'll prolly want to request the fast sensor mode (4.2.2.3)
## For convenience, we might want to look at using config objects (4.2. Configuration objects) instead of the create_ constructors
##  - Probably not the best plan, since they're persistant. But the config dict is probably the best thing to change.
## We might want to look at FrameDurationLimits to change the framerate of the camera
#
#picam2.start()
##overlay = np.zeros((300, 400, 4), dtype=np.uint8)
##overlay[:150, 200:] = (255, 0, 0, 64) # reddish
##overlay[150:, :200] = (0, 255, 0, 64) # greenish
##overlay[150:, 200:] = (0, 0, 255, 64) # blueish
##picam2.set_overlay(overlay)
#
#
#time.sleep(2) # Let the camera stabalize
#picam2.capture_file(os.path.join(CONFIG_IMAGES_PATH,"test-image.jpg"))
#
#time.sleep(20)
#
#picam2.close()
