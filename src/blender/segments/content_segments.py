import bpy
import uuid
from .segment import Segment

class OpeningSegment(Segment):
    def __init__(self, scene=None, data={}, channel=1):
        super().__init__(
            scene=scene,
            frame_start=0,
            first_channel=channel,
            name="opening"
            )
        
        self.background, channel, _ = self.new_clip_strip(
            bg_path=data.get("background"), 
            channel=channel, 
            frame_start=0, 
            name="background",
            has_audio=True)
        self.frame_end = self.background.frame_final_end
        self.last_channel = channel

class ClosingSegment(Segment):
    def __init__(self, scene=None, data={}, channel=1, frame_start=0):
        super().__init__(
            scene=scene,
            frame_start=frame_start,
            first_channel=channel,
            name="closing"
            )
        
        self.background, channel, _ = self.new_clip_strip(
            bg_path=data.get("background"), 
            channel=channel, 
            frame_start=frame_start, 
            name="background",
            has_audio=True)
        self.frame_end = self.background.frame_final_end
        self.last_channel = channel

class ContentSegment(Segment):
    def __init__(self, scene=None, frame_start=0, first_channel=1, data={}, index=0):
        super().__init__(
            scene=scene,
            frame_start=frame_start,
            name=f"content.{index}",
            first_channel=first_channel
            )
        
        channel = first_channel
        
        # audio
        self.audio = self.new_audio_strip(
            name="main_audio",
            data={
                "filepath": data["audio_path"]
            },
            channel=channel,
            frame_start=frame_start
            )
        
        frame_start_offset = self.audio.frame_final_start
        timeline_data = data["timeline"]
        timeline_frame_start = frame_start_offset + int(timeline_data["start_time"] * self.fps)
        
        # background
        channel = channel + 1
        self.background, _, _ = self.new_clip_strip(
            bg_path=data.get("background_path", None), 
            channel=channel, 
            frame_start=frame_start,
            frame_end=timeline_frame_start,
            name=f"background")
        
        # title
        channel = channel + 1
        self.title = self.create_title(
            text=data["title"],
            channel=channel,
            name=f"title.{index}",
            frame_start=frame_start + 50,
            frame_end=timeline_frame_start
        )
        
        # bullets
        self.bullets = []
        for index, bullet in enumerate(data["summary_bullets"]):
            text = bullet["text"]
            frame_start = frame_start_offset + int(bullet["start_time"] * self.fps)
            print(f"frame_start={frame_start}. timeline_frame_start={timeline_frame_start}")
            channel = channel + 1
            strip = self.create_bullet(
                name=f"bullet.{index}",
                data={"text": text},
                channel=channel,
                frame_start=frame_start,
                frame_end=timeline_frame_start,
                index=index
                )
            self.bullets.append(strip)
            # TODO: add animation
        
        
        # timeline
        channel = channel + 1
        stages = timeline_data["bill_process_stages"]
        current_stage_index = timeline_data["bill_process_step"]
        
        # timeline 
        self.timeline = {}
        self.timeline["title"] = self.create_timeline_title(
            data={"text": timeline_data["title"]},
            name=f"timeline.title",
            channel=channel,
            frame_start=timeline_frame_start,
            frame_end=self.audio.frame_final_end
        )
        
        # timeline stages
        channel = channel + 1
        self.timeline["animation"] = self.create_timeline_stage(
            stages=stages,
            current_stage_index=current_stage_index,
            channel=channel,
            frame_start=self.timeline["title"].frame_final_start,
            frame_duration=self.audio.frame_final_end - timeline_frame_start,
            name="timeline.clip"
        )
        
        hearing_date_data = timeline_data.get("hearing_date", None)
        if hearing_date_data:
            channel = channel + 1
            self.timeline["hearing_date"] = self.create_hearing_date(
                frame_start=frame_start_offset + int(hearing_date_data["start_time"] * self.fps),
                frame_end=self.audio.frame_final_end,
                text=hearing_date_data["text"],
                channel=channel
            )
        
        self.frame_end = self.audio.frame_final_end
        self.last_channel = channel
        
    def create_timeline_title(self, data, name, channel, frame_start, frame_end):
        return self.render_text_rect_asset(
            scene=next(s for s in bpy.data.scenes if s.name == "timeline_title"),
            text=data["text"],
            name=name,
            channel=channel,
            frame_start=frame_start,
            frame_end=frame_end,
            position=[-300, 220]
        )
    
    def create_hearing_date(self, frame_start, frame_end, text, channel):
        strip = self.new_text_strip(
            text=text, 
            name=f"timeline.hearing_date",
            channel=channel,
            frame_start=frame_start,
            frame_end=frame_end,
            format={
                "font_size": 30,
                "color": (1, 1, 1, 1),
                "font_path": "/Users/pavel/Documents/haystack/hs-blender/assets/MEDIA/FONTS/static/Roboto-Bold.ttf"
            }
        )
        
        strip.transform.offset_x = 64
        strip.transform.offset_y = -214
    
    def create_timeline_stage(self, stages, current_stage_index, channel, frame_start, frame_duration, name):
        # clone the original scene
        original_scene=next((s for s in bpy.data.scenes if s.name == "timeline_stages"), None)
        if not original_scene:
            raise ValueError("Scene 'timeline_stages' not found in the current Blender file.")
        scene = original_scene.copy()
        scene.name = f"cloned_scene_{uuid.uuid4()}"
        
        for obj in original_scene.objects:
            obj_copy = obj.copy()
            if obj.data:
                obj_copy.data = obj.data.copy()
            scene.collection.objects.link(obj_copy)
        
        meta_main = next(s for s in scene.sequence_editor.sequences_all if s.name == "meta.main")
        
        metas = [meta for meta in meta_main.strips if meta.type == "META"]
        # update strips content
        for index, stage in enumerate(stages):
            meta = metas[index]
            meta.frame_final_duration = frame_duration
            text_strip = next((s for s in meta.strips if s.type == "TEXT"), None)
            text_strip.text = stage
        
        # remove unnecessary strips
        for meta in metas[current_stage_index:]:
            red_strip = next((s for s in meta.strips if "red" in s.name), None)
            # scene.sequence_editor.sequences.remove(red_strip)
            meta.strips.remove(red_strip)
        
        for meta in metas[len(stages):]:
            # scene.sequence_editor.sequences.remove(meta)
            meta.blend_alpha = 0
        
        # remove last stage line
        last_meta = metas[len(stages)-1]
        line_strip = next((s for s in last_meta.strips if ".line" in s.name), None)
        line_strip.blend_alpha = 0
        last_meta.strips.remove(line_strip)
        
        offset = 80 * (len(metas) - len(stages))
        meta_main.transform.offset_x += offset
        meta_main.frame_final_duration = frame_duration
        
        # update color strip
        color_strip = next(s for s in scene.sequence_editor.sequences_all if s.type == "COLOR")
        # color_strip = next((s for s in meta_main.strips if s.type == "COLOR"), None)
        color_strip.frame_final_duration = frame_duration
        
        # render
        bpy.context.window.scene = scene
        
        bpy.context.scene.render.use_sequencer = True
        scene.render.fps_base = 1
        # scene.render.fps = 30
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.gopsize = 60
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"  # MEDIUM,LOW
        # scene.render.ffmpeg.ffmpeg_preset = "GOOD"
        # # scene.render.ffmpeg.audio_codec = "NONE"
        scene.frame_start = 1
        scene.frame_end = frame_duration
        bpy.context.scene.render.filepath = f"/tmp/timeline_{uuid.uuid4()}.mp4"
        bpy.ops.render.render(animation=True, write_still=False)
        
        filepath = bpy.context.scene.render.filepath
        # filepath = "/tmp/timeline.mp4"
        
        # bpy.context.window.scene = self.scene
        strip, _, _ = self.new_clip_strip(
            bg_path=filepath,
            channel=channel, 
            frame_start=frame_start,
            name=name,
            frame_end=frame_start + frame_duration
        )
        
        strip.transform.offset_y = -220
        
        scene.use_fake_user = True
        bpy.context.window.scene = scene
        
        return strip
    
    def create_bullet(self, name, data, channel, frame_start, frame_end, index):
        return self.render_text_rect_asset(
            scene=next(s for s in bpy.data.scenes if s.name == "bullet"),
            text=data["text"],
            name=name,
            channel=channel,
            frame_start=frame_start,
            frame_end=frame_end,
            position=[320,  250 - 130 * (index + 1)]
        )
        
    def create_title(self, text, name, channel, frame_start, frame_end):
        return self.render_text_rect_asset(
            scene=next(s for s in bpy.data.scenes if s.name == "title"),
            text=text,
            name=f"{self.name}.{name}",
            channel=channel,
            frame_start=frame_start,
            frame_end=frame_end,
            position=[320, 250]
        )
        