from ..scene import SceneElements
class TimelineStageGroup:
    def __init__(self, meta=None, line=None, text=None, red=None, circle=None):
        self.meta = meta
        self.line = line
        self.text = text
        self.red = red
        self.circle = circle

class TextGroup:
    def __init__(self, meta=None, text=None):
        self.meta = meta
        self.text = text
        
class BulletGroup:
    def __init__(self, meta=None, text=None, rect=None):
        self.meta = meta # meta container
        self.text = text # text displayed in the bullet
        self.rect = rect # rectangle background for the bullet text
        
class TimelineGroup:
    def __init__(self, title=None, upcoming_text=None, stages=[]):
        self.title = title # title text displayed in the timeline
        self.upcoming_text = upcoming_text # text indicating the upcoming stage date
        self.stages = stages # list of meta elements for each stage in the timeline

class BillBlockGroup:
    def __init__(self, index=0, background=None, outro_animation=None, outro_audio=None, title=None, audio=None, bullets=[], timeline=TimelineGroup()):
        self.index = index  # Position of the block in the overall scene

        self.background = background  # Background video clip for the block
        self.outro_animation = outro_animation  # Animation shown at the end of the block
        self.outro_audio = outro_audio  # Audio played during the outro animation
        self.title = title  # Title text displayed in the block
        self.bullets = bullets  # List of bullet points related to the bill
        self.timeline = timeline  # Timeline indicating the current stage of the bill
        self.audio = audio  # Narration voiceover explaining the bill


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
