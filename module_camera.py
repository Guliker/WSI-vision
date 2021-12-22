"""
Used to get each frame from 'Daheng Imaging' type camera's
This code has only been tested with the MER2-630-60U3C

API used from Daheng imaging SDK:
Download path: https://www.get-cameras.com/customerdownloads?submissionGuid=3d8fbd3b-0ca4-4de2-b947-2480dd706c29
API can only be used to Python 3.5
"""

""" ----- IMPORTS ----- """
import config as cfg
import gxipy as gx
import numpy as np
import cv2
""" ----- ----- ----- """

def init(cam, dev):
    """
    :brief      Starting the camera with all the right settings
    :param      cam:        Camera Device
    :param      dev:        Device Manager
    """
    # create a device manager
    dev_num, dev_info_list = dev.update_device_list()
    if dev_num == 0:
        print("Number of enumerated devices is 0")
        return

    # exit when the camera is a mono camera
    if cam.PixelColorFilter.is_implemented() is False:
        print("This sample does not support mono camera.")
        cam.close_device()
        return

    config(cam, cfg.cam_exposure, cfg.cam_resolution, cfg.cam_offset_resolution, cfg.cam_frame_rate, cfg.cam_gain, cfg.cam_gain_rgb)

    # start data acquisition
    cam.stream_on()


def auto_calibrate(cam):
    """
    :brief      Automatically sets the exposure and white balance
    :param      cam:        Camera Device
    """
    cam.ExposureAuto.set(gx.GxAutoEntry.ONCE)
    cam.BalanceWhiteAuto.set(gx.GxAutoEntry.ONCE)
    
def check_auto_calibrate(cam):
    """
    :brief      Prints the values that have been set by auto_calibrate(cam)
    :param      cam:        Camera Device
    """
    exp = str(cam.ExposureTime.get())
    
    cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.RED)
    r = str(cam.BalanceRatio.get())
    cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.GREEN)
    g = str(cam.BalanceRatio.get())
    cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.BLUE)
    b = str(cam.BalanceRatio.get())
    print("----- camera:")
    print("e: " + exp)
    print("r: " + r)
    print("g: " + g)
    print("b: " + b)
    
def config(cam,exp, res, res_o, fps, gain, gain_rgb):
    """
    :brief      Changing settings of the camera
    :param      cam:        Camera Device
    :param      dev:        Device Manager
    :param      exp:        Exposure
    :param      res:        Resolution (width, height)
    :param      res_o:      Resolution offset (x, y)
    :param      fps:        Framerate
    :param      gain:       Gain all channels
    :param      gain_rgb:   Gain for each channel (red, green, blue)
    """
    # set default values
    cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
    #cam.ExposureTime.set(exp)
    # reset offsets
    cam.OffsetX.set(0)
    cam.OffsetY.set(0)
    # set resolution of camera
    cam.Width.set(res[0])
    cam.Height.set(res[1])
    cam.OffsetX.set(res_o[0])
    cam.OffsetY.set(res_o[1])
    # set frame rate of the camera
    cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)
    cam.AcquisitionFrameRate.set(fps)
    # set gain/balance for all channels and then for red green and blue
    cam.Gain.set(gain)
    '''
    cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.RED)
    cam.BalanceRatio.set(gain_rgb[0])
    cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.GREEN)
    cam.BalanceRatio.set(gain_rgb[1])
    cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.BLUE)
    cam.BalanceRatio.set(gain_rgb[2])
    '''
    
    
def read(cam, scale):
    """
    :brief      Read one frame from the camera
    :param      cam:        Camera Device
    :param      scale:      Factor to scale the image, 1 = normal
    :return     Numpy array of the image in BGR
    """
    # get raw image
    raw_image = cam.data_stream[0].get_image()
    if raw_image is None:
        print("Getting image failed.")
        
    # get param of improving image quality
    if cam.GammaParam.is_readable():
        gamma_value = cam.GammaParam.get()
        gamma_lut = gx.Utility.get_gamma_lut(gamma_value)
    else:
        gamma_lut = None
    if cam.ContrastParam.is_readable():
        contrast_value = cam.ContrastParam.get()
        contrast_lut = gx.Utility.get_contrast_lut(contrast_value)
    else:
        contrast_lut = None
    if cam.ColorCorrectionParam.is_readable():
        color_correction_param = cam.ColorCorrectionParam.get()
    else:
        color_correction_param = 0
        
    
    #rgbg_image = raw_image.get_numpy_array()
    # get RGB image from raw image
    inst_image = raw_image.convert("RGB")
    # improve image quality
    inst_image.image_improvement(color_correction_param, contrast_lut, gamma_lut)
    # create numpy array with data from raw image
    rgb_image = inst_image.get_numpy_array()
    #r,g,b = cv2.split(rgb_image)
    #rgb_image = np.dstack((r*2, g, b*2))
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    
    # rotate, 1 = cw, 0 = ccw
    #rotated_image=cv2.transpose(bgr_image)
    #rotated_image=cv2.flip(rotated_image,flipCode=1)
    #rotated_image=cv2.transpose(rotated_image)
    #rotated_image=cv2.flip(rotated_image,flipCode=1)
    #rotated_image = np.rot90(bgr_image, 2)
    rotated_image=bgr_image
    
    #rescale
    width = int(rotated_image.shape[1] * scale)
    height = int(rotated_image.shape[0] * scale)
    dim = (width, height)
    #print(dim)
    return cv2.resize(rotated_image, dim, interpolation = cv2.INTER_AREA)

def close(cam):
    """
    :brief      Closing the camera and disabling the streaming
    :param      cam:        Camera Device
    """
    cam.stream_off()

    # close device
    cam.close_device()
    
# combines four frames into one, using this order:
# 0 1
# 2 3
def four_in_one_frame(four_frames,scale):
    """
    :brief      Combines four frames in this order
                0 1
                2 3
    :param      four_frames:    Four numpy arrays of images [image0, image1, image2, image3]
    :param      scale:          Factor to scale the image, 1 = normal
    :return:    Numpy array of the combined image
    """
    #combine the four frames into one
    ry_horiontal = np.hstack((four_frames[0], four_frames[1]))
    bg_horiontal = np.hstack((four_frames[2], four_frames[3]))
    rybg_frame = np.hstack((ry_horiontal, bg_horiontal))
    width, height = rybg_frame.shape
    
    # rescaling image
    width = int(rybg_frame.shape[1] * scale)
    height = int(rybg_frame.shape[0] * scale)
    dim = (width, height)
    return cv2.resize(rybg_frame, dim, interpolation = cv2.INTER_AREA)
    