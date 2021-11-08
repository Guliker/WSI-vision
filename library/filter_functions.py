"""
Based on python code for Multiple Color Detection:
https://www.geeksforgeeks.org/multiple-color-detection-in-real-time-using-python-opencv/

	to run:
install python 2.17.18
pip2 install numpy
pip2 install opencv-contrib-python

cd "Windesheim Office365\O365-Fabriek van de Toekomst 21-22 sem1 - IJsseltechnologie\3 realiseren\Camera Python"
python2
then run this file with python

controls:
- to shift mid offset to the left
+ to shift mid offset to the right
d to open debug windows and info
"""

""" ----- IMPORTS ----- """
import gxipy as gx

import math
import numpy as np
import cv2
""" ----- ----- ----- """

""" ----- DEFINE ----- """
debug = False
config = True
font = cv2.FONT_HERSHEY_SIMPLEX

# 0,1 for webcam, 1,0 for droidcam
resolution = (1000, 1600)
offset_resolution = (1040, 200)
#resolution = (3088, 2048)
#offset_resolution = (0, 0)
balance_auto = False
gain_rgb = (1.6 , 1.0, 2.5)
frame_rate = 20

device_manager = gx.DeviceManager()
camera = device_manager.open_device_by_index(1)
cam_scale = 0.5
mask_scale = 0.5

cam_exposure = 8000
cam_gain = 8

# settings for the calibration window
x_offset = 0
y_offset = 0
search_height = 450
search_width = 60

# lab offsets for the color finder, each value is an hard value, order is:
# 0 = lum
# 1 = a; green - magenta
# 2 = b; blue - yellow
lab_offset_table = [50,5,5]

# hard values of block information, !!!!! should be added to calibration mode !!!!!
block_small_area = 500
block_width_big = 50
block_height = 20
block_height_offset = 5


# line size to split blocks
cut_size = 10 	
# distance to check rotation
workspace_height = block_height * 10
workspace_width = int(block_width_big * 2.5)
off_orr = int(block_height*0.5)

# type of color space used, many possibilities
# https://learnopencv.com/color-spaces-in-opencv-cpp-python/
# COLOR_BGR2RGB, COLOR_BGR2LAB, COLOR_BGR2YCrCb, COLOR_BGR2HSV, COLOR_BGR2HSL
color_space = cv2.COLOR_BGR2LAB
#color_space = cv2.COLOR_BGR2YCrCb

# all logic tables
color_name_table = (		"green",		"yellow",	   "blue",		 "red"	   )   # name of each color
color_bgr_table = (		 (0,200,0),	 (0,190,255),	(255,70,0),	 (0,0,255)	)   # colors used to display on screen text and boxes
lab_min_max_table = [	   [[],[]],		[[],[]],		[[],[]],		[[],[]]	 ]   # here are the min and max LAB values stored for each color
color_mask_table = [		[],			 [],			 [],			 []		  ]   # here are the bit masks stored for each color
color_contour_table = [	 [],			 [],			 [],			 []		  ]   # here are the contours of each block stored for each color
color_mask_combine = []
""" ----- ----- ----- """

""" ----- FUNCTION ----- """

def init(cam, dev):
	print("")
	print("Initializing......")

	# create a device manager
	dev_num, dev_info_list = device_manager.update_device_list()
	if dev_num == 0:
		print("Number of enumerated devices is 0")
		return

	# exit when the camera is a mono camera
	if cam.PixelColorFilter.is_implemented() is False:
		print("This sample does not support mono camera.")
		cam.close_device()
		return
	
	if(config):
		# set default values
		cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
		cam.ExposureTime.set(cam_exposure)
			# reset offsets
		cam.OffsetX.set(0)
		cam.OffsetY.set(0)
			# set resolution of camera
		cam.Width.set(resolution[0])
		cam.Height.set(resolution[1])
		cam.OffsetX.set(offset_resolution[0])
		cam.OffsetY.set(offset_resolution[1])
			# set frame rate of the camera
		cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)
		cam.AcquisitionFrameRate.set(frame_rate)
			# set gain/balance for all channels and then for red green and blue
		if(balance_auto):
			cam.BalanceWhiteAuto.set(gx.GxSwitchEntry.ON)
		else:
			cam.BalanceWhiteAuto.set(gx.GxSwitchEntry.OFF)
			cam.Gain.set(cam_gain)
			cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.RED)
			cam.BalanceRatio.set(gain_rgb[0])
			cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.GREEN)
			cam.BalanceRatio.set(gain_rgb[1])
			cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.BLUE)
			cam.BalanceRatio.set(gain_rgb[2])
	
	print("Complete")
	print("")
	
	# start data acquisition
	cam.stream_on()

