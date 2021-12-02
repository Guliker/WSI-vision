"""
Functions used for the WSI vision module
- calibration
- mask
- contours
- workspace
"""

""" ----- IMPORTS ----- """
from xml.dom import minidom
import os 
  
map_block =   {
                    1: ("Green", "1"),
                    2: ("Yellow", "1"),
                    3: ("Blue", "1") ,
                    4: ("Red", "1"),
                    5: ("Green", "2"),
                    6: ("Yellow", "2"),
                    7: ("Blue", "2"),
                    8: ("Red", "2"),
                }

map_pos =    {
                        1: "-0.5",
                        2: "0",
                        3: "0.5",
                    }

""" ----- ----- ----- """

"""----- ----- XML ----- -----"""
def xml_generate(block_and_pos, save_path_file = "C://ViewerOrder/Order.xml"):
    """
    :brief      Creates an xml file of the product that can be read by the customer portal
    :param      block_and_pos:      Array of the block lane and position
    :param      save_path_file:     The path and file where the made xml file will be saved
    """
    root = minidom.Document()

    xml = root.createElement('LEGOORDER') 
    root.appendChild(xml)

    for i, info in enumerate(block_and_pos):
        pos = map_pos[info[1]]
        size = map_block[info[0]][1]
        color =  map_block[info[0]][0]

        productChild = root.createElement('BRICK')
        productChild.setAttribute('Orientation', str(pos))
        productChild.setAttribute('Size', str(size))
        productChild.setAttribute('Color', str(color))
        xml.appendChild(productChild)

    xml_str = root.toprettyxml(indent ="\t") 

    with open(save_path_file, "w") as f:
        f.write(xml_str) 

#cleares file
xml_generate(())