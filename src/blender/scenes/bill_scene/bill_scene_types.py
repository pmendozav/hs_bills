from ..scene_types import SceneElements
class TimelineStageGroup:
    def __init__(self, meta=None, line=None, text=None, red=None):
        self.meta = meta
        self.line = line
        self.text = text
        self.red = red

class TextGroup:
    def __init__(self, meta=None, text=None):
        self.meta = meta
        self.text = text
        
class BulletGroup:
    def __init__(self, meta=None, text=None):
        self.meta = meta
        self.text = text
        
class TimelineGroup:
    def __init__(self, title=None, upcoming_text=None, stages=[]):
        self.title = title
        self.upcoming_text = upcoming_text
        self.stages = stages

class BillBlockGroup:
    def __init__(self, index=0, background=None, outro_animation=None, outro_audio=None, title=None, audio=None, bullets=[], timeline=TimelineGroup()):
        self.index = index

        self.background = background
        self.outro_animation = outro_animation
        self.outro_audio = outro_audio
        self.title = title
        self.bullets = bullets
        self.timeline = timeline
        self.audio = audio

class BillSceneElements(SceneElements):
    def __init__(self):
        super().__init__()

    def set_opening(self, bg=None, outro_animation=None, outro_audio=None):
        super().set_opening({
            "background": bg,
            "outro_animation": outro_animation,
            "outro_audio": outro_audio
        })
        
    def set_closing(self, bg=None, audio=None):
        super().set_closing({
            "background": bg,
            "audio": audio
        })

    def set_blocks(self, blocks=None):
        super().set_blocks(blocks)
