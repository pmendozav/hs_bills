import bpy

class BlenderFile:
    def __init__(self, filepath=None):
        self.filepath = filepath

    def read(self, filepath=None):
        path = filepath or self.filepath
        if path:
            bpy.ops.wm.open_mainfile(filepath=path)

    def write(self, filepath=None):
        path = filepath or self.filepath
        if path:
            bpy.ops.wm.save_as_mainfile(filepath=path)
        else:
            bpy.ops.wm.save_mainfile()

    def render(self, output_path):
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)

    def search_by_strip_type(self, strip_type):
        strips = []
        for seq in bpy.context.scene.sequence_editor.sequences_all:
            if seq.type == strip_type:
                strips.append(seq)
        return strips
    
    def search_by_id(self, id, meta=None):
        for seq in bpy.context.scene.sequence_editor.sequences_all:
            if seq.id == id:
                return seq
        return None

    def search_meta_strip(self):
        for seq in bpy.context.scene.sequence_editor.sequences_all:
            if seq.type == 'META':
                return seq
        return None