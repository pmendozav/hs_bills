import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blender.helper import BlenderFile
from blender.bill_scene import BillScene

import debugpy

debugpy.listen(("localhost", 5678))
print("Waiting for debugger attach...")
debugpy.wait_for_client()

if __name__ == "__main__":
    blender_file = BlenderFile()
    blender_file.read(filepath="./assets/blender/Legislative_Watch_Demo1.blend")

    bill_scene = BillScene(scene=blender_file.get_scene(), n_blocks=3)

    print("Current scene:", bill_scene.name)
    print("Sample:", bill_scene.elements.blocks[2].timeline.stages[6].text.text)
    