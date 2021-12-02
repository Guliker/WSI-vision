"""
Function used to make a xml file from a block list
"""

""" ----- IMPORTS ----- """
import config as cfg
from xml.dom import minidom
""" ----- ----- ----- """

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
        pos = cfg.map_pos[info[1]]
        size = cfg.map_block[info[0]][1]
        color =  cfg.map_block[info[0]][0]

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