def cam_exit(cam):
	cam.stream_off()

	# close device
	cam.close_device()

def cam_read(cam,scale):
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
	
	#rescale
	width = int(bgr_image.shape[1] * scale)
	height = int(bgr_image.shape[0] * scale)
	dim = (width, height)

	#print(bgr_image[0][0])
	#b, g, r = cv2.split(bgr_image)
	#print(g)
	return cv2.resize(bgr_image, dim, interpolation = cv2.INTER_AREA)

""" ----- ----- CALIBRATION ----- ----- """
# draws box on pos(x,y) with size(w,h)
# draws text above the box
def draw_calibration_box(image, x, y, w, h, text, color):
	line_width = 2  # change if resolution changes
	# draw square
	cv2.rectangle(image, (x, y), (x + w, y + h), color, line_width)
	# write text above square
	cv2.putText(image, text, (x, y - 2 * line_width),
				cv2.FONT_HERSHEY_SIMPLEX, line_width/4, 
				color)  

# returns min and max value of an array corrected with the offset
def min_max_calculate(value, offset):
	min_value = np.amin(value) - offset
	max_value = np.amax(value) + offset
	return [min_value, max_value]

# returns min lab and max lab values of an image
def lab_min_max_calculate(image):
	#convert image to lab and split those values
	lab_image = cv2.cvtColor(image, color_space)
	l, a, b = cv2.split(lab_image)
	
	# lum
	l_min, l_max = min_max_calculate(l, lab_offset_table[0])
	# a
	a_min, a_max = min_max_calculate(a, lab_offset_table[1])
	# b
	b_min, b_max = min_max_calculate(b, lab_offset_table[2])
	
	return[[l_min, a_min, b_min],[l_max, a_max, b_max]] 

# save the lab values for a specific color
def lab_save(color_index, lab_min, lab_max):
	lab_min_max_table[color_index][0] = lab_min
	lab_min_max_table[color_index][1] = lab_max

""" ----- ----- COLOR MASK ----- ----- """
# creates a mask for one color
def mask_color(kernal, image, color, min_max_array, scale=1):
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

	return cv2.resize(color_mask, dim, interpolation = cv2.INTER_AREA)

# combines four frames into one, using this order:
# 0 1
# 2 3
def four_in_one_frame(four_frames,scale):
	#combine the four frames into one
	ry_horiontal = np.hstack((four_frames[0], four_frames[1]))
	bg_horiontal = np.hstack((four_frames[2], four_frames[3]))
	rybg_frame = np.vstack((ry_horiontal, bg_horiontal))
	width, height = rybg_frame.shape
	
	# rescaling image
	width = int(rybg_frame.shape[1] * scale)
	height = int(rybg_frame.shape[0] * scale)
	dim = (width, height)
	return cv2.resize(rybg_frame, dim, interpolation = cv2.INTER_AREA)
	
# calculates smallest angle between two points, always under 180
def angle_between(p1, p2):
	angle = np.arctan2(p1[1] - p2[1], p2[0] - p1[0])
	return angle
	
""" ----- ----- CONTOURS ----- ----- """
# creates contour array from an image and checks if the contour is big enough
def create_contour(mask, method=cv2.CHAIN_APPROX_SIMPLE):
	# Creating contour array
	contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, method)
	i = 0
	while (i < len(contours)):
		area = int(cv2.contourArea(contours[i]))
		if(area < block_small_area):
			contours.pop(i)
		else:
			i += 1

	return contours

# spits contours that are too high
def split_contour(image, contour):
	x, y, w, h = cv2.boundingRect(contour)
	stack_height = int(round((h - block_height_offset)/block_height))
	for index in range(1, stack_height):
		left_cut = np.array([x, y + (h*(index/float(stack_height)))], dtype='int')
		right_cut = np.array([x + w, y + (h*(index/float(stack_height)))], dtype='int')
		cv2.line(image, tuple(left_cut), tuple(right_cut), (0, 0, 0), 3)
		#print("cutting" + str(index) + "	pos: " + str(left_cut) + ":" + str(right_cut))
		#print(str(stack_height) + "	num: " + str(index/float(stack_height)))
			
# show contours on the main display
def draw_contour(image, contour, color):
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

