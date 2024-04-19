import os
import shutil
from enum import Enum

class ConfigType(Enum):
    HW = 1
    FMT = 2

class FormatConfigFields(Enum):
    BUFFER_COUNT = "buffer_count"
    QUEUE = "use_queue"
    MAIN_SIZE = "main_size"
    LORES_SIZE = "lores_size"

CONFIG_IMAGES_PATH = "camera-configuration"
HARDWARE_CONTROLS_FILENAME = "hardware-configuration.json"  # Stores the physical hardware settings (wb, exposure, etc)
FORMAT_CONTROLS_FILENAME = "formatting-configuration.json" # Stores the hardware capture size, crop and formatting configuration
#CROP_CONFIG_FILENAME = "crop-configuration.json" # Stores the cropping and masking configuration


CROP_SIZE = (240,240)
PERFECT_CROP_IMG_FILENAME = "crop-mask.png" # This just lives out in the open

def load_crop_mask(edge_highlight=False):
    img = imageio.imread(PERFECT_CROP_IMG_FILENAME)
    return numpy.asarray(img)

# Full paths
_HW_CONTROLS_PATH = os.path.join(CONFIG_IMAGES_PATH, HARDWARE_CONTROLS_FILENAME)
_FMT_CONTROLS_PATH = os.path.join(CONFIG_IMAGES_PATH, FORMAT_CONTROLS_FILENAME)
#_CROP_CONFIG_PATH = os.path.join(CONFIG_IMAGES_PATH, CROP_CONFIG_FILENAME)
_PATH_FROM_TYPE = {
    ConfigType.HW: _HW_CONTROLS_PATH,
    ConfigType.FMT: _FMT_CONTROLS_PATH,
}

def ensure_configuration_path():
    os.makedirs(CONFIG_IMAGES_PATH, exist_ok=True)

def backup_files_if_exist():
    for p in _PATH_FROM_TYPE.values():
        if os.path.exists(p):
            print("Warning: Hardware control file already exists. Creating backup...")
            shutil.copy(p, p + ".bk")
        if os.path.exists(p):
            print("Warning: Format control file already exists. Creating backup...")
            shutil.copy(p, p + ".bk")

def get_config_data(config_type):
    path = _PATH_FROM_TYPE[config_type]
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return None

# Applies the supplied format object to the picam2 config
# If no format object is supplied, it loads one from disk.
# If no format can be loaded, it gets a default.
#def apply_format_config(config, fmt_obj = None):
#    out_config = config
#    fmt = fmt_obj
#    if fmt == None:
#        if os.path.exists(_FMT_CONTROLS_PATH):
#            # Load the format file if it's found
#            with loads(open(_FMT_CONTROLS_PATH)) as loaded_fmt:
#                fmt = loaded_fmt
#        else:
#            # If no config file is found or supplied, just return the default
#            max_size = picam2.camera_properties["PixelArraySize"]
#            out_config = picam2.create_preview_configuration(buffer_count=4,
#                                                              queue=False,
#                                                              main={"size": max_size},#, format:"YUV420"},
#                                                              lores={"size": max_size},#, format:"YUV420"},
#                                                              display="main",
#                                                              #sensor={"output_size":mode["size"], "bit_depth":mode["bit_depth"]}
#                                                             )
#            return out_config
#    # Configure the config object
#    out_config["main"] = {"size": fmt["main_size"]}
#    out_config["lores"] = {"size": fmt["lores_size"]}
#    return out_config


# Saves the important format config data into the FORMAT_CONTROLS_FILE
def save_format_config(config):
    #TODO
    pass
