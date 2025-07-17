from .scene import Scene

class BillScene(Scene):
    def __init__(self, scene=None):
        super().__init__(scene=scene)

    def setup(self):
        pass

    def render(self, output_path):
        pass
    
    def parse(self, scene=None):
        super().parse(scene)
        
        self.parse_opening_strips()
        self.parse_closing_strips()
        self.parse_block_strips()

    def parse_opening_strips(self):
        super().parse_opening_strips()
        pass

    def parse_closing_strips(self):
        super().parse_closing_strips()
        pass

    def parse_one_block_strips(self, index):
        super().parse_one_block_strips(index)
        pass
            
    def update_opening_strips(self):
        pass

    def update_closing_strips(self):
        pass

    def update_one_block_strips(self, index, offset=0):
        last_frame = 0
        return last_frame
