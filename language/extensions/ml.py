# ============================================================
# VIREO ML EXTENSIONS
# Machine Learning constructs
# ============================================================

ML_GRAMMAR = """
// ============================================================
// ML EXTENSIONS GRAMMAR
// ============================================================

model_layer: "layer" layer_type "(" [layer_params] ")"

layer_type: "Dense" | "Conv2D" | "Conv1D" | "LSTM" | "GRU"
          | "Dropout" | "BatchNorm" | "Flatten" | "MaxPool2D"
          | "AveragePool2D" | "GlobalAvgPool" | "Embedding"
          | "Residual" | "Attention" | "MultiHeadAttention"

layer_params: NUMBER ["," NUMBER] ["," NUMBER] ["," NUMBER]

model_activation: "activation" activation_type

activation_type: "ReLU" | "Sigmoid" | "Tanh" | "Softmax"
               | "LeakyReLU" | "ELU" | "GELU" | "Swish"
               | "Mish" | "SiLU" | "HardSwish"

model_loss: "loss" loss_type

loss_type: "CrossEntropy" | "MSE" | "MAE" | "Huber"
         | "BinaryCrossEntropy" | "FocalLoss" | "DiceLoss"
         | "KLDivergence" | "CosineSimilarity"

model_optimizer: "optimizer" optimizer_type ["(" optimizer_params ")"]

optimizer_type: "Adam" | "SGD" | "RMSprop" | "AdamW" | "Lion"
              | "Adamax" | "Nadam" | "RAdam"

optimizer_params: param ["," param]*
param: IDENTIFIER "=" NUMBER

model_metrics: "metrics" "[" metric_list "]"
metric_list: IDENTIFIER ["," IDENTIFIER]*

model_callbacks: "callbacks" "[" callback_list "]"
callback_list: IDENTIFIER ["," IDENTIFIER]*
"""


class MLParser:
    """Parser for ML extensions."""
    
    def __init__(self):
        self.grammar = ML_GRAMMAR
    
    def parse_layer(self, params: dict) -> dict:
        return {"type": params.get("type", "Dense"), "params": params.get("params", [])}
    
    def parse_activation(self, name: str) -> str:
        return name
    
    def parse_loss(self, name: str) -> str:
        return name
    
    def parse_optimizer(self, name: str, params: dict) -> dict:
        return {"name": name, "params": params}
    
    def parse_metrics(self, metrics: list) -> list:
        return metrics
    
    def parse_callbacks(self, callbacks: list) -> list:
        return callbacks


ml_grammar = ML_GRAMMAR