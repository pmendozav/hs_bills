from pydub import AudioSegment
import bpy
import os

from ..scene import Scene
from . import bill_scene_types as types

class BillScene(Scene):
    def __init__(self, scene=None, n_blocks=1):
        super().__init__(scene=scene, n_blocks=n_blocks)
        self.elements = types.BillSceneElements()
        
    def setup(self):
        pass
    
    def render(self, output_path):
        pass
    
    def parse_opening_strips(self):
        bg = super().find_strip_by_name(name="opening.background", strips=self.get_movie_strips())
        animation = super().find_strip_by_name(name="opening.outro.animation", strips=self.get_movie_strips())
        audio = super().find_strip_by_name(name="opening.audio", strips=self.get_audio_strips())

        self.elements.set_opening(bg, animation, audio)


    def parse_closing_strips(self):
        bg = super().find_strip_by_name(name="closing.background", strips=self.get_movie_strips())
        audio = super().find_strip_by_name(name="closing.audio", strips=self.get_audio_strips())
        
        self.elements.set_closing(bg=bg, audio=audio)

    def parse_one_block_strips(self, index):
        strips = [strip for strip in self.all_strips if getattr(strip, "name", "").startswith(f"group.{index}")]
        timeline_strips = [strip for strip in strips if getattr(strip, "name", "").startswith(f"group.{index}.timeline")]
        bullet_strips = [strip for strip in strips if getattr(strip, "name", "").startswith(f"group.{index}.bullet")]
        outro_strips = [strip for strip in strips if getattr(strip, "name", "").startswith(f"group.{index}.outro")]
        # Remove timeline_strips, bullet_strips, and outro_strips from strips
        exclude = set(timeline_strips + bullet_strips + outro_strips)
        strips = [strip for strip in strips if strip not in exclude]
        
        # extract elements
        background = next((s for s in strips if s.name == f"group.{index}.background"), None)
        audio = next((s for s in strips if s.name == f"group.{index}.audio"), None)
        title = types.TextGroup(
            meta=next((s for s in strips if s.name == f"group.{index}.title"), None),
            text=next((s for s in strips if s.name == f"group.{index}.title.text"), None)
        )
        
        outro_animation = next((s for s in outro_strips if s.name == f"group.{index}.outro.animation"), None)
        outro_audio = next((s for s in outro_strips if s.name == f"group.{index}.outro.audio"), None)
        
        bullets = []
        for i in range(1, 4):
            bulletGroup = types.BulletGroup(
                meta=next((s for s in bullet_strips if s.name == f"group.{index}.bullet.{i}"), None),
                text=next((s for s in bullet_strips if s.name == f"group.{index}.bullet.{i}.text"), None),
                rect=next((s for s in bullet_strips if s.name == f"group.{index}.bullet.{i}.rect"), None)
            )
            bullets.append(bulletGroup)
        
        # timeline elements
        timeline_title = types.TextGroup(
            meta=next((s for s in timeline_strips if s.name == f"group.{index}.timeline.title"), None),
            text=next((s for s in timeline_strips if s.name == f"group.{index}.timeline.title.text"), None)
        )
        upcoming_text = next((s for s in timeline_strips if s.name == f"group.{index}.timeline.upcoming_text"), None)
        
        stages = []
        for i in range(1, 8):
            meta = next((s for s in timeline_strips if s.name == f"group.{index}.timeline.stage.{i}"), None)
            line = next((s for s in timeline_strips if s.name == f"group.{index}.timeline.stage.{i}.line"), None)
            text = next((s for s in timeline_strips if s.name == f"group.{index}.timeline.stage.{i}.text"), None)
            red = next((s for s in timeline_strips if s.name == f"group.{index}.timeline.stage.{i}.red"), None)
            circle = next((s for s in timeline_strips if s.name == f"group.{index}.timeline.stage.{i}.circle"), None)

            stage = types.TimelineStageGroup(meta=meta, line=line, text=text, red=red, circle=circle)
            stages.append(stage)
        timeline = types.TimelineGroup(
            title=timeline_title,
            upcoming_text=upcoming_text,
            stages=stages
        )

        billBlock = types.BillBlockGroup(
            index=index,
            background=background,
            audio=audio,
            title=title,
            bullets=bullets,
            outro_animation=outro_animation,
            outro_audio=outro_audio,
            timeline=timeline
        )
        self.elements.blocks.append(billBlock)

    def update_closing_strips(self, data=None, config=None, start_frame=0):
        pass

    def update_one_block_strips(self, index, start_frame=0, data=None, config=None):
        start_frame = start_frame + 1
        
        blocks = data.get('blocks', [])
        block_data = blocks[index - 1] if 1<= index and index <= len(blocks) else None
        if not block_data:
            return start_frame
        
        block_strips = self.elements.blocks[index - 1]
        
        #audio
        audio_path = block_data.get("audio_path")
        block_strips.audio.sound = bpy.data.sounds.load(os.path.expanduser(audio_path))
        self.update_strip_position(block_strips.audio, {
            "frame_start": start_frame,
            "frame_duration": block_strips.audio.frame_duration,
            "animation_offset_start": 0,
            "animation_offset_end": 0
        })
        
        # frames duration
        intro_frames_duration = round(block_data.get('timeline', {}).get('start_time', 0) * self.fps)
        
        # background
        background_path = block_data.get("background_path")
        clip = bpy.data.movieclips.load(os.path.expanduser(background_path))
        
        video_resolution_x, video_resolution_y = clip.size
        block_strips.background.transform.scale_x = self.scene.render.resolution_x / video_resolution_x
        block_strips.background.transform.scale_y = self.scene.render.resolution_y / video_resolution_y
        block_strips.background.filepath = background_path
        block_strips.background.frame_offset_start = 0
        block_strips.background.frame_start = start_frame
        block_strips.background.frame_final_duration = intro_frames_duration
        
        # title
        block_strips.title.text.text = block_data.get("title", "")
        self.update_strip_position(block_strips.title.meta, {
            "frame_start": start_frame + 54,
            "frame_end": block_strips.background.frame_final_end
        })
        
        # summary bullets
        frame_offset = block_strips.title.meta.frame_final_start
        for data, ref in zip(block_data.get("summary_bullets", []), block_strips.bullets):
            text = data.get("text", "")
            # icon_category = data.get("icon_category", "unknown_icon_category")
            bullet_frame_start = frame_offset + int(data.get("start_time", 0) * self.fps)
            self.update_strip_position(ref.meta, {
                "frame_start": bullet_frame_start,
                "frame_end": block_strips.background.frame_final_end
            })
            self.update_strip_position(ref.text, {
                "text": text,
                "frame_end": block_strips.background.frame_final_end
            })
            self.update_strip_position(ref.rect, {
                "frame_end": block_strips.background.frame_final_end
            })
            
        # delete other bullets
        for ref in block_strips.bullets[len(block_data.get("summary_bullets", [])):]:
            self.scene.sequence_editor.sequences.remove(ref.meta)
           
        # timeline 
        frame_offset = block_strips.background.frame_final_end
        timeline_data = block_data["timeline"]
        timeline_strips = block_strips.timeline
        
        timeline_strips.title.text.text = timeline_data.get("title", "")
        self.update_strip_position(timeline_strips.title.meta, {
            "frame_start": frame_offset,
            "frame_end": block_strips.audio.frame_final_end
        })
        
        next_important_date_text = timeline_data.get("next_important_date_text", None)
        if next_important_date_text is not None:
            timeline_strips.upcoming_text.text = next_important_date_text
            timeline_strips.upcoming_text.frame_offset_end = 0
            timeline_strips.upcoming_text.frame_offset_start = 0
            timeline_strips.upcoming_text.frame_final_start = frame_offset
            timeline_strips.upcoming_text.frame_final_end = block_strips.audio.frame_final_end

        outro_animation_duration = block_strips.outro_animation.frame_final_duration
        frame_start = block_strips.audio.frame_final_end - 17
        self.update_strip_position(block_strips.outro_animation, {
            "frame_start": frame_start,
            "frame_end": frame_start + block_strips.outro_animation.frame_final_start + outro_animation_duration
        })
        
        for index, stage_text in enumerate(timeline_data.get("bill_process_stages", [])):
            group = timeline_strips.stages[index]
            meta = group.meta
            red = group.red
            circle = group.circle
            line = group.line
            text = group.text
            
            text.text = stage_text
            if index >= timeline_data.get("bill_process_step", 0):
                red.blend_alpha = 0
            self.update_strip_position(meta, {
                "frame_start": timeline_strips.title.meta.frame_final_start + 17,
                "frame_end": block_strips.audio.frame_final_end
            })
            
            self.update_strip_position(red, {
                "frame_end": block_strips.audio.frame_final_end
            })
            
            self.update_strip_position(text, {
                "frame_end": block_strips.audio.frame_final_end
            })
            
            self.update_strip_position(line, {
                "frame_end": block_strips.audio.frame_final_end
            })
            
            self.update_strip_position(circle, {
                "frame_end": block_strips.audio.frame_final_end
            })
        
        steps_count = len(timeline_data.get("bill_process_stages", []))
        for strip in timeline_strips.stages[steps_count:]:
            strip.meta.blend_alpha = 0
        # hide last stage line
        timeline_strips.stages[steps_count-1].line.blend_alpha = 0
        
        return block_strips.audio.frame_final_end - 1 + 7 - 1
