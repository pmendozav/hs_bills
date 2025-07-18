from ..scene import Scene
from . import bill_scene_types as types


class BillScene(Scene):
    def __init__(self, scene=None, n_blocks=1):
        self.elements = types.BillSceneElements()
        
        super().__init__(scene=scene, n_blocks=n_blocks)
        
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
                text=next((s for s in bullet_strips if s.name == f"group.{index}.bullet.{i}.text"), None)
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
            
            stage = types.TimelineStageGroup(meta=meta, line=line, text=text, red=red)
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

    def update_opening_strips(self):
        pass

    def update_closing_strips(self):
        pass

    def update_one_block_strips(self, index, offset=0):
        last_frame = 0
        return last_frame
