import sys
import os
import json
import random
from pydub import AudioSegment

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blender.helper import BlenderFile
from blender.scenes.bills.bill_scene import BillScene

import debugpy

debugpy.listen(("localhost", 5678))
print("Waiting for debugger attach...")
debugpy.wait_for_client()

def save_template(filepath):
    blender_file = BlenderFile()
    blender_file.save(filepath)

def read_and_parse_template(filepath):
    blender_file = BlenderFile()
    blender_file.read(filepath=filepath)

    return BillScene(scene=blender_file.get_scene(), n_blocks=3)

def read_and_preprocess_input_data():
    """Read and preprocess input from assets/input.json."""
    input_path = os.path.join(os.path.dirname(__file__), "../assets/input.json")
    segments_data = None
    with open(input_path, "r", encoding="utf-8") as f:
        segments_data = json.load(f)
    if segments_data is None:
        raise ValueError("Input data is empty or not found.")
    
    """Read and preprocess config from assets/config.json."""
    config_path = os.path.join(os.path.dirname(__file__), "../assets/config.json")
    config = None
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    if config is None:
        raise ValueError("Configuration data is empty or not found.")
    
    for segment in segments_data:
        if "bill_topic" not in segment:
            raise ValueError("Segment is missing 'bill_topic' field.")
        if "title" not in segment:
            raise ValueError("Segment is missing 'title' field.")
        
        # validate bullet points
        bullets_content = segment.get("summary_bullets", None)
        if bullets_content is None or not isinstance(bullets_content, list):
            raise ValueError("Segment is missing 'summary_bullets' field or it is not a list.")
        for bullet in bullets_content:
            if "text" not in bullet:
                raise ValueError("Bullet point is missing 'text' field.")
            if "start_time" not in bullet or not isinstance(bullet["start_time"], (int, float)):
                raise ValueError("Bullet point 'start_time' must be an integer or float.")
            # icon_category is optional, so we don't validate it here
        
        # validate timeline
        if "timeline" not in segment:
            raise ValueError("Segment is missing 'timeline' field.")
        timeline_content = segment["timeline"]
        if "bill_process" not in timeline_content:
            raise ValueError("Segment is missing 'bill_process' field.")
        if "bill_process_step" not in timeline_content:
            raise ValueError("Segment is missing 'bill_process_step' field.")
        if "title" not in timeline_content:
            raise ValueError("Segment is missing 'title' field.")
        if "start_time" not in timeline_content or not isinstance(timeline_content["start_time"], (int, float)):
            raise ValueError("Segment is missing 'start_time' field or it is not a number.")
        audio_path = segment.get("audio_path", None)
        if audio_path is None or not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # audio duration
        segment["audio_duration"] = len(AudioSegment.from_file(audio_path)) / 1000.0
        
        bill_process_key = segment.get("timeline", {}).get("bill_process", None)
        if not bill_process_key:
            raise ValueError("Segment is missing 'bill_process' field.")
        bill_process_stages = config.get("bill_processes", {}).get(bill_process_key, None)
        if not bill_process_stages:
            raise ValueError(f"Bill process '{bill_process_key}' not found in configuration.")
        segment["timeline"]["bill_process_stages"] = bill_process_stages
        
        # background clip
        bill_topic = segment.get("bill_topic", None)
        if bill_topic is None:
            raise ValueError("Bill topic is missing in the segment data.")
        
        bg_list = config.get("backgrounds", {}).get(bill_topic, [])
        background_path = random.choice(bg_list) if bg_list else None
        if background_path is None or not os.path.exists(background_path):
            raise FileNotFoundError(f"Background file not found for topic '{bill_topic}': {background_path}")
        segment["background_path"] = background_path

        summary_bullets = segment.get("summary_bullets", [])
        if not isinstance(summary_bullets, list):
            raise ValueError("Summary bullets should be a list.")
        for bullet in summary_bullets:
            # validate mandatory fields: text and start_time (int)
            if "text" not in bullet:
                raise ValueError("Bullet point is missing 'text' field.")
            if "start_time" not in bullet:
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
            
        segment["break_assets"] = {
            "background_path": config["break_assets"]["background"],
            "audio_path": config["break_assets"]["audio"]
        }

    return {
        "template": config["template"],
        "segments": segments_data,
        "closing": {
            "background": config["closing_background"],
            "break_assets": {
                "background_path": config["break_assets"]["background"],
                "audio_path": config["break_assets"]["audio"],
                "sting_path": config["break_assets"]["sting"]
            }
        },
        "opening": {
            "background": config["opening_background"]
        },
        "globals": {
            "audio_path": config["globals"]["audio"]
        }
    }
 
if __name__ == "__main__":
    
    input = read_and_preprocess_input_data()
    blender_file = BlenderFile()
    blender_file.read(filepath=input["template"])
    scene = BillScene(scene=blender_file.get_scene("Scene"))
    
    scene.create_scene(data=input)
    
    blender_file.save("./assets/blender/result.blend")
    blender_file.render(
        scene=scene.scene,
        frame_end=scene.frame_end,
        output_path="./assets/blender/result.mp4"
    )
    