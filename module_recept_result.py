"""
Module to draw the recept and result colom
"""

""" ----- IMPORTS ----- """
import config as cfg
import cv2
import numpy as np
""" ----- ----- ----- """

def draw_recept_result(recept_array, result_array, background):
    """
    :brief      Creates a image that shows the recept and result array, when they are the same a background will display that
    :param      recept_array:   Array of the recipe to build, in the format: [[block1,pos1],[block2,pos2],..]
    :param      result_array:   Array of the result that is build, in the format: [[block1,pos1],[block2,pos2],..]
    :return     two values: An image where the arrays and background are displayed on, percentage completed
    """
    if(background):
        window_recept_result = np.full(cfg.window_size, (0,50,0), np.uint8)
    else:
        window_recept_result = np.zeros(cfg.window_size, np.uint8)
    
    total = 0
    progress = 0
    if(len(result_array) <= 8):
        total = draw_background(window_recept_result, recept_array, result_array)
        draw_array_vertical(window_recept_result, result_array, cfg.colom2, "result:")
    draw_array_vertical(window_recept_result, recept_array, cfg.colom1, "recept:")

    if(len(recept_array)):
        progress = total/float(len(recept_array))
    
    return [window_recept_result, progress]

def draw_array_vertical(image, array, colom_pos, sub_text):
    """
    :brief      Draws an array on an image in the vertial axis, from bottom to top
    :param      array:      Array to be drawn
    :param      image:      Image to be drawn on
    :param      colom_pos:  Position of the array in the x-axis
    :param      sub_text:   Text that is drawn below the array
    """
    cv2.putText(image, sub_text, (colom_pos + 5,cfg.window_size[0] - 30),
                            cfg.font, cfg.font_size_rr*0.8,
                            (255, 255, 255))
    for i,item in enumerate(array):
        #item = np.array(item, "uint8")
        cv2.putText(image, str(item), (colom_pos,cfg.window_size[0] - cfg.spacing*(i + 1)),
                            cfg.font, cfg.font_size_rr,
                            (255, 255, 255))

def draw_background(image, inputarray1, inputarray2):
    """
    :brief      Draws an background depending on the values of both inputs
    :param      input1:     Input to be compared with the other input
    :param      input2:     Input to be compared with the other input 
    :param      colom:      Position of the background
    :return     amount of green rectangles
    """
    total = 0
    max_i, dif = calc_max_common(inputarray1, inputarray2)
    for i in range(max_i + dif):
        start = (0, cfg.window_size[0] - int(cfg.spacing*(i + 0.8)))
        end = (cfg.window_size[1], cfg.window_size[0] - int(cfg.spacing*(i + 1.5)))
        if(i < max_i):
            if(np.array_equal(inputarray1[i],inputarray2[i])):
                cv2.rectangle(image, start, end, (0,64,0), -1)  # green
                total += 1
            else:
                cv2.rectangle(image, start, end, (0,0,64), -1)  # red
        else:
            cv2.rectangle(image, start, end, (0,32,64), -1)     # orange
    
    return total
    
def calc_max_common(array1, array2):
    """
    :brief      Calculates the max length that both arrays can have
    :param      array1:     Array to compare
    :param      array2:     Array to compare
    :return     two values: maximum common length, difference between the arrays
    """
    length_1 = len(array1)
    length_2 = len(array2)
    max_common = 0
    difference = 0
    if(length_1 > length_2):
        max_common = length_2
        difference = length_1 - length_2
    else:
        max_common = length_1
        difference = length_2 - length_1
    return [max_common, difference]
    
    
    
    

