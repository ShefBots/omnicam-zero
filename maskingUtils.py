import cv2
from cameraConfigUtils import CropConfigFields
import imageio
import numpy as np

CROP_SIZE = 240 # The size that crop-mask is (crops are always circular)
PERFECT_CROP_IMG_FILENAME = "crop-mask.png" # This just lives out in the open

def load_perfect_crop_mask():
    return load_crop_mask(PERFECT_CROP_IMG_FILENAME)

def load_crop_mask(path):
    img = imageio.imread(path)
    return np.asarray(img)

# NOTE: mask MUST be only 1 dimensional
def make_bool_mask(mask_img):
    # If the mask image didn't exist, just allow that for continuous pass-through:
    if mask_img is None:
        return None
    data = [b < 128 for b in mask_img] # Bool masks are actually inverted.
    ex_data = np.expand_dims(data, 2)
    return np.concatenate((ex_data,ex_data,ex_data), axis=2)

# NOTE: `image` and `mask` MUST be the same size 
# Actually changes `image`
def mask_image(image, bool_mask, mask_colour):
    np.copyto(image, mask_colour, 'unsafe', bool_mask)

def convert_and_crop_yuv420(image_yuv420, crop_config):
    # Convert
    rgb = cv2.cvtColor(image_yuv420, cv2.COLOR_YUV420p2RGB)
    # Crop it down to CROP_SIZE x CROP_SIZE
    crop_pos = crop_config[CropConfigFields.CROP_POSITION.value]
    rgb = rgb[crop_pos[0]:crop_pos[0]+CROP_SIZE, crop_pos[1]:crop_pos[1]+CROP_SIZE]
    return rgb

def convert_crop_and_mask_yuv420(image_yuv420, bool_mask, crop_config, mask_colour):
    # Crop and convert
    rgb = convert_and_crop_yuv420(image_yuv420, crop_config)
    # Apply the crop mask
    mask_image(rgb, bool_mask, mask_colour)

    return rgb
