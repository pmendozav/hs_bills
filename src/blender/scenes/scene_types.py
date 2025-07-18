class SceneElements:
    def __init__(self):
        self.opening = {}
        self.closing = {}
        self.blocks = []

    def set_opening(self, opening):
        self.opening = opening
        
    def set_closing(self, closing):
        self.closing = closing

    def set_blocks(self, blocks):
        self.blocks = blocks