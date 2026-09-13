# ============================================================
# VIREO VISION EXTENSIONS
# Computer Vision operations
# ============================================================

VISION_GRAMMAR = """
// ============================================================
// VISION EXTENSIONS GRAMMAR
// ============================================================

vision_op: "image" "." operation "(" [params] ")"

operation: "resize" | "crop" | "rotate" | "flip"
         | "grayscale" | "blur" | "edges" | "sharpen"
         | "detect_objects" | "classify" | "segment"
         | "detect_faces" | "read_text" | "enhance"
         | "normalize" | "augment" | "extract_features"
         | "optical_flow" | "depth_estimation" | "pose_estimation"

params: param ["," param]*
param: IDENTIFIER "=" value

value: NUMBER
     | STRING
     | "true" | "false"
     | array

vision_model: "vision_model" IDENTIFIER block

vision_model_layer: "backbone" IDENTIFIER
                  | "head" IDENTIFIER
                  | "pretrained" STRING
"""


class VisionParser:
    """Parser for Vision extensions."""
    
    def __init__(self):
        self.grammar = VISION_GRAMMAR
    
    def parse_image_op(self, op: str, params: dict) -> dict:
        return {"type": "vision", "op": op, "params": params}
    
    def parse_resize(self, width: int, height: int) -> dict:
        return {"type": "resize", "width": width, "height": height}
    
    def parse_crop(self, x: int, y: int, w: int, h: int) -> dict:
        return {"type": "crop", "x": x, "y": y, "w": w, "h": h}
    
    def parse_detect_objects(self, model: str = "yolo") -> dict:
        return {"type": "detect_objects", "model": model}
    
    def parse_classify(self, model: str = "resnet") -> dict:
        return {"type": "classify", "model": model}


vision_grammar = VISION_GRAMMAR