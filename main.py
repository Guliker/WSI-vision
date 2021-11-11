"""
Based on python code for Multiple Color Detection:
https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/

    to run:
install python 2.17.18
pip2 install numpy
pip2 install opencv-contrib-python

cd "Windesheim Office365\O365-Fabriek van de Toekomst 21-22 sem1 - IJsseltechnologie\3 realiseren\Camera Python"
python2
then run this file with python

controls:
- to shift mid offset to the left
+ to shift mid offset to the right
d to open debug windows and info
"""

""" ----- IMPORTS ----- """
import gxipy as gx
import module_camera as mc
import module_functions as mf

#import math
import numpy as np
import cv2
import datetime
""" ----- ----- ----- """

""" ----- DEFINE ----- """
debug = False
config = True
font = cv2.FONT_HERSHEY_SIMPLEX

device_manager = gx.DeviceManager()
camera = device_manager.open_device_by_index(1)
cam_scale = 0.5
mask_scale = float(1)/2

# settings for the calibration window
x_offset = 0
y_offset = 0
search_height = 350
search_width = 50

# lab offsets for the color finder, each value is an hard value, order is:
# 0 = lum
# 1 = a; green - magenta
# 2 = b; blue - yellow
lab_offset_table = [50,5,5]

# hard values of block information, !!!!! should be added to calibration mode !!!!!
block_small_area = 500
block_width_big = 55
block_height = 26
block_height_offset = 2


# line size to split blocks
cut_size = 12
erode_dilate = 2
# distance to check rotation
workspace_height = block_height * 12
workspace_width = int(block_width_big * 3)
off_orr = int(block_width_big/4)

# type of color space used, many possibilities
# https://learnopencv.com/color-spaces-in-opencv-cpp-python/
# COLOR_BGR2RGB, COLOR_BGR2LAB, COLOR_BGR2YCrCb, COLOR_BGR2HSV, COLOR_BGR2HSL
color_space = cv2.COLOR_BGR2LAB
#color_space = cv2.COLOR_BGR2YCrCb

# all logic tables
color_name_table = (        "green",        "yellow",       "blue",         "red"       )   # name of each color
color_bgr_table = (         (0,200,0),     (0,190,255),    (255,70,0),     (0,0,255)    )   # colors used to display on screen text and boxes
lab_min_max_table = [       [[],[]],        [[],[]],        [[],[]],        [[],[]]     ]   # here are the min and max LAB values stored for each color
color_mask_table = [        [],             [],             [],             []          ]   # here are the bit masks stored for each color
color_contour_table = [     [],             [],             [],             []          ]   # here are the contours of each block stored for each color
color_mask_combine = []
""" ----- ----- ----- """

# trackbar callback fucntion does nothing but required for trackbar
def nothing(x):
    pass
    
start_time = datetime.datetime.now()
def get_time(name, start):
    now = datetime.datetime.now()
    delta = now - start
    print("-----"),
    print(name),
    print(": "),    
    print(int(delta.total_seconds() * 1000)),
    print("ms "),

""" ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- """
""" ----- MAIN LOOP FOR CALIBRATION ----- """
""" ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- """
#(cam, dev, exp, res[], res_o[], fps, gain, gain_rgb[])
print("initialisation ... "),
mc.init(camera, device_manager)
step_index = 0
print("complete")

