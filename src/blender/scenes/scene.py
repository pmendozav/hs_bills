import bpy

from .scene_types import SceneElements

def get_last_frame(strip):
    return strip.frame_final_end + (strip.frame_final_start if strip.frame_final_start is not None else 0)
    
class Scene:
    def __init__(self, scene=None, n_blocks=1):
        self.scene = scene
        self.fps = scene.render.fps / scene.render.fps_base
        self.name = scene.name if scene else "unknown"
        self.strips_by_type = {}
        self.all_strips = []
        self.n_blocks = n_blocks
        self.elements = SceneElements()

    def setup(self):
        pass

    def render(self, output_path):
        pass

    def parse(self, scene=None):
        scene = scene or self.scene
        if not scene:
            return

        self.strips_by_type = {}
        self.all_strips = []

        sequence_editor = scene.sequence_editor
        if not sequence_editor:
            return

        for seq in sequence_editor.sequences_all:
            self.all_strips.append(seq)
            strip_type = seq.type
            self.strips_by_type.setdefault(strip_type, []).append(seq)
        
        self.parse_opening_strips()
        self.parse_closing_strips()
        self.parse_block_strips()

    def get_image_strips(self):
        return self.strips_by_type.get('IMAGE', [])
    
    def get_text_strips(self):
        return self.strips_by_type.get('TEXT', [])

    def get_audio_strips(self):
        return self.strips_by_type.get('SOUND', [])

    def get_movie_strips(self):
        return self.strips_by_type.get('MOVIE', [])

    def get_meta_strips(self):
        return self.strips_by_type.get('META', [])
    
    def get_strip_by_id(self, strip_id):
       for strip in self.all_strips:
           if getattr(strip, "name", None) == strip_id:
               return strip
       return None

    def parse_opening_strips(self):
        raise NotImplementedError("This method should be implemented in subclasses")

    def parse_closing_strips(self):
        raise NotImplementedError("This method should be implemented in subclasses")
    
    def parse_one_block_strips(self, index):
        raise NotImplementedError("This method should be implemented in subclasses")
    
    def parse_block_strips(self):
        for index in range(1, self.n_blocks + 1):
            self.parse_one_block_strips(index)

    ''' Assume that the opening duration is based on the background strip's duration. Also a '''
    def update_opening_strips(self, data=None, config=None):
        opening = self.elements.opening
        bg = next((strip for strip in opening.values() if "background" in strip.name and strip.type == 'MOVIE'), None)
        return get_last_frame(bg) if bg else 0

    ''' do not update noghing, only calculate the last frame of all the closing strips '''
    def update_closing_strips(self, data=None, config=None, start_frame=0):
        closing = self.elements.closing
        last_frame = max(get_last_frame(strip) for strip in closing.values())
        return last_frame if isinstance(last_frame, int) else 0

    def update_one_block_strips(self, index, start_frame=0, data=None, config=None):
        pass
    
    def update(self, data=None, config=None):
        last_frame = 0
        last_frame = self.update_opening_strips(data=data, config=config)
        for index in range(1, self.n_blocks):
            last_frame = self.update_one_block_strips(index=index, start_frame=last_frame, data=data, config=config)
            # return 0
        last_frame = self.update_closing_strips(data=data, config=config, start_frame=last_frame)
        return last_frame

    def find_strip_by_name(self, name, strips=None):
        for strip in (strips if strips else self.all_strips):
            if getattr(strip, "name", "") == name:
                return strip
        return None