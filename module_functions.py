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
    line_width = 2  # change if resolution changes
    # draw square
    cv2.rectangle(image, (x, y), (x + w, y + h), color, line_width)
    # write text above square
    cv2.putText(image, text, (x, y - 2 * line_width),
                cv2.FONT_HERSHEY_SIMPLEX, line_width/4, 
                color)  

def min_max_calculate(value, offset):
    """
    :brief      Finds the min and max value of an array and corrects with the offset
    :param      value:      Array of values that will be checked
    :param      offset:     Amount the real values will be changed
    :return     minimum,    maximum
    """
    min_value = np.amin(value) - offset
    max_value = np.amax(value) + offset
    return [min_value, max_value]

def lab_min_max_calculate(image, color_space, offset_table):
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
    l_min, l_max = min_max_calculate(l, offset_table[0])
    # a
    a_min, a_max = min_max_calculate(a, offset_table[1])
    # b
    b_min, b_max = min_max_calculate(b, offset_table[2])
    
    return[[l_min, a_min, b_min],[l_max, a_max, b_max]] 

def lab_save(color_index, lab_min, lab_max, min_max_table):
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
def mask_color(kernal, image, min_max_array, scale=1):
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
    color_mask = cv2.erode(color_mask, kernal, iterations=2)
    # dilate to increase back to original size
    color_mask = cv2.dilate(color_mask, kernal, iterations=4)
    
    # rescale image for the mask
    width = int(color_mask.shape[1] * scale)
    height = int(color_mask.shape[0] * scale)
    dim = (width, height)

    # inerpolation default = cv2.INTER_AREA
    return cv2.resize(color_mask, dim, interpolation = cv2.INTER_NEAREST)

    
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

def split_contour(image, contour, height, offset):
    """
    :brief      Spits contours that are too high
    :param      image:      Image to draw lines on to split
    :param      contour:    Array of contours in the image
    :param      height:     Maximum height of a contour
    :param      offset:     Offset the height can be
    """
    x, y, w, h = cv2.boundingRect(contour)
    stack_height = int(round((h - offset)/height))
    for index in range(1, stack_height):
        left_cut = np.array([x, y + (h*(index/float(stack_height)))], dtype='int')
        right_cut = np.array([x + w, y + (h*(index/float(stack_height)))], dtype='int')
        cv2.line(image, tuple(left_cut), tuple(right_cut), (0, 0, 0), 3)
        #print("cutting" + str(index) + "    pos: " + str(left_cut) + ":" + str(right_cut))
        #print(str(stack_height) + "    num: " + str(index/float(stack_height)))
            
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

