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

"""----- ----- WORKSPACE ----- -----"""
def create_workspace(image, debug_image, contours, width, height, offset, debug, scale=1):
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
    scale = int(1/scale)
    offset /= scale
    width /= scale*2
    height /= scale*2
    
    if(contours):
        # find biggest contour to work with
        big_contour = max(contours, key=cv2.contourArea)
        centre,(w, h), rotation = cv2.minAreaRect(big_contour)
        
        angle, pos_lowest = find_contour_angle(big_contour, image, scale, debug)

        #angle, idx = min([(abs(val), idx) for (idx, val) in enumerate([angle_r, angle_l])])
                                    
        box = [[],[],[],[]]
        midleft = [int(centre[0] - (width * np.cos(angle))), int(centre[1] + (width * np.sin(angle)))]         # left
        midright = [int(centre[0] + (width * np.cos(angle))), int(centre[1] - (width * np.sin(angle)))]        # right
        
        box[0] = [int(midleft[0] - (height * np.sin(angle)))*scale, int(midleft[1] - (height * np.cos(angle)))*scale]        # topleft
        box[1] = [int(midright[0] - (height * np.sin(angle)))*scale, int(midright[1] - (height * np.cos(angle)))*scale]      # topright
        box[2] = [int(midright[0] + (height * np.sin(angle)))*scale, int(midright[1] + (height * np.cos(angle)))*scale]      # bottomright
        box[3] = [int(midleft[0] + (height * np.sin(angle)))*scale, int(midleft[1] + (height * np.cos(angle)))*scale]        # bottomleft
        
        box = np.int0(box)
        cv2.drawContours(image,[box], 0, (255,255,255), 1)
       
        
        if(debug):
            cv2.putText(debug_image, "b0: " + str(box[0]), (20,300),
                        font, 1,
                        (255, 255, 255))
            cv2.putText(debug_image, "roatation: " + str(rotation), (20,400),
                        font, 1,
                        (255, 255, 255))
        
        return np.array(box)

def find_contour_angle(contour, image, scale, debug, points_group= 9):
    """
    :brief      Returns the angle of a contour
    :param      contour:        Contour with no approx
    :param      imgate:         Image to draw angle lines on
    :param      scale:          Scale that the contour has been scaled by
    :param      debug:          If debug mode is active
    :param      start_index:    Search area width
    :param      end_index:      Search area height
    :return     The closest angle to make te contour flat
    """
    #find lowset point
    ext_left = contour[:, :, 1].argmax()
    ext_right = contour_same_height_point(contour, ext_left)
   
    left_points = contour[ext_left - points_group : ext_left]
    right_points = contour[ext_right : ext_right + points_group]
    left_points = contour_to_points(left_points)
    right_points = contour_to_points(right_points)
    
    # find two points to for the line angle
    right1,right2 = points_avg(contour, ext_right, points_group)
    left1,left2 = points_avg(contour, ext_left, -points_group)
    
    # calculate angle of bottom to left and bottom to right
    angle_r = find_angle_between(right1, right2)
    angle_l = find_angle_between(left1, left2)
    
    right1 = np.int0(right1)
    right2 = np.int0(right2)
    left1 = np.int0(left1)
    left2 = np.int0(left2)
   
    # draw lowest, left and right points
    cv2.line(image, tuple(np.array(left1)*scale), tuple(np.array(left2)*scale), (128,0,255), 3)
    cv2.line(image, tuple(np.array(right1)*scale), tuple(np.array(right2)*scale), (255,0,128), 3)
    if(debug):
        
        # write radiant angle of the workspace
        cv2.putText(image, "R: " + str(angle_r), (20,180),
                    font, 1,
                    (255, 255, 255))
        cv2.putText(image, "L: " + str(angle_l), (20,250),
                    font, 1,
                    (255, 255, 255))
    
    # return the smallest angle
    if((abs(angle_l) > abs(angle_r))):
        return (angle_r,contour[ext_right][0])
    else:
        return (angle_l,contour[ext_left][0])

def transform_workspace(image, workspace, width, height):
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
    
def find_angle_between(p1, p2):
    """
    :brief      Calculates smallest angle between two points, always under 180
    :param      p1:     Point 1 of the line
    :param      p2:     Point 2 of the line
    :return     Angle of that line relative to the horizon
    """
    angle = np.arctan2(p1[1] - p2[1], p2[0] - p1[0])
    return angle

def contour_same_height_point(cnt, low_i):
    cur_y= cnt[low_i][0][1]
    most_right = low_i
    for i in range(low_i, low_i + 20):
        most_right = i
        if not (cnt[i][0][1] == cur_y):
            return most_right
    return low_i
    
def points_avg(cnt, ext, group):
    """
    :brief      Calculates avg start and end point for the angle calculation
    :param      cnt:    Contour to find point for
    :param      ext:    Lowest point index in the contour:    ext = contour[:, :, 1].argmax()
    :param      skip:   Error margin of the lowest point
    :param      group:  How many points a group consists of
    :return     Avg position of two points ((x,y),(x,y))
    """

    p1 = ext
    p2 = p1 + group
    p3 = p2 + group

    #swap p1,p3 so p1 is the smallest
    if(p1 > p3):
        temp = p1
        p1 = p3
        p3 = temp
    
    avg1 = points_to_avg(cnt[p1:p2])
    avg2 = points_to_avg(cnt[p2:p3])
    
    return (avg1,avg2)

def contour_to_points(cnt):
    """
    :brief      From array (((x,y)),((x,y)),..) to avg ((x,y),(x,y),..)
    :param      cnt:    Array of points
    :return     Positions of each contour point
    """
    pos = []
    for i, item in enumerate(cnt):
        pos.append(item[0])
    return (pos)


def points_to_avg(points):
    """
    :brief      From array ((x,y),(x,y),..) to avg (x,y)
    :param      points:  Array of points
    :return     Avg position of two points ((x,y),(x,y))
    """
    x = []
    y = []
    for i, item in enumerate(points):
        x.append(item[0][0])
        y.append(item[0][1])
    return (np.average(x),np.average(y))

    
'''
def difference(x,y):
    if x >= y:
        return x-y
    else:
        return y-x
'''