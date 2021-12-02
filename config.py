"""
Load all the settings used for the vision module
"""
""" ----- overall settings ----- """
import cv2
font = cv2.FONT_HERSHEY_SIMPLEX

""" ----- recept result ----- """
font_size_rr = 1
spacing = 80*font_size_rr
colom1 = 10
colom2 = 150
window_size = (1000, 250,3)

""" ----- calibration ----- """
calibration_search_height = 80
calibration_serach_height_offset = 70
## settings for the calibration window
calibration_search_width = 80

""" ----- socket ----- """
# IJsel laptop
#HOST = '192.168.14.219'
# debug laptop
#HOST = '192.168.14.174'
HOST = ''
PORT = 30001
HOST_send = '192.168.14.219'

command_message_vision = "asking_for_file"

""" ----- XML ----- """
map_block = {
    1: ("Green", "1"),
    2: ("Yellow", "1"),
    3: ("Blue", "1") ,
    4: ("Red", "1"),
    5: ("Green", "2"),
    6: ("Yellow", "2"),
    7: ("Blue", "2"),
    8: ("Red", "2"),
}

map_pos = {
    1: "-0.5",
    2: "0",
    3: "0.5",
}
""" ----- viewer ----- """
viewer_size = (668,974)