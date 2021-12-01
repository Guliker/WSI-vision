"""
Functions to read a open window
Used to open the Viewer Portal

Using:
OBS
OBS virtual cam filter
https://obsproject.com/forum/resources/obs-virtualcam.949/
"""

""" ----- IMPORTS ----- """
import cv2 as cv

cam_index = 0
pos = (0,0)
size = (600,400)

def OBS_open(i):
    global cam_index
    cam_index = i
    cap = cv.VideoCapture(i)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, size[0])
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, size[1])
    if not cap.isOpened():
        print("Cannot open camera")
    return cap

def OBS_frame(cap):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # crop image to centre
    global size
    global pos
    x,y = pos
    w,h = size
    frame_crop = frame[y:y+h, x:x+w]
    # if frame is read correctly ret is True
    cv.imshow('frame',frame_crop)
    return frame_crop

def OBS_close(cap):
    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

def check_multiple():
    for i in range(-1,10):
        try:
            print(f'checking camera #{i}')
            OBS_window = OBS_open(i)
            while(1):
                frame = OBS_frame(OBS_window)
                if cv.waitKey(1) == ord('q'):
                    break
            OBS_close(OBS_window)
        except:
            continue

#check_multiple() # 2 is index of OBS Virtual Camera , 0 is index of OBS-Camera
#check_multiple()
'''

OBS_window = OBS_open(2)
while(1):
    OBS_frame(OBS_window)
    if cv.waitKey(1) == ord('q'):
        break
OBS_close(OBS_window)
'''