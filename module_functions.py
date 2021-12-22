"""
Functions used for the WSI vision module
- calibration
- mask
- contours
- workspace
"""

""" ----- IMPORTS ----- """
import numpy as np
import cv2

font = cv2.FONT_HERSHEY_SIMPLEX
""" ----- ----- ----- """

""" ----- FUNCTION ----- """
""" ----- ----- CALIBRATION ----- ----- """
def draw_calibration_box(image, x, y, w, h, text, color):
    """
    :brief      Draw square in the middle of the screen with text
    :param      image:  image that will be drawn on
    :param      x:      X position offset
    :param      y:      Y possition offset
    :param      w:      Width of the square
    :param      h:      Height of the square
    :param      text:   Text above the square
    :param      color:  Color of the text and square
    """
    line_width = 6  # change if resolution changes
    # draw white outline
    cv2.rectangle(image, (x - line_width, y - line_width), (x + w  + line_width, y + h + line_width), (255,255,255), line_width)
    # draw coloured inside
    cv2.rectangle(image, (x, y), (x + w, y + h), color, line_width)
    # write text above square
    cv2.putText(image, text, (x, y - 4 * line_width),
                cv2.FONT_HERSHEY_SIMPLEX, line_width/4, 
                color,2)  

def find_min_max_array(value, offset=0):
    """
    :brief      Finds the min and max value of an array and corrects with the offset
    :param      value:      Array of values that will be checked
    :param      offset:     Amount the real values will be changed, default = 0
    :return     minimum,    maximum
    """
    min_value = np.amin(value) - offset
    max_value = np.amax(value) + offset
    return [min_value, max_value]

def find_min_max_color(image, color_space, offset_table):
    """
    :brief      Finds the min and max value of an image
    :param      image:          Array of values that will be checked
    :param      color_space:    Color space the image will be transformed to
    :param      offset_table:   Amount the first second and third values will be changed [l,a,b]
    :return     minimum array,  maximum array (size = 3)
    """
    #convert image to lab and split those values
    lab_image = cv2.cvtColor(image, color_space)
    l, a, b = cv2.split(lab_image)
    
    # lum
    l_min, l_max = find_min_max_array(l, offset_table[0])
    # a
    a_min, a_max = find_min_max_array(a, offset_table[1])
    # b
    b_min, b_max = find_min_max_array(b, offset_table[2])
    
    return[[l_min, a_min, b_min],[l_max, a_max, b_max]] 

def save_min_max_color(color_index, lab_min, lab_max, min_max_table):
    """
    :brief      Save the lab values for a specific color
    :param      color_index:    Color to save
    :param      lab_min:        Minimum values to save [l,a,b]
    :param      lab_max:        Maximum values to save [l,a,b]
    :param      min_max_table,  Array to save the values in
    """
    min_max_table[color_index][0] = lab_min
    min_max_table[color_index][1] = lab_max

""" ----- ----- COLOR MASK ----- ----- """
def create_bit_mask_for_color(kernal, image, min_max_array, erode, dilate, scale=1):
    """
    :brief      creates a mask for one color
    :param      kernal:         kernal used for dilation/erosion
    :param      image:          image to find the mask
    :param      min_max_array:  Min and max values [[l,a,b],[l,a,b]]
    :param      scale:          Factor to scale the image, 1 = normal
    :return     bit mask of the image where the lab values are within the min and max
    """
    # split into min and max values
    bound_lower = np.array(min_max_array[0])
    bound_upper = np.array(min_max_array[1])    
    
    # morphological transform
    # creates mask for specific color range
    # color_mask = cv2.inRange(image, bound_lower, bound_upper)
    color_mask = cv2.inRange(image, bound_lower, bound_upper)
    
    # erode to remove little white noise
    color_mask = cv2.erode(color_mask, kernal, iterations= erode)
    # dilate to increase back to original size
    color_mask = cv2.dilate(color_mask, kernal, iterations= dilate)
    
    # rescale image for the mask
    width = int(color_mask.shape[1] * scale)
    height = int(color_mask.shape[0] * scale)
    dim = (width, height)

    # inerpolation default = cv2.INTER_AREA
    return cv2.resize(color_mask, dim, interpolation = cv2.INTER_LINEAR)

    
""" ----- ----- CONTOURS ----- ----- """
def create_contour(image, min_area, method=cv2.CHAIN_APPROX_SIMPLE):
    """
    :brief      Creates contour array from an image
    :param      mask:       Image to use
    :param      min_area:   Minimum area a contour can be
    :param      method:     Method used to make the contour (SIMPLE, NONE)
    :return     Array of contours in the image
    """
    # creating contour array
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, method)
    # remove all coutnours that are too small
    i = 0
    while (i < len(contours)):
        area = int(cv2.contourArea(contours[i]))
        if(area < min_area):
            contours.pop(i)
        else:
            i += 1

    return contours

def split_contour_on_height(image, contour, height, offset, cut_size):
    """
    :brief      Splits contours that are too high
    :param      image:      Image to draw lines on to split
    :param      contour:    Array of contours in the image
    :param      height:     Maximum height of a contour
    :param      offset:     Offset the height can be
    """
    x, y, w, h = cv2.boundingRect(contour)
    # calculate amount of blocks: (height contour) / (height block)
    stack_height = int(h/height)
    for index in range(1, stack_height):
        new_y = (y + h) - ((height * index) + offset)
        draw_horizontal_line(image, x, new_y, w, cut_size)

