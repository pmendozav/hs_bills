import sys
import os
import json
import random
from pydub import AudioSegment

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

def read_and_preprocess_input_data(config=None):
    """Read and preprocess input from assets/input.json."""
    data = None
    input_path = os.path.join(os.path.dirname(__file__), "../assets/input.json")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data is None:
        raise ValueError("Input data is empty or not found.")
    
    if config is None:
        config = read_config()
        
    if config is None:
        raise ValueError("Configuration data is empty or not found.")
    
    data.get("blocks", [])
    for block in data["blocks"]:
        # validate mandatory fields: bill_topic, title, summary_bullets (array), bill_flow_origin, current_step (integer), timeline (dict), audio_path
        if "bill_topic" not in block:
            raise ValueError("Block is missing 'bill_topic' field.")
        if "title" not in block:
            raise ValueError("Block is missing 'title' field.")
        if "summary_bullets" not in block or not isinstance(block["summary_bullets"], list):
            raise ValueError("Block is missing 'summary_bullets' field or it is not a list.")
        if "bill_flow_origin" not in block:
            raise ValueError("Block is missing 'bill_flow_origin' field.")
        if "current_step" not in block or not isinstance(block["current_step"], int):
            raise ValueError("Block 'current_step' must be an integer.")
        
        # audio duration
        audio_path = block.get("audio_path", None)
        if audio_path is None or not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        block["audio_duration"] = len(AudioSegment.from_file(audio_path)) / 1000.0
        
        # background clip
        bill_topic = block.get("bill_topic", None)
        if bill_topic is None:
            raise ValueError("Bill topic is missing in the block data.")
        
        bg_list = config.get("backgrounds", {}).get(bill_topic, [])
        background_path = random.choice(bg_list) if bg_list else None
        if background_path is None or not os.path.exists(background_path):
            raise FileNotFoundError(f"Background file not found for topic '{bill_topic}': {background_path}")
        block["background_path"] = background_path

        summary_bullets = block.get("summary_bullets", [])
        if not isinstance(summary_bullets, list):
            raise ValueError("Summary bullets should be a list.")
        for bullet in summary_bullets:
            # validate mandatory fields: text and start_time (int)
            if "text" not in bullet:
                raise ValueError("Bullet point is missing 'text' field.")
            if "start_time" not in bullet or not isinstance(bullet["start_time"], int):
                raise ValueError("Bullet point 'start_time' must be an integer.")
            
            icon_cagetory = bullet.get("icon_category", None)
            if icon_cagetory is None:
                continue
            icons_list = config.get("icons", {}).get(icon_cagetory, [])
            icon_path = random.choice(icons_list) if icons_list else None
            if icon_path is None:
                continue
            if not os.path.exists(icon_path):
                raise FileNotFoundError(f"Icon file not found for category '{icon_cagetory}': {icon_path}")
            bullet["icon_path"] = icon_path

    return data

def read_config():
    """Read and preprocess config from assets/config.json."""
    config_path = os.path.join(os.path.dirname(__file__), "../assets/config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

if __name__ == "__main__":
    config = read_config()
    
    data = read_and_preprocess_input_data()
    print("Input data:", data)
    
    scene = read_and_parse_template(filepath=data.get("template", None))
    scene.parse()
    scene.update(data=data, config=config)
    print("Current scene:", scene.name)
    print("Sample:", scene.elements.blocks[2].timeline.stages[6].text.text)
    
    