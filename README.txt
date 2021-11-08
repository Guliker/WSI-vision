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

5. Optional configuration camera (MER2-630-60U3M)

	(1) Open the configuration tool "galaxy"
	
	(2) Open the usb3.0 camera in the left tool bar
	
	(3) In the right toolbar change these settings
	
		ImageFormat:
			Width = 	600
			Height = 	1000
			OffsetX =	1244
			OffsetY =	532
			
		AcquisitionTrigger:
			ExposureTime = 	8000
			TriggerMode =	gx.GxSwitchEntry.OFF
		
		AnalogControls:
			Gain = 8
			BalanceRatioSelector = 	gx.GxBalanceRatioSelectorEntry.RED
			BalanceRatio = 			1.5
			BalanceRatioSelector = 	gx.GxBalanceRatioSelectorEntry.GREEN
			BalanceRatio = 			1.0
			BalanceRatioSelector = 	gx.GxBalanceRatioSelectorEntry.BLUE
			BalanceRatio = 			2.5

6. Run Python script

	(1) Bring up the DOS command window by typing CMD 
	
	(2) Open the Python script in python2.7(3.5)
	
		python SIW_vision.py
		
		or
		
		python2 SIW_vision.py





Optie 1:
	Shape Detectie:
		Difference Mat / contour
		Box + Orientatie
	
	Kleur Detectie:
		Zet de kleuren voor de camera
		Capture de vier kleuren
		check op de hoogtes de kleuren
		
optie 2:
	Grid layout
	check kleur in elke grid
	is deze gelijk aan wat verwacht wordt

optie 3:
	3 lane detectie met points.
	(gelijk aan optie 2)
	
optie 4:
	Brick detection, via edge detection
	common height
	
	
	
