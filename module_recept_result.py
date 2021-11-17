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

    
    for i,recept in enumerate(recept_array):
        cv2.putText(window_recept_result, recept, (colom1,50 + spacing*i),
                            font, size,
                            (255, 255, 255))
        cv2.putText(window_recept_result, result_array[i], (colom2,50 + spacing*i),
                            font, size,
                            (255, 255, 255))
    return window_recept_result


