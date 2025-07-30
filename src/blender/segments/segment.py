import bpy
import os
import uuid

class Segment:
    def __init__(self, scene=None, frame_start=0, first_channel=None, name=""):
        self.scene = scene
        self.fps = scene.render.fps / scene.render.fps_base
        
        self.first_channel = first_channel
        self.frame_end = None
        self.frame_start = frame_start
        self.name = name
        
    def render_text_rect_asset(
        self,
        scene,
        text,
        name,
        channel,
        frame_start,
        frame_end,
        position
    ):
        strip_text = next((s for s in scene.sequence_editor.sequences_all if s.type == "TEXT"), None)
        strip_text.text = text
        
        scene.render.filepath = f"/tmp/{str(uuid.uuid4())}.png"
        bpy.context.window.scene = scene
        
        bpy.context.scene.render.use_sequencer = True
        bpy.ops.render.render(animation=False, write_still=True)
        filepath = scene.render.filepath
        
        bpy.data.images.load(filepath)
        
        strip = self.scene.sequence_editor.sequences.new_image(
            name=f"{self.name}.{name}",
            filepath=filepath,
            channel=channel,
            frame_start=frame_start
        )
        
        strip.frame_final_duration = frame_end - frame_start
        strip.transform.offset_x = position[0]
        strip.transform.offset_y = position[1]
        return strip
    
    def new_text_strip(self, text, name, channel, frame_start, frame_end, format=None):
        strip = self.scene.sequence_editor.sequences.new_effect(
            name=f"{self.name}.{name}",
            type='TEXT',
            channel=channel,
            frame_start=frame_start,
            frame_end=frame_end
        )
        
        strip.text = text
        
        # default layout
        strip.transform.origin = (0.0, 0.0)
        strip.location = (0.0, 1.0)
        strip.alignment_x = 'LEFT'
        strip.anchor_x = 'LEFT'
        strip.anchor_y = 'TOP'
        
        if format is not None:
            font_path = format.get("font_path", None)
            if font_path and os.path.exists(font_path):
                strip.font = bpy.data.fonts.load(font_path)
            if format.get("font_size", None):
                strip.font_size = format.get("font_size", 20)
            if format.get("align_x", None):
                strip.align_x = format.get("align_x", 'CENTER')
            if format.get("align_y", None):
                strip.align_y = format.get("align_y", 'CENTER')
            if format.get("color", None):
                strip.color = format.get("color", (1, 1, 1, 1))
                
        return strip
        
    def new_clip_strip(self, bg_path, channel, name, frame_start=0, frame_end=None):
        strip = self.scene.sequence_editor.sequences.new_movie(
            name=f"{self.name}.{name}",
            filepath=bg_path,
            channel=channel,
            frame_start=frame_start
        )
        
        if frame_end is not None:
            strip.frame_final_end = frame_end
        
        return strip
        
    def new_audio_strip(self, data, name, channel, frame_start):
        filepath = data["filepath"]
        if not self.scene.sequence_editor:
            self.scene.sequence_editor_create()
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Audio file not found: {filepath}")
        
        strip = self.scene.sequence_editor.sequences.new_sound(
            name=f"{self.name}.{name}",
            filepath=filepath,
            channel=channel,
            frame_start=frame_start
        )
        
        return strip
    
    def new_color_strip(self, channel, name, frame_start, color):
        strip = self.scene.sequence_editor.sequences.new_effect(
            name=f"{self.name}.{name}",
            type='COLOR',
            channel=channel,
            frame_start=frame_start,
            frame_end=frame_start + 1
        )
        strip.color = color
        return strip