def draw_horizontal_line(image, x , y, w, t):
    """
    :brief      Makes a black horizontal line on (x,y) with a width to the right
    :param      image:  Image to draw lines on
    :param      x:      X position for the left point of the line
    :param      y:      Y position for the left point of the line
    :param      w:      Width the line will be to the right
    :param      t:      Thickness of the line
    """
    cv2.line(image, (x, y), (x + w, y), (0, 0, 0), t)

def draw_contour(image, contour, color, debug):
    """
    :brief      Show contours on the main display
    :param      image:      Image to draw on
    :param      contour:    Array of contours to draw on the imge
    :param      color:      Color the contour should be
    :param      debug:      If debug info should be shown
    """
    # calculate area of the contour
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
    mid_x = int(x + 0.5*w)
    mid_y = int(y + 0.5*h)

    # write info on screen in debug mode (widht, height)
    if(debug):
        area = int(cv2.contourArea(contour))
        cv2.putText(image, "A: " + str(area), (mid_x - 20, mid_y - 6),
                    font, 0.3,
                    (255,255,255))
        cv2.putText(image, "W: " + str(w), (mid_x - 20, mid_y + 4),
                    font, 0.3,
                    (255,255,255))
        cv2.putText(image, "H: " + str(h), (mid_x - 20, mid_y + 14),
                    font, 0.3,
                    (255,255,255))

""" ----- ----- COUNTING ----- ----- """
def sort_contours_on_height(cnts, clr):
    """
    :brief      Sort a contour array in the Y-axis
    :param      cnts:   Array of contours to be sorted
    :param      clr:   Array of colors to be sorted in the same way as the contours
    :return     Both arrays (contours, colors)
    """
    if(len(cnts) > 0):
        # initialize the reverse flag and sort index
        reverse = True
        # use 0 to sort for x coordinate else 1 for y
        i = 1
        # construct the list of bounding boxes and sort them from top to
        # bottom
        boundingBoxes = [cv2.boundingRect(c) for c in cnts]
        (cnts, clr, boundingBoxes) = zip(*sorted(zip(cnts, clr, boundingBoxes), key=lambda b:b[2][i], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return (cnts, clr) 

# fills an array with the size of an other array
# cnt_array = [1,2,3,4,5] with color_index = 1
# fill_array = [2,2,2,2,2]
def block_color_fill(fill_array, cnt_array, color_index, block_width):
    """
    :brief      Fills an array with the size of an other array
    :param      fill_array:     Array to fill with numbers
    :param      cnt_array:      Array of contours to get the width from
    :param      color_index:    Type of color to fill the array with
    :param      block_width:    Width of a big block to check against

    Examples:
        fill_array = []

        block_color_fill(cnt_array = [1,2,3,4,5], color_index = 1)
        fill_array = [2,2,2,2,2]

        block_color_fill(cnt_array = [6,7,8], color_index = 2)
        fill_array = [2,2,2,2,2,3,3,3]

        block_color_fill(cnt_array = [9,10], color_index = 0)
        fill_array = [2,2,2,2,2,3,3,3,1,1]
    """
    for i in range(0,len(cnt_array)):
        x, y, w, h = cv2.boundingRect(cnt_array[i])
        # magic numbers used to convert color index to block type
        if(w > block_width):
            fill_array.append(color_index + 5)
        else:
            fill_array.append(color_index + 1)

def create_block_pos_array(image, contours, lowest_block_pos, offset_width):
    """
    :brief      Creates an array that shows if the block is positioned in the left(1), middle(2), right(3)
    :param      image:              Image to draw the mid position on
    :param      contours:           Array of contours sorted in height
    :param      lowest_block_pos:   Position of the lowest block
    :return     An array of the position from the bottom block to the top block
    """
    all_pos = []

    # place mid line
    if(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[0])
        x = int((x + w) - ((lowest_block_pos/float(4))*w))
        y = int(y + 0.5*h)
        cv2.circle(image, (x,y), 5, (255,255,255), -1)

        compare_x = x
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            mid_x = int(x + 0.5*w)
            if (mid_x > compare_x + offset_width):    # right side
                all_pos.append(3)
            elif (mid_x < compare_x - offset_width):  # left side
                all_pos.append(1)
            else:                           # middle
                all_pos.append(2)
    return all_pos


def overlay_image(l_img, s_img, position = (0,0)):
    """
    :brief      Overlays an smaller image(s_img) over an lager image(l_img)
    :param      l_img:      The large image that is the base
    :param      s_img:      The small image that will be inserted
    :param      position:   Position of the small image
    """
    x_offset,y_offset= position
    if(s_img.ndim == 2):  # gray scale image
        s_img = cv2.cvtColor(s_img,cv2.COLOR_GRAY2RGB)
    
    l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img

def pos_shift(pos, shift_pos):
    return(pos[0] + shift_pos[0], pos[1] + shift_pos[1])
    
""" ----- ----- ----- """
