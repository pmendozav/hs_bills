import bpy

class BlenderFile:
    def __init__(self, filepath=None):
        self.filepath = filepath

    def save(self, filepath=None):
        bpy.ops.wm.save_mainfile(filepath=filepath)
        return filepath

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

    def render(self, scene=None, frame_end=None, output_path=None):
        if scene is not None:
            bpy.context.window.scene = scene
            
        if frame_end is not None:
            frame_end = int(scene.frame_end)
        
        bpy.context.scene.render.use_sequencer = True
        scene.render.fps_base = 1
        # scene.render.fps = 30
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.gopsize = 60
        scene.render.ffmpeg.constant_rate_factor = "MEDIUM"  # MEDIUM,LOW
        
        scene.frame_start = 1
        scene.frame_end = frame_end
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(animation=True, write_still=False)

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
    
    def get_scene(self, name):
        return next(s for s in bpy.data.scenes if s.name == name)