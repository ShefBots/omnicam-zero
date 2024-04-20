import time
from picamera2 import Picamera2, Preview
from cameraUtils import ConfigType, FormatConfigFields, CropConfigFields, CROP_SIZE
import cameraUtils
import numpy as np
import json
from pprint import *
import argparse
import os
import copy

print("Importing OpenCV2, please wait...")
import cv2

SNAPSHOT_NAME = "snapshot.png"


args = argparse.ArgumentParser(description="Walks the user through configuring a camera for use with the omnicam-zero sensor server. Make sure you're running this through X-forwarding SSH (ssh -X). Must be run on pi zero.")
args.add_argument("-s", "--preview-size", type=int, nargs=1, default=840, help="The size of the width of the preview window (used as a lores downscale during phase 1 configuration). Default: 840")
args.add_argument("-m", "--max-size", type=int, nargs=2, default=(1000, 1000), help="When running the formatting config, this is the size the capture starts at. If you're getting crashes due to memory issues. Turn this down. Default: (1500,1500)")
args.add_argument("-o", "--only-hardware", action="store_true", help="Use this to just load config files and skip all the format and crop configuration.")
args = args.parse_args()

cameraUtils.ensure_configuration_path()

if not args.preview_size:
    print("No preview size specified.")

def ask_b(s, invert=False):
    yn_string = "Y/n" if not invert else "y/N"
    answer = input(f"{s} [{yn_string}]: ").lower()
    if invert and answer == "":
        return False
    return answer == "y" or answer == "yes" or answer == ""

def get_preview_size(main_size, prev_size):
    size = (prev_size, int((float(prev_size)/float(main_size[0])) * main_size[1]))
    if size[0] > main_size[0] or size[1] > main_size[1]:
        size = get_preview_size(main_size, min(main_size))
    return size

def configure_lores_to_preview(config, prev_size):
    current = config["main"]["size"]
    new_prev_size = get_preview_size(current, prev_size)
    config["lores"]["size"] = new_prev_size

def get_config_from_json_format_config(pcam, fmt_config, align=False, preview=False):
    pprint(fmt_config)
    out = pcam.create_preview_configuration(buffer_count=fmt_config[FormatConfigFields.BUFFER_COUNT.value],
                                              queue=fmt_config[FormatConfigFields.QUEUE.value],
                                              main={"size": fmt_config[FormatConfigFields.MAIN_SIZE.value]},#, format:"YUV420"},
                                              lores={"size": fmt_config[FormatConfigFields.LORES_SIZE.value]},#, format:"YUV420"},
                                              display="lores",
                                              #sensor={"output_size":mode["size"], "bit_depth":mode["bit_depth"]}
                                             )
    if align:
        pcam.align_configuration(out)
    if preview:
        configure_lores_to_preview(out, args.preview_size)
    return out

def get_json_format_config_from_config(config):
    json_format_config = {
                              FormatConfigFields.BUFFER_COUNT.value:config["buffer_count"],
                              FormatConfigFields.QUEUE.value:config["queue"],
                              FormatConfigFields.MAIN_SIZE.value:config["main"]["size"],
                              FormatConfigFields.LORES_SIZE.value:config["lores"]["size"]
                           }
    return json_format_config

