import bpy

class Scene:
    def __init__(self, scene=None, n_blocks=1):
        self.scene = scene
        self.name = scene.name if scene else "unknown"
        self.strips_by_type = {}
        self.all_strips = []
        self.n_blocks = n_blocks

        self.parse()

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
        pass

    def parse_closing_strips(self):
        pass

    def parse_one_block_strips(self, index):
        pass
    
    def parse_block_strips(self):
        for index in range(1, self.n_blocks + 1):
            self.parse_one_block_strips(index)
    
    def update_strips_data(self):
        self.update_opening_strips()
        self.update_closing_strips()
        last_frame = 0
        for index in range(1, self.n_blocks):
            last_frame = self.update_one_block_strips(index, last_frame=last_frame)
            
    def find_strip_by_name(self, name, strips=None):
        for strip in (strips if strips else self.all_strips):
            if getattr(strip, "name", "") == name:
                return strip
        return None