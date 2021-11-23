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
        
        angle = find_contour_angle(big_contour, offset*2, offset, image, scale, debug)

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
       
        
        if(debug):
            cv2.putText(debug_image, "b0: " + str(box[0]), (20,300),
                        font, 1,
                        (255, 255, 255))
                        
            
            # draw corners of workspace
            cv2.circle(image, tuple(box[0]), 4, (0,0,255), -1)
            cv2.circle(image, tuple(box[1]), 4, (0,255,0), -1)
            cv2.circle(image, tuple(box[2]), 4, (255,0,0), -1)
            cv2.circle(image, tuple(box[3]), 4, (255,0,255), -1)
        
        return np.array(box)

def find_contour_angle(contour, image, scale, debug, points_skip= 6, points_group= 6):
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

    # find two points to for the line angle
    bot_right, ext_right = points_avg(contour, points_skip, points_group)
    bot_left, ext_left = points_avg(contour, points_skip, points_group)

    # calculate angle of bottom to left and bottom to right
    angle_r = find_angle_between(bot_right, ext_right)
    angle_l = find_angle_between(bot_left, ext_left) -3.1415
    
    # draw lowest, left and right points
    cv2.line(image, tuple(np.array(bot_left)*scale), tuple(np.array(ext_left)*scale), (128,0,255), 3)
    cv2.line(image, tuple(np.array(bot_right)*scale), tuple(np.array(ext_right)*scale), (255,0,128), 3)
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
        return angle_r
    else:
        return angle_l

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


def points_avg(cnt, skip, group):
    """
    :brief      Calculates avg start and end point for the angle calculation
    :param      cnt:    Contour to find point for
    :param      skip:   Error margin of the lowest point
    :param      group:  How many points a group consists of
    :return     Avg position of two points ((x,y),(x,y))
    """
    #find lowset point
    ext = cnt[:, :, 1].argmax()

    p1 = ext + skip
    p2 = p1 + group
    p3 = p2 + group

    #swap p1 and p3 so p1 is the smallest
    if(p1 > p3):
        t1 = p1
        p1 = p3
        p3 = t1
    
    start = tuple(cnt[p1:p2][0])
    end = tuple(cnt[p2:p3][0])

    x, y = np.split(start,[-1],axis=1)
    start = (np.average(x),np.average(y))
    x, y = np.split(end,[-1],axis=1)
    end = (np.average(x),np.average(y))
    return (start,end)

'''
def difference(x,y):
    if x >= y:
        return x-y
    else:
        return y-x
'''