"""----- ----- WORKSPACE ----- -----"""
def get_workspace(image, contours, width, height, offset, debug, scale=1):
    """
    :brief      Makes a workspace centred on the biggest contour
    :param      image:      Image to draw on in debug mode
    :param      contours:   Array of contours in the image
    :param      width:      Width of the workspace
    :param      height:     Height of the workspace
    :param      offset:     How big the search window is for the angle
    :param      debug:      If debug info should be shown
    :param      scale:      Factor to scale the image, 1 = normal
    :return     Four points of the designated workspace
    """
    width /= 2
    height /= 2
    
    scale = int(1/scale)
    if(contours):
        # find biggest contour to work with
        big_contour = max(contours, key=cv2.contourArea)
        
        #find lowset point
        ext_index = big_contour[:, :, 1].argmax()
        ext_bottom = tuple(big_contour[ext_index][0])
        
        # find left and right points that are close to the bottom
        most_left = ext_index
        most_right = ext_index
        for i, y in enumerate (big_contour[:, :, 1]):
            x = big_contour[:, :, 0][i]
            if((x < ext_bottom[0] + offset and x > ext_bottom[0] - offset*2)
            and (y < ext_bottom[1] + offset and y > ext_bottom[1] - offset)):
                # more right
                if(x > big_contour[most_left][0][0]):
                    most_right = i
                # more left
                if(x < big_contour[most_left][0][0]):
                    most_left = i
            
        ext_left = tuple(big_contour[most_left][0])
        ext_right = tuple(big_contour[most_right][0])
        
        # calculate angle of bottom to left and bottom to right
        angle_r = angle_between(ext_bottom, ext_right)
        angle_l = angle_between(ext_bottom, ext_left) -3.1415
        
        if(abs(angle_l) > abs(angle_r)):
            angle = angle_r
        else:
            angle = angle_l
        #angle, idx = min([(abs(val), idx) for (idx, val) in enumerate([angle_r, angle_l])])
                        
        # create corner points of the workspace
        mid = cv2.moments(big_contour)
        if((mid['m00']) == 0):
            cx = 0
            cy = 0
        else:
            cx = int(mid['m10']/mid['m00'])
            cy = int(mid['m01']/mid['m00'])
            
        box = [[],[],[],[]]
        midleft = [int(cx - (width * np.cos(angle))), int(cy + (width * np.sin(angle)))]        # left
        midright = [int(cx + (width * np.cos(angle))), int(cy - (width * np.sin(angle)))]        # right
        
        box[0] = [int(midleft[0] - (height * np.sin(angle)))*scale, int(midleft[1] - (height * np.cos(angle)))*scale]        # topleft
        box[1] = [int(midright[0] - (height * np.sin(angle)))*scale, int(midright[1] - (height * np.cos(angle)))*scale]        # topright
        box[2] = [int(midright[0] + (height * np.sin(angle)))*scale, int(midright[1] + (height * np.cos(angle)))*scale]        # bottomright
        box[3] = [int(midleft[0] + (height * np.sin(angle)))*scale, int(midleft[1] + (height * np.cos(angle)))*scale]        # bottomleft
        
        if((angle_r - angle_l)>1.5 or (angle_r - angle_l)<-1.64):
            cv2.putText(image, "good", (40,100),
                        font, 1,
                        (0, 0, 255))   
        
        if(debug):
            # draw lowest, left and right points
            cv2.circle(image, tuple(np.array(ext_bottom)*scale), 4, (255,255,255), -1)
            cv2.circle(image, tuple(np.array(ext_left)*scale), 4, (255,0,0), -1)
            cv2.circle(image, tuple(np.array(ext_right)*scale), 4, (0,0,255), -1)
            
            # write radiant angle of the workspace
            cv2.putText(image, "R: " + str(angle_r), (20,180),
                        font, 1,
                        (255, 255, 255))
            cv2.putText(image, "L: " + str(angle_l), (20,250),
                        font, 1,
                        (255, 255, 255))
            cv2.putText(image, "b0: " + str(box[0]), (20,300),
                        font, 1,
                        (255, 255, 255))
                        
            
            # draw corners of workspace
            cv2.circle(image, tuple(box[0]), 4, (0,0,255), -1)
            cv2.circle(image, tuple(box[1]), 4, (0,255,0), -1)
            cv2.circle(image, tuple(box[2]), 4, (255,0,0), -1)
            cv2.circle(image, tuple(box[3]), 4, (255,0,255), -1)
        
        return np.array(box)

def transform(image, workspace, width, height):
    """
    :brief      Rotates and resizes an section off the image
    :param      image:      Original image where the workspace is in
    :param      workspace:  Four points of the workspace
    :param      width:      Width of the new image
    :param      height:     Height of the new image
    :return     New image that has been transformed and warped
    """
    h = np.float32( [[0, 0],
                    [width - 1, 0],
                    [width - 1, height - 1],
                    [0, height - 1]])
    m = cv2.getPerspectiveTransform(workspace.astype(np.float32),h)
    return cv2.warpPerspective(image,m,(width, height))
    
def angle_between(p1, p2):
    """
    :brief      Calculates smallest angle between two points, always under 180
    :param      p1:     Point 1 of the line
    :param      p2:     Point 2 of the line
    :return     Angle of that line relative to the horizon
    """
    angle = np.arctan2(p1[1] - p2[1], p2[0] - p1[0])
    return angle

""" ----- ----- COUNTING ----- ----- """
def sort_contours(cnts, clr):
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
    """
    for i in range(0,len(cnt_array)):
        x, y, w, h = cv2.boundingRect(cnt_array[i])
        # magic numbers used to convert color index to block type
        if(w > block_width):
            fill_array.append(color_index + 5)
        else:
            fill_array.append(color_index + 1)

""" ----- ----- ----- """