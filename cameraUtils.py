import os
import shutil
from picamera2 import Picamera2, Preview


CONFIG_IMAGES_PATH = "camera-configuration"
HARDWARE_CONTROLS_FILENAME = "hardware-configuration.json"
FORMAT_CONTROLS_FILENAME = "formatting-configuration.json"

# Full paths
_HW_CONTROLS_PATH = os.path.join(CONFIG_IMAGES_PATH, HARDWARE_CONTROLS_FILENAME)
_FMT_CONTROLS_PATH = os.path.join(CONFIG_IMAGES_PATH, FORMAT_CONTROLS_FILENAME)

def ensure_configuration_path():
    os.makedirs(CONFIG_IMAGES_PATH, exist_ok=True)

def backup_files_if_exist():
    if os.path.exists(_HW_CONTROLS_PATH):
        print("Warning: Hardware control file already exists. Creating backup...")
        shutil.copy(_HW_CONTROLS_PATH, _HW_CONTROLS_PATH + ".bk")
    if os.path.exists(_FMT_CONTROLS_PATH):
        print("Warning: Format control file already exists. Creating backup...")
        shutil.copy(_FMT_CONTROLS_PATH, _FMT_CONTROLS_PATH + ".bk")

# Applies the supplied format object to the picam2 config
# If no format object is supplied, it loads one from disk.
# If no format can be loaded, it gets a default.
def apply_format_config(config, fmt_obj = None):
    out_config = config
    fmt = fmt_obj
    if fmt == None:
        if os.path.exists(_FMT_CONTROLS_PATH):
            # Load the format file if it's found
            with loads(open(_FMT_CONTROLS_PATH)) as loaded_fmt:
                fmt = loaded_fmt
        else:
            # If no config file is found or supplied, just return the default
            max_size = picam2.camera_properties["PixelArraySize"]
            out_config = picam2.create_preview_configuration(buffer_count=4,
                                                              queue=False,
                                                              main={"size": max_size},#, format:"YUV420"},
                                                              lores={"size": max_size},#, format:"YUV420"},
                                                              display="main",
                                                              #sensor={"output_size":mode["size"], "bit_depth":mode["bit_depth"]}
                                                             )
            return out_config
    # Configure the config object
    out_config["main"] = {"size": fmt["main_size"]}
    out_config["lores"] = {"size": fmt["lores_size"]}
    return out_config


# Saves the important format config data into the FORMAT_CONTROLS_FILE
def save_format_config(config):
    #TODO
    pass
