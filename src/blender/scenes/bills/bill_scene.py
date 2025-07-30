from ...segments.content_segments import OpeningSegment, ClosingSegment, ContentSegment

class BillScene:
    def __init__(self, scene=None):
        self.scene = scene
        
        self.opening_segment = None
        self.closing_segment = None
        self.content_segments = []
        self.n_block_segments = 0
    
    def create_scene(self, data):
        # blue background
        channel = 1
        
        self.blue_background = self.scene.sequence_editor.sequences.new_effect(
            name="blue_background",
            type='COLOR',
            channel=channel,
            frame_start=0,
            frame_end=1
        )
        self.blue_background.color = (0.015686, 0.137255, 0.235294)
        
        
        channel = channel + 1
        self.opening_segment = OpeningSegment(scene=self.scene, data=data["opening"], channel=channel)
        
        offset = 7
        frame_start = self.opening_segment.frame_end + offset
        channel = self.opening_segment.last_channel + 1
        
        # content segments
        frame_current = frame_start
        content_segments_data = data.get("segments", [])
        self.n_block_segments = len(content_segments_data)
        for index in range(0, self.n_block_segments):
            content_segment = ContentSegment(
                scene=self.scene, 
                frame_start=frame_current,
                first_channel=channel,
                data=content_segments_data[index],
                index=index
            )
            
            self.content_segments.append(content_segment)
            channel = content_segment.last_channel + 1
            
            frame_current = content_segment.frame_end
                
        self.closing_segment = ClosingSegment(scene=self.scene, data=data["closing"], channel=channel, frame_start=frame_current)
        
        self.blue_background.frame_final_end = self.closing_segment.frame_end