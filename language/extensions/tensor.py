# ============================================================
# VIREO TENSOR EXTENSIONS
# Tensor operations
# ============================================================

TENSOR_GRAMMAR = """
// ============================================================
// TENSOR EXTENSIONS GRAMMAR
// ============================================================

tensor_literal: "Tensor" "(" array ")"

tensor_zeros: "zeros" "(" shape ")"
tensor_ones: "ones" "(" shape ")"
tensor_eye: "eye" "(" NUMBER ")"
tensor_random: "random" "(" shape ")"
tensor_normal: "normal" "(" shape ["," NUMBER] ["," NUMBER] ")"
tensor_uniform: "uniform" "(" shape ["," NUMBER] ["," NUMBER] ")"

tensor_op: tensor_add | tensor_sub | tensor_mul | tensor_div
         | tensor_matmul | tensor_transpose | tensor_reshape
         | tensor_flatten | tensor_permute | tensor_sum
         | tensor_mean | tensor_max | tensor_min
         | tensor_std | tensor_var | tensor_clip
         | tensor_exp | tensor_log | tensor_sqrt

tensor_add: expression "+" expression
tensor_sub: expression "-" expression
tensor_mul: expression "*" expression
tensor_div: expression "/" expression
tensor_matmul: expression "." "matmul" "(" expression ")"
tensor_transpose: expression "." "transpose" "(" [dims] ")"
tensor_reshape: expression "." "reshape" "(" shape ")"
tensor_flatten: expression "." "flatten" "(" ")"
tensor_permute: expression "." "permute" "(" dims ")"
tensor_sum: expression "." "sum" "(" [axis] ")"
tensor_mean: expression "." "mean" "(" [axis] ")"
tensor_max: expression "." "max" "(" [axis] ")"
tensor_min: expression "." "min" "(" [axis] ")"
tensor_std: expression "." "std" "(" [axis] ")"
tensor_var: expression "." "var" "(" [axis] ")"
tensor_clip: expression "." "clip" "(" NUMBER "," NUMBER ")"
tensor_exp: expression "." "exp" "(" ")"
tensor_log: expression "." "log" "(" ")"
tensor_sqrt: expression "." "sqrt" "(" ")"

shape: "[" NUMBER ["," NUMBER]* "]"
dims: "[" NUMBER ["," NUMBER]* "]"
axis: NUMBER | "None"

tensor_compare: expression "==" expression
              | expression "!=" expression
              | expression "<" expression
              | expression ">" expression
              | expression "<=" expression
              | expression ">=" expression
"""


class TensorParser:
    """Parser for Tensor extensions."""
    
    def __init__(self):
        self.grammar = TENSOR_GRAMMAR
    
    def parse_tensor(self, data: list) -> dict:
        return {"type": "tensor", "data": data}
    
    def parse_shape(self, shape: list) -> list:
        return shape
    
    def parse_op(self, op_type: str, args: list) -> dict:
        return {"type": "tensor_op", "op": op_type, "args": args}
    
    def parse_zeros(self, shape: list) -> dict:
        return {"type": "zeros", "shape": shape}
    
    def parse_ones(self, shape: list) -> dict:
        return {"type": "ones", "shape": shape}
    
    def parse_eye(self, n: int) -> dict:
        return {"type": "eye", "size": n}
    
    def parse_normal(self, shape: list, mean: float = 0.0, std: float = 1.0) -> dict:
        return {"type": "normal", "shape": shape, "mean": mean, "std": std}
    
    def parse_random(self, shape: list) -> dict:
        return {"type": "random", "shape": shape}


tensor_grammar = TENSOR_GRAMMAR