# returns a box of the designated workspace
# workspace is calculated as a rectanble that is rotated the same as the lowest block in the image
def get_work_space(image, contours, width, height, offset, scale=1):
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
		midleft = [int(cx - (width * np.cos(angle))), int(cy + (width * np.sin(angle)))]		# left
		midright = [int(cx + (width * np.cos(angle))), int(cy - (width * np.sin(angle)))]		# right
		
		box[0] = [int(midleft[0] - (height * np.sin(angle)))*scale, int(midleft[1] - (height * np.cos(angle)))*scale]		# topleft
		box[1] = [int(midright[0] - (height * np.sin(angle)))*scale, int(midright[1] - (height * np.cos(angle)))*scale]		# topright
		box[2] = [int(midright[0] + (height * np.sin(angle)))*scale, int(midright[1] + (height * np.cos(angle)))*scale]		# bottomright
		box[3] = [int(midleft[0] + (height * np.sin(angle)))*scale, int(midleft[1] + (height * np.cos(angle)))*scale]		# bottomleft
		
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
	h = np.float32( [[0, 0],
[width - 1, 0],
					[width - 1, height - 1],
					[0, height - 1]])
	m = cv2.getPerspectiveTransform(workspace.astype(np.float32),h)
	return cv2.warpPerspective(image,m,(width, height))

""" ----- ----- COUNTING ----- ----- """
def sort_contours(cnts, clr):
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
def block_color_fill(fill_array, cnt_array, color_index):
	for i in range(0,len(cnt_array)):
		x, y, w, h = cv2.boundingRect(cnt_array[i])
		if(w > block_width_big):
			fill_array.append(color_index + 5)
		else:
			fill_array.append(color_index + 1)

""" ----- ----- ----- """
# trackbar callback fucntion does nothing but required for trackbar
def nothing(x):
	pass
""" ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- """
""" ----- MAIN LOOP FOR CALIBRATION ----- """
""" ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- """
init(camera, device_manager)
step_index = 0

while(1):	
	# get one frame of the camera
	frame = cam_read(camera, cam_scale)
	
	# create copy of frame to show to user
	final_frame = frame.copy()

	# get info of that frame
	height, width, depth = frame.shape

	# crop image to centre
	x = int((width - search_width)/2) + x_offset
	y = int((height - search_height)/2) + y_offset
	img_crop = frame[y:y+search_height, x:x+search_width]
	# show the box that shows where the crop is
	draw_calibration_box(final_frame, x, y, search_width, search_height,
							color_name_table[step_index], color_bgr_table[step_index])
  
	# convert cropped image to min and max LAB values
	lab_min,lab_max = lab_min_max_calculate(img_crop)

	# in debug mode: display the lab min and max values
	# and display the cropped image
	if(debug):
		#min
		cv2.putText(final_frame, str(lab_min), (20,20),
					font, 0.4,
					color_bgr_table[step_index])   
		# max
		cv2.putText(final_frame, str(lab_max), (20,40),
					font, 0.4,
					color_bgr_table[step_index])
		# show the cropped image
		cv2.imshow('img_crop', img_crop)
	
	# show operator instructions
	cv2.putText(final_frame, "Calibration mode", (150,50),
				font, 1,
				(255,255,255))
	cv2.putText(final_frame, "press space to save", (150,100),
				font, 1,
				(255,255,255))

	# show the video with the calibration box
	cv2.imshow("Video", final_frame)
	
	key = cv2.waitKey(10) & 0xFF 
	# check for spacebar to go to next step
	if key == ord(' '):
		# save the found lab values
		lab_save(step_index, lab_min, lab_max)
		# go to the next color
		step_index += 1
		# test if there is a next color
		if step_index >= len(color_name_table):
			break
	# check d key to toggle debug mode
	if key == ord('d'):
		if(debug):
			cv2.destroyWindow("img_crop")
		debug = not debug

""" ----- EXIT ----- """

# print all the saved LAB min and max values
# cv2.destroyAllWindows()
if(debug):
	cv2.destroyWindow("img_crop")
for i,name in enumerate(color_name_table):
	print(name + ":")
	print(lab_min_max_table[i])

""" ----- ----- ----- """

