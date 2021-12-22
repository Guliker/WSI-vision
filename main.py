"""
Based on python code for Multiple Color Detection:
https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/

Usefull links:
https://images4.programmersought.com/894/e7/e759c86ba15f596c2d5a8e795de4925e.png
https://www.programmersought.com/article/7916959440/

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
x to cancel the current product
"""
print("initialisation ... "),

""" ----- IMPORTS ----- """
import config as cfg
import gxipy as gx
import module_camera as mc
import module_functions as mf
import module_socket as ms
import module_recept_result as mrr
import module_workspace as mw
import module_xml   as mx
import module_display_window as mdw

#import math
import numpy as np
import cv2
import datetime
""" ----- ----- ----- """

""" ----- DEFINE ----- """
## state of the debug mode
debug = False

## all logic tables
color_mask_combine = []
current_product = []
buffer_product = []

completed_flag = 0

OBS_window = mdw.OBS_open(2)
""" ----- ----- ----- """

# trackbar callback fucntion does nothing but required for trackbar
def nothing(x):
    pass
    
# used to check frame times and process time
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
mc.init(cfg.camera, cfg.device_manager)
print("complete")
while(True):
    mc.auto_calibrate(cfg.camera)
    step_index = 0

    while(step_index < len(cfg.color_name_table)):
        window_vision = cfg.window_blank.copy()
        
        if(debug):
            #time to get frame
            get_time("process time", start_time)
        
        # get one frame of the camera
        frame = mc.read(cfg.camera, cfg.cam_scale)

        if(debug):
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
        x = int((width - cfg.calibration_search_width)/2)
        y = int((height - cfg.calibration_search_height)/2) + cfg.calibration_serach_height_offset
        img_crop = frame[y:y+cfg.calibration_search_height, x:x+cfg.calibration_search_width]
        # show the box that shows where the crop is
        mf.draw_calibration_box(final_frame, x, y, cfg.calibration_search_width, cfg.calibration_search_height,
                                cfg.color_name_table[step_index], cfg.color_bgr_table[step_index])
      
        # convert cropped image to min and max LAB values
        lab_min,lab_max = mf.find_min_max_color(img_crop, cfg.color_space, cfg.lab_offset_table)

        # in debug mode: display the lab min and max values
        # and display the cropped image
        if(debug):
            #min
            cv2.putText(window_vision, str(lab_min), mf.pos_shift(cfg.pos_img_crop,(0,-40)),
                        cfg.font, 0.4,
                        cfg.color_bgr_table[step_index])   
            # max
            cv2.putText(window_vision, str(lab_max), mf.pos_shift(cfg.pos_img_crop,(0,-20)),
                        cfg.font, 0.4,
                        cfg.color_bgr_table[step_index])
            # show the cropped image
            mf.overlay_image(window_vision, img_crop, cfg.pos_img_crop)
        
        # show operator instructions
        cv2.putText(window_vision, "Calibration mode", (50,450),
                    cfg.font, 5,
                    (255,255,255),4)
        cv2.putText(window_vision, "press space", (50,700),
                    cfg.font, 5,
                    (255,255,255),4)
        cv2.putText(window_vision, "to save", (50,900),
                    cfg.font, 5,
                    (255,255,255),4)
        cv2.putText(window_vision, str(cfg.color_name_table[step_index]), (700,900),
                    cfg.font, 5,
                    cfg.color_bgr_table[step_index],4)

        # show the video with the calibration box
        
        mf.overlay_image(window_vision, final_frame, cfg.pos_raw_image)
        #cv2.imshow("Video", final_frame)
        cv2.imshow("window vision", window_vision)
        
        
        key = cv2.waitKey(10) & 0xFF 
        # check for spacebar to go to next step
        if key == ord(' '):
            # save the found lab values
            mf.save_min_max_color(step_index, lab_min, lab_max, cfg.lab_min_max_table)
            # go to the next color
            step_index += 1
        # check d key to toggle debug mode
        if key == ord('d'):
            if(debug):
                cv2.destroyWindow("img_crop")
            debug = not debug
        if (key == 27):
            mc.close(cfg.camera)
            cv2.destroyAllWindows()
            exit()

    """ ----- EXIT ----- """

    # print all the saved LAB min and max values
    # cv2.destroyAllWindows()
    print("----- values saved: ")
    if(debug):
        cv2.destroyWindow("img_crop")
    for i,name in enumerate(cfg.color_name_table):
        print(name + ":	"),
        print(cfg.lab_min_max_table[i])
    mc.check_auto_calibrate(cfg.camera)
    print("")

    """ ----- ----- ----- """

    """ ----- MAIN LOOP BLOCK FINDER ----- """
    mid_pos = 2
    frame_count = 0
    # test code
    #buffer_product = [[[7,3], [8,1], [4,2], [8,3], [8,2], [6,3], [7,1], [7,2]],[[7,2], [7,1], [6,3], [8,2], [8,3], [4,2], [8,1], [7,3]]]

    viewer_frame = mdw.OBS_frame(OBS_window)

    while(1):
        frame_count += 1
        window_vision = cfg.window_blank.copy()
        color_pos = []
        
        # get product to be checked
        if(frame_count > 10):
            temp_product = ms.ask_for_data(0.01,5.0)
            # check if there is a product received
            if(len(temp_product)):
                buffer_product.append(temp_product)

            # check if the current checked product is empty
            if(not len(current_product) and len(buffer_product)):
                current_product = buffer_product.pop(0)
                mid_pos = current_product[0][1]
                mx.xml_generate(current_product)
                
            # a product? update viewer
            viewer_frame = mdw.OBS_frame(OBS_window)

        # display viewer frame
        mf.overlay_image(window_vision, viewer_frame, cfg.pos_viewer)

        if(debug):
            #time to get frame
            get_time("process time", start_time)
        
        # get one frame of the camera
        frame = mc.read(cfg.camera, cfg.cam_scale)

        if(debug):
            #time to get frame
            get_time("frame time", start_time)
            
            print("")
            # get start time
            start_time = datetime.datetime.now()
        
        # Convert the frame
        # BGR(RGB color space) to 
        # lab(hue-saturation-value)
        lab_frame = cv2.cvtColor(frame, cfg.color_space)
        
        # create masks for each color, and check rotation of the masks
        for i, name in enumerate(cfg.color_name_table):
            #creates a color mask
            cfg.color_mask_table[i] = mf.create_bit_mask_for_color(cfg.kernal, lab_frame, cfg.lab_min_max_table[i], cfg.erode_dilate, cfg.erode_dilate+1, cfg.mask_scale_rotation)
            if (i):
                color_mask_combine = cv2.bitwise_or(color_mask_combine, cfg.color_mask_table[i])
            else:
                color_mask_combine = cfg.color_mask_table[i]
        
        #color_mask_combine = cv2.dilate(color_mask_combine, kernal, iterations=1)
        #color_mask_combine = cv2.erode(color_mask_combine, kernal, iterations=2)
        contours_combined = mf.create_contour(color_mask_combine, cfg.block_small_area*cfg.mask_scale_rotation, method=cv2.CHAIN_APPROX_NONE)
        
        #time to get contour
        #get_time(start_time)
        
        if(contours_combined):
            workspace = mw.create_workspace(frame, window_vision, contours_combined, cfg.workspace_width, cfg.workspace_height, debug, cfg.mask_scale_rotation)
            work_frame = mw.transform_workspace(frame, workspace, cfg.workspace_width, cfg.workspace_height)
            lab_frame = cv2.cvtColor(work_frame, cfg.color_space)
            
            # time to get workplace
            #get_time(start_time)
            
            #cv.drawContours(frame, contours, 3, (0,255,0), 3)
            # after rotated make contours of the mask
            
            # loop through all the colors and make for each color an mask and contours
            for i, name in enumerate(cfg.color_name_table):
                #creates a color mask
                cfg.color_mask_table[i] = mf.create_bit_mask_for_color(cfg.kernal, lab_frame, cfg.lab_min_max_table[i], cfg.erode_dilate, cfg.erode_dilate+1)
                
                # creates contours of the created mask
                # contour = create_contour(color_mask_table[i])
                cfg.color_contour_table[i] = mf.create_contour(cfg.color_mask_table[i], cfg.block_small_area)
                
                # loop trough all contours
                for contour in cfg.color_contour_table[i]:
                    if(debug):
                        mf.draw_contour(work_frame, contour, cfg.color_bgr_table[i], debug)
                    mf.split_contour_on_height(cfg.color_mask_table[i], contour, cfg.block_height, cfg.block_height_offset, cfg.block_split_cut_size)
                
                
                # erode to remove little white noise
                cfg.color_mask_table[i] = cv2.erode(cfg.color_mask_table[i], cfg.kernal, iterations= 6)
                # dilate to increase back to original size
                cfg.color_mask_table[i] = cv2.dilate(cfg.color_mask_table[i], cfg.kernal, iterations= 4)
                
                cfg.color_contour_table[i] = mf.create_contour(cfg.color_mask_table[i], cfg.block_small_area)
                for contour in cfg.color_contour_table[i]:
                    if(not debug):
                        mf.draw_contour(work_frame, contour, cfg.color_bgr_table[i], debug)
                
                # show the cut up frame

                # write color channel text to display
                cv2.putText(cfg.color_mask_table[i], name, (10,20),
                            cfg.font, 1,
                            (255, 255, 255))
                cv2.putText(cfg.color_mask_table[i], str(cfg.lab_min_max_table[i][0]), (10,45),
                            cfg.font, 0.5,
                            (255, 255, 255))
                cv2.putText(cfg.color_mask_table[i], str(cfg.lab_min_max_table[i][1]), (10,60),
                            cfg.font, 0.5,
                            (255, 255, 255))
            
            # time to get all colors
            #get_time(start_time)
            
            # combine all the colors for sorting
            all_contours = cfg.color_contour_table[0] + cfg.color_contour_table[1] + cfg.color_contour_table[2] + cfg.color_contour_table[3]
            
            # fill a color array to remember the size and color of each contour
            all_colors = []
            for i, name in enumerate(cfg.color_name_table):
               mf.block_color_fill(all_colors, cfg.color_contour_table[i], i, cfg.block_width_big)

            # sort all blocks from bottom-top and print
            contours,colors = mf.sort_contours_on_height(all_contours,all_colors)
            
            all_pos = mf.create_block_pos_array(work_frame, contours, mid_pos, cfg.block_width_big/4)

            color_pos = np.stack((colors, all_pos), axis=1)
                    
            # in debug mode: show the mask frames of each color
            if(debug):
                cv2.imshow("color_mask_combine", color_mask_combine)
                
            four_filters = mc.four_in_one_frame(cfg.color_mask_table, 0.8)
            #cv2.imshow("rybg_frame", four_filters)
            #four_filters = cv2.cvtColor(four_filters,cv2.COLOR_GRAY2RGB)
            mf.overlay_image(window_vision, four_filters, cfg.pos_four_filters)
            # resize workframe
            width = int(work_frame.shape[1] * 3)
            height = int(work_frame.shape[0] * 3)
            dim = (width, height)
            work_frame = cv2.resize(work_frame, dim, interpolation = cv2.INTER_AREA)
            mf.overlay_image(window_vision, work_frame, cfg.pos_corrected_image)
              
        # create raw image and recipe overlays
        mf.overlay_image(window_vision, frame, cfg.pos_raw_image)
        rr_frame, progress = mrr.draw_recept_result(current_product, color_pos, 0)
        mf.overlay_image(window_vision, rr_frame, cfg.pos_recept_result)
        
        # quick debug to show variables
        test_var = len(buffer_product)
        cv2.putText(window_vision, str(test_var), (10,10), cfg.font, 0.5, (255, 255, 255))
        
        if(progress == 1):
            completed_flag = 1

        if(completed_flag):
            # draw completed mark on screen
            cv2.putText(window_vision, '>>', (30,900), cfg.font, 40, (0, 200, 0), 80)

            # go to next product
            if(progress == 0 and not len(color_pos)):
                current_product = []
                # no product? clear viewer
                mx.xml_generate(())
                completed_flag = 0
        
        # show normal view + bounding boxes    
        #cv2.imshow("Video", frame)
        #cv2.imshow("Raw Frame", work_frame)
        #cv2.imshow("rr", rr_frame)
        
        #get_time(start_time)

        cv2.putText(window_vision, "ESC = Exit ; SPACE = Calibration", mf.pos_shift(cfg.pos_viewer,(10, 0)),
                        cfg.font, 1, (255,255,255))   
        cv2.imshow("window vision", window_vision)
        
        key = cv2.waitKey(10) & 0xFF 
        # check esc to exit
        if key == 27:
            mc.close(cfg.camera)
            cv2.destroyAllWindows()
            mdw.OBS_close(OBS_window)
            exit()
        # reload config on spacebar
        if key == ord(' '):
            break
        # check d key to toggle debug mode
        if key == ord('d'):
            if(debug):
                cv2.destroyWindow("rybg_frame")
                cv2.destroyWindow("color_mask_combine")
            debug = not debug
        if key == ord('-'):
            mid_pos += 1
        if key == ord('='):
            mid_pos -= 1
        if key == ord('x'):
            current_product = []
            completed_flag = 0

    """ ----- ----- ----- """

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