def setup_format_and_crop(args):

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


    if json_format_config == None:
        print("Creating default formatting config file...")
        max_size = camera_properties["PixelArraySize"]
        max_size = (min(args.max_size[0],max_size[0]), min(args.max_size[1], max_size[1])) # We'll just use this instead, because the max size kills the pi0
        #preview_size = (min(max_size[0],args.preview_size[0]), min(max_size[1],args.preview_size[1])) if args.preview_size else max_size
        json_format_config = {
                                  FormatConfigFields.BUFFER_COUNT.value:4,
                                  FormatConfigFields.QUEUE.value:False,
                                  FormatConfigFields.MAIN_SIZE.value:max_size,
                                  FormatConfigFields.LORES_SIZE.value:get_preview_size(max_size, args.preview_size),
                               }
        format_config = get_config_from_json_format_config(picam2, json_format_config, True, True)

    else:
        format_config = get_config_from_json_format_config(picam2, json_format_config)

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
        
        while True:
            new_size = tuple([int(n) for n in input("Enter a new size as two ints: ").split(" ")[:2]])
            new_json_format_config = copy.deepcopy(json_format_config)
            new_json_format_config[FormatConfigFields.MAIN_SIZE.value] = new_size
            new_json_format_config[FormatConfigFields.LORES_SIZE.value] = get_preview_size(new_json_format_config[FormatConfigFields.MAIN_SIZE.value], args.preview_size)

            new_format_config = get_config_from_json_format_config(picam2, new_json_format_config, align=True, preview=True)
            print("New generated config:")
            pprint(new_format_config)

            new_size = new_format_config['main']['size']
            if new_size[0] < cameraUtils.CROP_SIZE or new_size[1] < cameraUtils.CROP_SIZE:
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
    crop_mask = cameraUtils.load_crop_mask()

    ORANGE = (252, 186, 3, 200)

    # Convert to a mask that works as an overlay (i.e. this will be a sub-section of an overlay object
    # TODO: Make this not just semiopaque and white but an actual outline
    crop_overlay_subsection = np.zeros((crop_mask.shape[0], crop_mask.shape[1], 4), dtype=np.uint8)
    for x in range(1,crop_mask.shape[0]-1):
        for y in range(1,crop_mask.shape[1]-1):
            if crop_mask[x,y]>128 and  (crop_mask[x+1,y]<128 or crop_mask[x-1,y]<128 or
                                        crop_mask[x,y+1]<128 or crop_mask[x,y-1]<128 or
                                        crop_mask[x+1,y+1]<128 or crop_mask[x-1,y-1]<128 or
                                        crop_mask[x-1,y+1]<128 or crop_mask[x+1,y-1]<128):
                crop_overlay_subsection[x,y] = ORANGE

    # Get crop controls
    crop_config = None
    if ask_b("Would you like to attempt to load the crop configuration file?", invert=True):
        crop_config = cameraUtils.get_config_data(ConfigType.CRP)
        if crop_config == None:
            print("Error: No crop config file found.")

    if crop_config == None:
        # Create default crop config
        crop_config = {}
        crop_config[CropConfigFields.CROP_POSITION.value] = (0,0)

    #main_size = format_config["main"]["size"]
    def get_new_lores_size_for(s, main_size):
        new_lores_size = None
        if(main_size[0] < main_size[1]):
            new_lores_size = [1.0, float(main_size[1])/float(main_size[0])]
        else:
            new_lores_size = [float(main_size[0])/float(main_size[1]), 1.0]
        new_lores_size = tuple([int(n*s) for n in new_lores_size])
        return new_lores_size


    # Make Lo-res the smallest it can be to start (crop size)
    new_lores_size = get_new_lores_size_for(CROP_SIZE, format_config["main"]["size"])

    # Store the main size for ease of use
    #main_size = json_format_config[FormatConfigFields.MAIN_SIZE.value]

    def update_overlay(lores_size, crop_config):
        overlay = np.zeros((lores_size[0], lores_size[1], 4), dtype=np.uint8)
        crop_pos = crop_config[CropConfigFields.CROP_POSITION.value]
        overlay[crop_pos[0]:crop_pos[0]+CROP_SIZE, crop_pos[1]:crop_pos[1]+CROP_SIZE] = crop_overlay_subsection
        picam2.set_overlay(overlay)

    new_config = None # Where we'll store the new config
    while True:
        picam2.close()
        picam2 = Picamera2()

        # Generate a new config, this time only optimising the main stream and leaving the lores stream as the bit that it is
        json_format_config[FormatConfigFields.LORES_SIZE.value] = new_lores_size
        new_config = get_config_from_json_format_config(picam2, json_format_config, align=False, preview=False)

        picam2.configure(new_config)
        picam2.start_preview(Preview.QT) # For transmitting over the network when connected over ssh -X
        picam2.start()

        update_overlay(new_lores_size, crop_config)

        # Now ask if the overlay needs to move or stuff

        if ask_b(f"Does the mask align correctly?", invert=True):
            picam2.close()
            break

        main_size = new_config["main"]["size"]
        print(f"lores size: {new_lores_size}, crop size: {CROP_SIZE}, main size: {main_size}")
        print("Edit commands:")
        print(" >,< n - right/left the crop location")
        print(" ^,v n - up/down the crop location")
        print(" *,/ n - increase and decrease the lores size.")
        print("  d    - indicate you're done.")

        while True:
            cmd = input("Enter command: ")
            if(cmd == "d"):
                break
            cmd = cmd.split(" ")
            num = int(cmd[1]) if len(cmd) > 1 else 1
            command_type = None
            movement = (0,0)
            size_change = 0
            match cmd[0]:
                case "^":
                    command_type = "move"
                    movement = (-num, 0)
                case "v":
                    command_type = "move"
                    movement = (num, 0)
                case "<":
                    command_type = "move"
                    movement = (0, -num)
                case ">":
                    command_type = "move"
                    movement = (0, num)
                case "*":
                    command_type = "resize"
                    size_change = num
                case "/":
                    command_type = "resize"
                    size_change = -num

            # Actually try and make the moves
            proposed_lores_size = (new_lores_size[0] + size_change, new_lores_size[1] + size_change)
            if main_size[0] < proposed_lores_size[0] or main_size[1] < proposed_lores_size[1]:
                print("Error: Proposed size change makes the lores image bigger than the main image!")
                continue
            if size_change != 0:
                # Only update the lores size if it's actually changed, as it requires a whole re-start of the camera
                new_lores_size = proposed_lores_size
                break # restart the camera

            proposed_crop_pos = (crop_config[CropConfigFields.CROP_POSITION.value][0] + movement[0],
                                 crop_config[CropConfigFields.CROP_POSITION.value][1] + movement[1])
            if proposed_crop_pos[0] < 0 or proposed_crop_pos[1] < 0 or proposed_crop_pos[0] + CROP_SIZE > proposed_lores_size[0] or proposed_crop_pos[1] + CROP_SIZE > proposed_lores_size[1]:
                print("Error: Proposed movement would move the crop outside of the image!")
                continue

            # Update the crop pos, no need to exit the for loop
            crop_config[CropConfigFields.CROP_POSITION.value] = proposed_crop_pos
            update_overlay(new_lores_size, crop_config)
                

        print("Loading new size...")
        picam2.close()

    print("Phase 2 complete.")
    # We now finally have a json format config file with optimised output in main and lores set to a sane size
    # We also have a configured crop mask config in crop_config for that format config
    json_format_config = get_json_format_config_from_config(new_config)

    print("FORMAT:")
    pprint(json_format_config)

    print("CROP:")
    pprint(crop_config)

    # SAVE the configurations
    cameraUtils.backup_files_if_exist()

    print("Saving...")
    cameraUtils.save_config_data(ConfigType.FMT, json_format_config)
    cameraUtils.save_config_data(ConfigType.CRP, crop_config)
    print("Saved!")