""" ----- MAIN LOOP BLOCK FINDER ----- """
mid_pos = 2
while(1):
	# get one frame of the camera
	frame = cam_read(camera, cam_scale)
	
	# Convert the frame
	# BGR(RGB color space) to 
	# lab(hue-saturation-value)
	lab_frame = cv2.cvtColor(frame, color_space)
	
	kernal = np.array( [[0,1,0]	,
						[1,1,1]	,
						[0,1,0]	,], "uint8")
	
	# create masks for each color, and check rotation of the masks
	for i, name in enumerate(color_name_table):
		#creates a color mask
		color_mask_table[i] = mask_color(kernal, lab_frame, color_bgr_table[i], lab_min_max_table[i], mask_scale)
		if (i):
			color_mask_combine = cv2.bitwise_or(color_mask_combine, color_mask_table[i])
		else:
			color_mask_combine = color_mask_table[i]
	
	color_mask_combine = cv2.dilate(color_mask_combine, kernal, iterations=1)
	#color_mask_combine = cv2.erode(color_mask_combine, kernal, iterations=2)
	contours_combined = create_contour(color_mask_combine, method=cv2.CHAIN_APPROX_NONE)
	
	if(contours_combined):
		workspace = get_work_space(frame, contours_combined, workspace_width, workspace_height, off_orr, mask_scale)
		work_frame = transform(frame, workspace, workspace_width, workspace_height)
		lab_frame = cv2.cvtColor(work_frame, color_space)
		
		#cv.drawContours(frame, contours, 3, (0,255,0), 3)
		# after rotated make contours of the mask
		
		# loop through all the colors and make for each color an mask and contours
		for i, name in enumerate(color_name_table):
			#creates a color mask
			color_mask_table[i] = mask_color(kernal, lab_frame, color_bgr_table[i], lab_min_max_table[i])
			
			# creates contours of the created mask
			# contour = create_contour(color_mask_table[i])
			color_contour_table[i] = create_contour(color_mask_table[i])
			
			# loop trough all contours
			for contour in color_contour_table[i]:
				if(debug):
					draw_contour(work_frame, contour, color_bgr_table[i])
				split_contour(color_mask_table[i], contour)
			
			color_contour_table[i] = create_contour(color_mask_table[i])
			for contour in color_contour_table[i]:
				if(not debug):
					draw_contour(work_frame, contour, color_bgr_table[i])
			
			# show the cut up frame

			# write color channel text to display
			cv2.putText(color_mask_table[i], name, (10,20),
						font, 1,
						(255, 255, 255))
			cv2.putText(color_mask_table[i], str(lab_min_max_table[i][0]), (10,45),
						font, 0.5,
						(255, 255, 255))
			cv2.putText(color_mask_table[i], str(lab_min_max_table[i][1]), (10,60),
						font, 0.5,
						(255, 255, 255))
			
		# combine all the colors for sorting
		all_contours = color_contour_table[0] + color_contour_table[1] + color_contour_table[2] + color_contour_table[3]
		
		# fill a color array to remember the size and color of each contour
		all_colors = []
		for i, name in enumerate(color_name_table):
			block_color_fill(all_colors, color_contour_table[i], i)

		# sort all blocks from bottom-top and print
		contours,colors = sort_contours(all_contours,all_colors)
		

		all_pos = []
		
		# place mid line
		if(len(contours)):
			x, y, w, h = cv2.boundingRect(contours[0])
			x = int(x + (mid_pos/float(4))*w)
			y = int(y + 0.5*h)
			cv2.circle(work_frame, (x,y), 5, (255,255,255), -1)
			
			compare_x = x
			for contour in contours:
				x, y, w, h = cv2.boundingRect(contour)
				mid_x = int(x + 0.5*w)
				if (mid_x > compare_x + 10):	# right side
					all_pos.append(3)
				elif (mid_x < compare_x - 10):  # left side
					all_pos.append(1)
				else:						   # middle
					all_pos.append(2)
					
		
		cv2.putText(frame, str(colors), (20,40),
					font, 1,
					(255, 255, 255))	

		cv2.putText(frame, str(all_pos), (20,100),
					font, 1,
					(255, 255, 255))	
				
	# in debug mode: show the mask frames of each color
	if(debug):
		debug_frame = four_in_one_frame(color_mask_table, 0.8)
		cv2.imshow("rybg_frame", debug_frame)
		cv2.imshow("color_mask_combine", color_mask_combine)

	# show normal view + bounding boxes	
	cv2.imshow("Video", frame)
	cv2.imshow("Raw Frame", work_frame)


	key = cv2.waitKey(10) & 0xFF 
	# check spacebar to exit
	if key == ord(' '):
		break
	# check d key to toggle debug mode
	if key == ord('d'):
		if(debug):
			cv2.destroyWindow("rybg_frame")
			cv2.destroyWindow("color_mask_combine")
		debug = not debug
	if key == ord('-'):
		mid_pos -= 1
	if key == ord('='):
		mid_pos += 1

""" ----- ----- ----- """

""" ----- EXIT ----- """
cam_exit(camera)
cv2.destroyAllWindows()

""" ----- ----- ----- """

'''
translator:
1 = Green Small	 5 = Green Big
2 = Yellow Small	6 = Yellow Big
3 = Blue Small	  7 = Blue Big
4 = Red Small	   8 = Red Big

1 = left
2 = middle
3 = right

height testing:
1 = 30 - 36
2 = 54 - 60
3 = 78 - 84
'''