while(1):    
    #time to get frame
    get_time("process time", start_time)
    
    # get one frame of the camera
    frame = mc.read(camera, cam_scale)
    
    #time to get frame
    get_time("frame time", start_time)
    
    print("")
    # get start time
    start_time = datetime.datetime.now()

    # create copy of frame to show to user
    final_frame = frame.copy()

    # get info of that frame
    height, width, depth = frame.shape

    # crop image to centre
    x = int((width - search_width)/2) + x_offset
    y = int((height - search_height)/2) + y_offset
    img_crop = frame[y:y+search_height, x:x+search_width]
    # show the box that shows where the crop is
    mf.draw_calibration_box(final_frame, x, y, search_width, search_height,
                            color_name_table[step_index], color_bgr_table[step_index])
  
    # convert cropped image to min and max LAB values
    lab_min,lab_max = mf.lab_min_max_calculate(img_crop, color_space, lab_offset_table)

    # in debug mode: display the lab min and max values
    # and display the cropped image
    if(debug):
        #min
        cv2.putText(final_frame, str(lab_min), (20,20),
                    font, 0.4,
                    color_bgr_table[step_index])   
        # max
        cv2.putText(final_frame, str(lab_max), (20,40),
                    font, 0.4,
                    color_bgr_table[step_index])
        # show the cropped image
        cv2.imshow('img_crop', img_crop)
    
    # show operator instructions
    cv2.putText(final_frame, "Calibration mode", (10,150),
                font, 1,
                (255,255,255))
    cv2.putText(final_frame, "press space to save", (10,200),
                font, 1,
                (255,255,255))

    # show the video with the calibration box
    cv2.imshow("Video", final_frame)
    
    key = cv2.waitKey(10) & 0xFF 
    # check for spacebar to go to next step
    if key == ord(' '):
        # save the found lab values
        mf.lab_save(step_index, lab_min, lab_max, lab_min_max_table)
        # go to the next color
        step_index += 1
        # test if there is a next color
        if step_index >= len(color_name_table):
            break
    # check d key to toggle debug mode
    if key == ord('d'):
        if(debug):
            cv2.destroyWindow("img_crop")
        debug = not debug

""" ----- EXIT ----- """

# print all the saved LAB min and max values
# cv2.destroyAllWindows()
print("\n-----values saved: ")
if(debug):
    cv2.destroyWindow("img_crop")
for i,name in enumerate(color_name_table):
    print(name + ":")
    print(lab_min_max_table[i])

""" ----- ----- ----- """

