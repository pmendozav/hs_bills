import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blender.helper import BlenderFile
from blender.scenes.bill_scene.bill_scene import BillScene

import debugpy

debugpy.listen(("localhost", 5678))
print("Waiting for debugger attach...")
debugpy.wait_for_client()

def read_and_parse_template(filepath):
    blender_file = BlenderFile()
    blender_file.read(filepath=filepath)

    return BillScene(scene=blender_file.get_scene(), n_blocks=3)

def read_and_preprocess_input():
    """Read and preprocess input from assets/input.json."""
    input_path = os.path.join(os.path.dirname(__file__), "../assets/input.json")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # TODO: preprocess data
    return data

def read_config():
    """Read and preprocess config from assets/config.json."""
    config_path = os.path.join(os.path.dirname(__file__), "../config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

if __name__ == "__main__":
    input = read_and_preprocess_input()
    print("Input data:", input)
    
    scene = read_and_parse_template(filepath=input.get("template", None))
    print("Current scene:", scene.name)
    print("Sample:", scene.elements.blocks[2].timeline.stages[6].text.text)
    
    