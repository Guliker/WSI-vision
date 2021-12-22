"""
Load all the settings used for the vision module
"""
""" ----- overall settings ----- """
import cv2
import gxipy as gx
import numpy as np
font = cv2.FONT_HERSHEY_SIMPLEX

""" ----- window positions ----- """
pos_raw_image = (1380,250)
pos_img_crop = (1300,280)
pos_four_filters = (1380,0)
pos_corrected_image = (880,110)
pos_recept_result = (600,0)
pos_viewer = (0,50)

""" ----- block info ----- """
## values of a block information
block_small_area = 500
block_width_big = 55
block_height = 26           ## height of the block without the nobs
block_height_offset = 4     ## height of the nobs of the block

""" ----- workspace ----- """
## distance to check rotation
workspace_height = block_height * 12
workspace_width = int(block_width_big * 3)

""" ----- Daheng Imaging Camera ----- """
# comment and uncomment these 2 lines for testing
device_manager = gx.DeviceManager()             ## device manager for the Daheng Imaging camera
camera = device_manager.open_device_by_index(1) ## device opened on index one, the first camera

#cam_resolution = (1600, 900)
#cam_offset_resolution = (744, 560)
#resolution = (3088, 2048)
#offset_resolution = (0, 0)
cam_resolution = (904,1600)
cam_offset_resolution = (1096, 0)

cam_gain_rgb = (1.4 , 1.0, 2.2)
# good values for 50hz lighting
# 25; 20; 16.67; 12.5
cam_frame_rate = 10

cam_exposure = 24000
cam_gain = 8

cam_scale = 0.5     ## scaling of the camera image to the filters

""" ----- mask ----- """
mask_scale_rotation = float(1)/1     ## scaling for the rotation mask
## lab offsets for the color finder, each value is an hard value, order is:
# 0 = lum
# 1 = a; green - magenta
# 2 = b; blue - yellow
lab_offset_table = [10,8,8]
## type of color space used, many possibilities
# https://learnopencv.com/color-spaces-in-opencv-cpp-python/
# COLOR_BGR2RGB, COLOR_BGR2LAB, COLOR_BGR2YCrCb, COLOR_BGR2HSV, COLOR_BGR2HSL
color_space = cv2.COLOR_BGR2LAB
#color_space = cv2.COLOR_BGR2YCrCb

block_split_cut_size = 4    ## line size to split blocks
erode_dilate = 2            ## ammount of erosion and dilation applied to the color masks
kernal = np.array([ [1,1,1],
                    [1,1,1],
                    [1,1,1]     ], "uint8")     ## kernal used for dilation and erosion
'''
kernal = np.array([ [1,1,1,1,1],
                    [1,1,1,1,1],
                    [1,1,1,1,1],
                    [1,1,1,1,1],
                    [1,1,1,1,1]     ], "uint8")
'''

""" ---- colors ----- """
color_name_table = (        "green",        "yellow",       "blue",         "red"       )   # name of each color
color_bgr_table = (         (0,200,0),      (0,200,255),    (255,100,0),    (0,0,255)    )  # colors used to display on screen text and boxes
lab_min_max_table = [       [[],[]],        [[],[]],        [[],[]],        [[],[]]     ]   # here are the min and max LAB values stored for each color
color_mask_table = [        [],             [],             [],             []          ]   # here are the bit masks stored for each color
color_contour_table = [     [],             [],             [],             []          ]   # here are the contours of each block stored for each color

## empty window to place frames in
window_blank = np.zeros((1080,1920,3), np.uint8)
window_green = np.full((1080,1920,3), (0,50,0), np.uint8)

""" ----- recept result ----- """
font_size_rr = 1
spacing = 85*font_size_rr
colom1 = 10
colom2 = 150
window_size = (950, 250,3)

""" ----- calibration ----- """
calibration_search_height = 80
calibration_serach_height_offset = 70
calibration_search_width = 80

""" ----- socket ----- """
# IJsel laptop
#HOST = '192.168.14.219'
# debug laptop
#HOST = '192.168.14.174'
HOST = ''
PORT = 30001
HOST_send = '192.168.14.219'

command_message_vision = "asking_for_file"

""" ----- XML ----- """
map_block = {
    1: ("Green", "1"),
    2: ("Yellow", "1"),
    3: ("Blue", "1") ,
    4: ("Red", "1"),
    5: ("Green", "2"),
    6: ("Yellow", "2"),
    7: ("Blue", "2"),
    8: ("Red", "2"),
}

map_pos = {
    1: "-0.5",
    2: "0",
    3: "0.5",
}

""" ----- """
num_to_block = {
    1: "G1",
    2: "Y1",
    3: "B1",
    4: "R1",
    5: "G2",
    6: "Y2",
    7: "B2",
    8: "R2",
}

num_to_pos = {
    1: "L",
    2: "M",
    3: "R",
}

""" ----- viewer ----- """
viewer_size = (668,974)