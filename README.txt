********************************************************

		Lego Tower Detection usage for OpenCV

						2021-11-1

********************************************************

Python2.7(3.5) gxipy installation  
=================================

1. Install python2.7(3.5)

	(1) Download the python2.7(3.5) installation package for Windows(x86/x86_64) from the python official path as follows and perform installations.

		Download path: https://www.python.org/downloads/windows/
  
	(2) Add the path of python.exe to the system environment variable path.

2. Install pip tools

	(1) Bring up the DOS command window by typing CMD

	(2) Type the command as follows in DOS command window to install pip.
    
		python get-pip.py

	(3) Add the path of pip.exe to the system environment variable path.

3. Install all libraries
 
	(1) Type the command as follows in DOS command window.

		pip install numpy
		
		pip install pillow
		
		pip install opencv-python==4.2.0.32

			Red error messages are fine here
		
4. Install Windows SDK Galaxy

	(1) Go to the website to download the Daheng imaging SDK, Windows SDK USB2+USB3+GigE (including Directshow + Python) Galaxy V1.12.2107.9211
	
		Download path: https://www.get-cameras.com/customerdownloads?submissionGuid=3d8fbd3b-0ca4-4de2-b947-2480dd706c29

		Only usb3 is necessarys
	
	(2) Copy the gxipy library to your project, if it isn't included yet
	
		Default path: C:\Program Files\Daheng Imaging\GalaxySDK\Samples\Python SDK\gxipy

5. Run Python script

	(1) Bring up the DOS command window by typing CMD 
	
	(2) Open the Python script in python2.7(3.5)
	
		python main.py
		
		or
		
		python2 main.py

6. Optional testing of the camera (MER2-630-60U3M)

	(1) Open the configuration tool "GalaxyView"
	
	(2) Open the usb3.0 camera in the left tool bar
	
	(3) Select the blue and white play button "start acquisition"
	
		The raw image of the camera is now displayed, if the white balance is not configured the image will have a green shade