""" ----- MAIN LOOP BLOCK FINDER ----- """
mid_pos = 2
while(1):
    #time to get frame
    get_time("process time", start_time)
    
    # get one frame of the camera
    frame = mc.read(camera, cam_scale)
    
    #time to get frame
    get_time("frame time", start_time)
    
    print("")
    # get start time
    start_time = datetime.datetime.now()
    
    # Convert the frame
    # BGR(RGB color space) to 
    # lab(hue-saturation-value)
    lab_frame = cv2.cvtColor(frame, color_space)
    
    kernal = np.array( [[1,1]    ,
                        [1,1]   ,], "uint8")
    
    # create masks for each color, and check rotation of the masks
    for i, name in enumerate(color_name_table):
        #creates a color mask
        color_mask_table[i] = mf.mask_color(kernal, lab_frame, lab_min_max_table[i], erode_dilate, erode_dilate+1, mask_scale)
        if (i):
            color_mask_combine = cv2.bitwise_or(color_mask_combine, color_mask_table[i])
        else:
            color_mask_combine = color_mask_table[i]
    
    #color_mask_combine = cv2.dilate(color_mask_combine, kernal, iterations=1)
    #color_mask_combine = cv2.erode(color_mask_combine, kernal, iterations=2)
    contours_combined = mf.create_contour(color_mask_combine, block_small_area*mask_scale, method=cv2.CHAIN_APPROX_NONE)
    
    #time to get contour
    #get_time(start_time)
    
    if(contours_combined):
        workspace = mf.get_workspace(frame, contours_combined, workspace_width, workspace_height, off_orr, debug, mask_scale)
        work_frame = mf.transform(frame, workspace, workspace_width, workspace_height)
        lab_frame = cv2.cvtColor(work_frame, color_space)
        
        # time to get workplace
        #get_time(start_time)
        
        #cv.drawContours(frame, contours, 3, (0,255,0), 3)
        # after rotated make contours of the mask
        
        # loop through all the colors and make for each color an mask and contours
        for i, name in enumerate(color_name_table):
            #creates a color mask
            color_mask_table[i] = mf.mask_color(kernal, lab_frame, lab_min_max_table[i], erode_dilate, erode_dilate+1)
            
            # creates contours of the created mask
            # contour = create_contour(color_mask_table[i])
            color_contour_table[i] = mf.create_contour(color_mask_table[i], block_small_area)
            
            # loop trough all contours
            for contour in color_contour_table[i]:
                if(debug):
                    mf.draw_contour(work_frame, contour, color_bgr_table[i], debug)
                mf.split_contour(color_mask_table[i], contour, block_height, block_height_offset, cut_size)
            
            color_contour_table[i] = mf.create_contour(color_mask_table[i], block_small_area)
            for contour in color_contour_table[i]:
                if(not debug):
                    mf.draw_contour(work_frame, contour, color_bgr_table[i], debug)
            
            # show the cut up frame

            # write color channel text to display
            cv2.putText(color_mask_table[i], name, (10,20),
                        font, 1,
                        (255, 255, 255))
            cv2.putText(color_mask_table[i], str(lab_min_max_table[i][0]), (10,45),
                        font, 0.5,
                        (255, 255, 255))
            cv2.putText(color_mask_table[i], str(lab_min_max_table[i][1]), (10,60),
                        font, 0.5,
                        (255, 255, 255))
        
        # time to get all colors
        #get_time(start_time)
        
        # combine all the colors for sorting
        all_contours = color_contour_table[0] + color_contour_table[1] + color_contour_table[2] + color_contour_table[3]
        
        # fill a color array to remember the size and color of each contour
        all_colors = []
        for i, name in enumerate(color_name_table):
           mf.block_color_fill(all_colors, color_contour_table[i], i, block_width_big)

        # sort all blocks from bottom-top and print
        contours,colors = mf.sort_contours(all_contours,all_colors)

        all_pos = []
        
        # place mid line
        if(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[0])
            x = int(x + (mid_pos/float(4))*w)
            y = int(y + 0.5*h)
            cv2.circle(work_frame, (x,y), 5, (255,255,255), -1)
            
            compare_x = x
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                mid_x = int(x + 0.5*w)
                if (mid_x > compare_x + 10):    # right side
                    all_pos.append(3)
                elif (mid_x < compare_x - 10):  # left side
                    all_pos.append(1)
                else:                           # middle
                    all_pos.append(2)
                    
        
        cv2.putText(frame, str(colors), (20,40),
                    font, 1,
                    (255, 255, 255))    

        cv2.putText(frame, str(all_pos), (20,100),
                    font, 1,
                    (255, 255, 255))    
                
        # in debug mode: show the mask frames of each color
        if(debug):
            debug_frame = mc.four_in_one_frame(color_mask_table, 0.8)
            cv2.imshow("rybg_frame", debug_frame)
            cv2.imshow("color_mask_combine", color_mask_combine)

    # show normal view + bounding boxes    
    cv2.imshow("Video", frame)
    cv2.imshow("Raw Frame", work_frame)

    #get_time(start_time)

    key = cv2.waitKey(10) & 0xFF 
    # check spacebar to exit
    if key == ord(' '):
        break
    # check d key to toggle debug mode
    if key == ord('d'):
        if(debug):
            cv2.destroyWindow("rybg_frame")
            cv2.destroyWindow("color_mask_combine")
        debug = not debug
    if key == ord('-'):
        mid_pos -= 1
    if key == ord('='):
        mid_pos += 1

""" ----- ----- ----- """

""" ----- EXIT ----- """
mc.close(camera)
cv2.destroyAllWindows()

""" ----- ----- ----- """

'''
translator:
1 = Green Small     5 = Green Big
2 = Yellow Small    6 = Yellow Big
3 = Blue Small      7 = Blue Big
4 = Red Small       8 = Red Big

1 = left
2 = middle
3 = right

height testing:
1 = 30 - 36
2 = 54 - 60
3 = 78 - 84
'''