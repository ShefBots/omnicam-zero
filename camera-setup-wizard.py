import time
from picamera2 import Picamera2, Preview
from cameraUtils import ConfigType, FormatConfigFields
import cameraUtils
import numpy as np
import json
from pprint import *
import argparse
import os
import copy


args = argparse.ArgumentParser(description="Walks the user through configuring a camera for use with the omnicam-zero sensor server. Make sure you're running this through X-forwarding SSH (ssh -X). Must be run on pi zero.")
args.add_argument("-s", "--preview-size", type=int, nargs=1, default=840, help="The size of the width of the preview window (used as a lores downscale during phase 1 configuration). Default: 840")
args = args.parse_args()

if not args.preview_size:
    print("No preview size specified.")

def ask_b(s, invert=False):
    yn_string = "Y/n" if not invert else "y/N"
    answer = input(f"{s} [{yn_string}]: ").lower()
    if invert and answer == "":
        return False
    return answer == "y" or answer == "yes" or answer == ""

# Initialise the camera
picam2 = Picamera2()

# Get data
sensor_modes = picam2.sensor_modes
camera_controls = picam2.camera_controls
camera_properties = picam2.camera_properties

if ask_b("Would you like to see the sensor modes, controls and properties?"):
    print("\nSENSOR MODES:")
    pprint(sensor_modes)
    print("\nCAMERA CONTROLS:")
    # Note: Fully json.dumps-able
    pprint(camera_controls)
    print("\nCAMERA PROPERTIES:")
    pprint(camera_properties) # cam_props["pixelArraySize"] indicates the maximum size

json_format_config = None
format_config = None

if ask_b("Would you like to attempt to load a formatting configuration file?"):
    json_format_config = cameraUtils.get_config_data(ConfigType.FMT)
    if json_format_config == None:
        print("Error: No formatting config file found.")

def get_preview_size(main_size, prev_size):
    size = (prev_size, int((float(prev_size)/float(main_size[0])) * main_size[1]))
    if size[0] > main_size[0] or size[1] > main_size[1]:
        size = get_preview_size(main_size, min(main_size))
    return size

def configure_lores_to_preview(config, prev_size):
    current = config["main"]["size"]
    new_prev_size = get_preview_size(current, prev_size)
    config["lores"]["size"] = new_prev_size

def get_config_from_json_format_config(fmt_config, align=False, preview=False):
    out = picam2.create_preview_configuration(buffer_count=fmt_config[FormatConfigFields.BUFFER_COUNT],
                                              queue=fmt_config[FormatConfigFields.QUEUE],
                                              main={"size": fmt_config[FormatConfigFields.MAIN_SIZE]},#, format:"YUV420"},
                                              lores={"size": fmt_config[FormatConfigFields.LORES_SIZE]},#, format:"YUV420"},
                                              display="lores",
                                              #sensor={"output_size":mode["size"], "bit_depth":mode["bit_depth"]}
                                             )
    if align:
        picam2.align_configuration(out)
    if preview:
        configure_lores_to_preview(out, args.preview_size)
    return out

def get_json_format_config_from_config(config):
    json_format_config = {
                              FormatConfigFields.BUFFER_COUNT:config["buffer_count"],
                              FormatConfigFields.QUEUE:config["queue"],
                              FormatConfigFields.MAIN_SIZE:config["main"]["size"],
                              FormatConfigFields.LORES_SIZE:config["lores"]["size"]
                           }

if json_format_config == None:
    print("Creating default formatting config file...")
    max_size = camera_properties["PixelArraySize"]
    max_size = (1000,1000) # We'll just use this instead, because the max size kills the pi0
    #preview_size = (min(max_size[0],args.preview_size[0]), min(max_size[1],args.preview_size[1])) if args.preview_size else max_size
    json_format_config = {
                              FormatConfigFields.BUFFER_COUNT:4,
                              FormatConfigFields.QUEUE:False,
                              FormatConfigFields.MAIN_SIZE:max_size,
                              FormatConfigFields.LORES_SIZE:get_preview_size(max_size, args.preview_size),
                           }
    format_config = get_config_from_json_format_config(json_format_config, True, True)

else:
    format_config = get_config_from_json_format_config(json_format_config)

# Formatting phase 1 loop
print("Now starting formatting phase 1 configuration...")
while True:
    picam2.close()
    picam2 = Picamera2()
    picam2.configure(format_config)
    picam2.start_preview(Preview.QT) # For transmitting over the network when connected over ssh -X
    picam2.start()
    if ask_b(f"Main size is at {format_config['main']['size']}. Is this okay?", invert=True):
        picam2.close()
        break
    new_config = {}
    while True:
        new_size = tuple([int(n) for n in input("Enter a new size as two ints: ").split(" ")[:2]])
        new_json_format_config = copy.deepcopy(json_format_config)
        new_json_format_config[FormatConfigFields.MAIN_SIZE] = new_size
        new_json_format_config[FormatConfigFields.LORES_SIZE] = get_preview_size(new_json_format_config[FormatConfigFields.MAIN_SIZE], args.preview_size)

        new_format_config = get_config_from_json_format_config(new_json_format_config, align=True, preview=True)
        print("New generated config:")
        pprint(new_format_config)

        new_size = new_format_config['main']['size']
        if new_size[0] < cameraUtils.CROP_SIZE[0] or new_size[1] < cameraUtils.CROP_SIZE[1]:
            print(f"That size is too small! Please supply a size bigger than {cameraUtils.CROP_SIZE}")
        else:
            format_config = new_format_config
            break
    print("Loading new size...")
    picam2.close()
    

print("Phase 1 complete.")
print(f"Main image size is set and optimised to {format_config['main']['size']}.We will now configure crop size.")

# Convert it back into a json config, now that we know the main size is optimised
json_format_config = get_json_format_config_from_config(format_config)

# Load the crop mask
crop_mask = cameraUtils.load_crop_mask(edge_highlight=True)

# Lores MUST be the same aspect ratio as the main image, but scaled so that the circle aligns.



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
