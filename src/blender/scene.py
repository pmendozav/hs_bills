import bpy

class Scene:
    def __init__(self, scene=None, n_blocks=1):
        self.scene = scene
        self.strips_by_type = {}
        self.all_strips = []
        self.meta_strips = []
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
        self.meta_strips = []


        sequence_editor = scene.sequence_editor
        if not sequence_editor:
            return

        for seq in sequence_editor.sequences_all:
            self.all_strips.append(seq)
            strip_type = seq.type
            self.strips_by_type.setdefault(strip_type, []).append(seq)
            if strip_type == 'META':
                self.meta_strips.append(seq)

    def get_image_strips(self):
        return self.strips_by_type.get('IMAGE', [])

    def get_audio_strips(self):
        return self.strips_by_type.get('SOUND', [])

    def get_movie_strips(self):
        return self.strips_by_type.get('MOVIE', [])

    def get_meta_strips(self):
        return self.meta_strips
    
    def get_strip_by_id(self, strip_id):
       for strip in self.all_strips:
           if getattr(strip, "name", None) == strip_id:
               return strip
       return None

    def parse_opening_strips(self):
        pass

    def parse_closing_strips(self):
        pass

    def parse_one_block(self, index):
        pass
    
    def parse_blocks(self):
        for index in range(1, self.n_blocks):
            self.parse_one_block_strips(index)
    
    def update_strips_data(self):
        self.update_opening_strips()
        self.update_closing_strips()
        last_frame = 0
        for index in range(1, self.n_blocks):
            last_frame = self.update_one_block_strips(index, last_frame=last_frame)