print("Welcome to the hastily put together pi zero camera configuration wizard!")
if not args.only_hardware:
    setup_format_and_crop(args)

picam2 = Picamera2()
json_format_config = cameraUtils.get_config_data(ConfigType.FMT)
format_config = get_config_from_json_format_config(picam2, json_format_config)
crop_config = cameraUtils.get_config_data(ConfigType.CRP)
picam2.close()

print("Loaded CROP and FORMAT configs from file.")
print("FORMAT:")
pprint(format_config)
print("\nCROP:")
pprint(crop_config)

if ask_b("Would you like to take a cv2 photo?"):
    picam2 = Picamera2()

    # Generate a config from the json format config image, making sure not to align or preview anything.
    new_config = get_config_from_json_format_config(picam2, json_format_config, align=False, preview=False)
    picam2.configure(new_config)
    picam2.start_preview(Preview.NULL) # We don't want to transmit the data anywhere
    picam2.start()
    time.sleep(2) # Sleep for a bit to wait for things to settle

    # Take the photo, convert it into RGB space
    yuv420 = picam2.capture_array()
    rgb = cv2.cvtColor(yuv420, cv2.COLOR_YUV420p2RGB)
    crop_pos = crop_config[CropConfigFields.CROP_POSITION.value]

    # Crop it down to CROP_SIZE x CROP_SIZE
    rgb = rgb[crop_pos[0]:crop_pos[0]+CROP_SIZE, crop_pos[1]:crop_pos[1]+CROP_SIZE]

    # ...apply the crop mask? TODO

    # Save the image
    save_path = os.path.join(cameraUtils.CONFIG_IMAGES_PATH, SNAPSHOT_NAME)
    print(f"Saving image as {save_path}...")
    cv2.imwrite(save_path, rgb)
    print("Saved!")

    picam2.stop()


print("Now on to camera hardware configuration!")

# Use picam2.capture_request(flush=True) to ensure the photo is one that was taken at or *after* the function is called.


# For capturing:
#yuv420 = picam2.capture_array()
#rgb = cv2.cvtColor(yuv420, cv2.COLOR_YUV420p2RGB)


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
