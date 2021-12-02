"""
Functions to read a open window
Used to open the Viewer Portal

Using:
OBS
OBS virtual cam filter
https://obsproject.com/forum/resources/obs-virtualcam.949/
"""

""" ----- IMPORTS ----- """
import cv2

cam_index = 0
pos = (200,0)
size = (200,400)

def OBS_open(i):
    global cam_index
    cam_index = i
    cap = cv2.VideoCapture(i)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
    if not cap.isOpened():
        print("Cannot open camera")
    return cap

def OBS_frame(cap, scale= 2.5):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True

    # crop image to centre
    global size
    global pos
    x,y = pos
    w,h = size
    frame_crop = frame[y:y+h, x:x+w]
    
    
    # rescaling image
    width = int(frame_crop.shape[1] * scale)
    height = int(frame_crop.shape[0] * scale)
    dim = (width, height)
    return cv2.resize(frame_crop, dim, interpolation = cv2.INTER_AREA)

def OBS_close(cap):
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def check_multiple():
    for i in range(-1,10):
        try:
            print('checking camera',i)
            OBS_window = OBS_open(i)
            while(1):
                frame = OBS_frame(OBS_window)
                if cv2.waitKey(1) == ord('q'):
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
    if cv2.waitKey(1) == ord('q'):
        break
OBS_close(OBS_window)
'''