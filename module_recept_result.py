"""
Module to draw the recept and result colom
"""
import cv2
import numpy as np

font = cv2.FONT_HERSHEY_SIMPLEX
size = 1
spacing = 20*size
colom1 = 0
colom2 = 200
window_size = (1000, 400,3)

""" ----- IMPORTS ----- """
def draw_recept_result(recept_array, result_array):
    """
    :brief      
    :return     
    """
    window_recept_result = np.zeros(window_size, np.uint8)

    draw_array_vertical(recept_array, window_recept_result, colom1)
    if(len(result_array) <= 8):
        draw_array_vertical(result_array, window_recept_result, colom2)

    return window_recept_result

def draw_array_vertical(array, image, colom_pos):
    """
    :brief      
    :return     
    """
    for i,item in enumerate(array):
        item = np.array(item, "uint8")
        cv2.putText(image, item, (colom_pos,50 + spacing*i),
                            font, size,
                            (255, 255, 255))
    