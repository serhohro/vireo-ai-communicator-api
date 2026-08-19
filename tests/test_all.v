// ============================================================
// VIREO TEST SUITE
// ============================================================

import testing
import std::io

// ============================================================
// TENSOR TESTS
// ============================================================

fn test_tensor_creation() {
    let t = Tensor<F32, [2, 3]>::ones()
    assert(t[0, 0] == 1.0)
    assert(t[1, 2] == 1.0)
}

fn test_tensor_addition() {
    let a = Tensor<F32, [2, 2]>::ones()
    let b = Tensor<F32, [2, 2]>::ones()
    let c = a + b
    assert(c[0, 0] == 2.0)
}

fn test_matrix_multiplication() {
    let a: Tensor<F32, [2, 3]> = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0]
    ]
    let b: Tensor<F32, [3, 2]> = [
        [7.0, 8.0],
        [9.0, 10.0],
        [11.0, 12.0]
    ]
    let c = a.matmul(b)
    assert(c[0, 0] == 58.0)
}

// ============================================================
// RUN ALL TESTS
// ============================================================

fn main() {
    io::println("🧪 Running Vireo Test Suite...")
    io::println("")
    
    testing::run_test("Tensor Creation", test_tensor_creation)
    testing::run_test("Tensor Addition", test_tensor_addition)
    testing::run_test("Matrix Multiplication", test_matrix_multiplication)
    
    io::println("")
    io::println("✅ All tests passed!")
}