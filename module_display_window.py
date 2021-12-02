"""
Functions to read a open window
Used to open the Viewer Portal

Using:
OBS
OBS virtual cam filter
https://obsproject.com/forum/resources/obs-virtualcam.949/
OBS settings
Filter:
    crop:
        left:   580
        right:  1700
        up:     580
        down:   1200
"""

""" ----- IMPORTS ----- """
import cv2

cam_index = 0
size = (668,974)

def OBS_open(i):
    global cam_index
    cam_index = i
    cap = cv2.VideoCapture(i)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
    if not cap.isOpened():
        print("Cannot open camera")
    return cap

def OBS_frame(cap, scale= 1):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True  
    
    # rescaling image
    return frame

def OBS_close(cap):
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def check_multiple():
    for i in range(2,10):
        try:
            print('checking camera',i)
            OBS_window = OBS_open(i)
            while(1):
                frame = OBS_frame(OBS_window)
                cv2.imshow("window", frame)
                if cv2.waitKey(1) == ord('q'):
                    break
            OBS_close(OBS_window)
        except:
            continue

#check_multiple() # 2 is index of OBS Virtual Camera , 0 is index of OBS-Camera

'''
OBS_window = OBS_open(2)
while(1):
    OBS_frame(OBS_window)
    if cv2.waitKey(1) == ord('q'):
        break
OBS_close(OBS_window)
'''