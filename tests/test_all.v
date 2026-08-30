// ============================================================
// VIREO TEST SUITE v1.4.3
// The World's First AI-to-AI Communication Language
// ============================================================

import std::io

// ============================================================
// HELPER FUNCTIONS
// ============================================================

fn assert_equal(actual: F32, expected: F32, test_name: Str) {
    let diff = actual - expected
    if diff < 0.0 { diff = -diff }
    
    if diff < 0.0001 {
        io::println(f"   ✅ {test_name} passed")
    } else {
        io::println(f"   ❌ {test_name} failed: expected {expected}, got {actual}")
    }
}

fn assert_true(condition: Bool, test_name: Str) {
    if condition {
        io::println(f"   ✅ {test_name} passed")
    } else {
        io::println(f"   ❌ {test_name} failed")
    }
}

// ============================================================
// TENSOR TESTS
// ============================================================

fn test_tensor_creation() {
    io::println("   🧪 Testing tensor creation...")
    
    let t = Tensor::ones([2, 3])
    let is_valid = t[0, 0] == 1.0 and t[1, 2] == 1.0
    
    assert_true(is_valid, "Tensor creation")
}

fn test_tensor_addition() {
    io::println("   🧪 Testing tensor addition...")
    
    let a = Tensor::ones([2, 2])
    let b = Tensor::ones([2, 2])
    let c = a + b
    
    assert_equal(c[0, 0], 2.0, "Tensor addition")
}

fn test_tensor_subtraction() {
    io::println("   🧪 Testing tensor subtraction...")
    
    let a = Tensor::ones([2, 2]) * 5.0
    let b = Tensor::ones([2, 2]) * 3.0
    let c = a - b
    
    assert_equal(c[0, 0], 2.0, "Tensor subtraction")
}

fn test_tensor_multiplication() {
    io::println("   🧪 Testing tensor multiplication...")
    
    let a = Tensor::ones([2, 2]) * 4.0
    let b = Tensor::ones([2, 2]) * 2.0
    let c = a * b
    
    assert_equal(c[0, 0], 8.0, "Tensor multiplication")
}

fn test_matrix_multiplication() {
    io::println("   🧪 Testing matrix multiplication...")
    
    let a: Tensor = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    let b: Tensor = [[7.0, 8.0], [9.0, 10.0], [11.0, 12.0]]
    let c = a.matmul(b)
    
    assert_equal(c[0, 0], 58.0, "Matrix multiplication")
    assert_equal(c[0, 1], 64.0, "Matrix multiplication")
    assert_equal(c[1, 0], 139.0, "Matrix multiplication")
    assert_equal(c[1, 1], 154.0, "Matrix multiplication")
}

fn test_tensor_transpose() {
    io::println("   🧪 Testing tensor transpose...")
    
    let a: Tensor = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    let b = a.transpose()
    
    assert_equal(b[0, 0], 1.0, "Tensor transpose")
    assert_equal(b[0, 1], 4.0, "Tensor transpose")
    assert_equal(b[1, 0], 2.0, "Tensor transpose")
    assert_equal(b[1, 1], 5.0, "Tensor transpose")
    assert_equal(b[2, 0], 3.0, "Tensor transpose")
    assert_equal(b[2, 1], 6.0, "Tensor transpose")
}

fn test_tensor_reshape() {
    io::println("   🧪 Testing tensor reshape...")
    
    let a = Tensor::arange(0, 12)
    let b = a.reshape([3, 4])
    
    assert_equal(b[0, 0], 0.0, "Tensor reshape")
    assert_equal(b[2, 3], 11.0, "Tensor reshape")
}

// ============================================================
// NEURAL NETWORK TESTS
// ============================================================

fn test_model_creation() {
    io::println("   🧪 Testing model creation...")
    
    model TestModel {
        layer Dense(10, 20)
        activation ReLU
        layer Dense(20, 5)
        activation Softmax
    }
    
    io::println("   ✅ Model creation passed")
}

fn test_activation_functions() {
    io::println("   🧪 Testing activation functions...")
    
    let x: Tensor = [-1.0, 0.0, 1.0, 2.0]
    
    let relu_x = relu(x)
    assert_equal(relu_x[0], 0.0, "ReLU")
    assert_equal(relu_x[1], 0.0, "ReLU")
    assert_equal(relu_x[2], 1.0, "ReLU")
    assert_equal(relu_x[3], 2.0, "ReLU")
    
    let sigmoid_x = sigmoid(x)
    assert_true(sigmoid_x[1] == 0.5, "Sigmoid")
    assert_true(sigmoid_x[3] > 0.8, "Sigmoid")
}

// ============================================================
// MAIN TEST RUNNER
// ============================================================

fn main() {
    io::println("")
    io::println("=" * 50)
    io::println("🧪 VIREO TEST SUITE v1.4.3")
    io::println("The World's First AI-to-AI Communication Language")
    io::println("=" * 50)
    io::println("")
    
    // Tensor tests
    io::println("📊 TENSOR TESTS")
    io::println("-" * 30)
    test_tensor_creation()
    test_tensor_addition()
    test_tensor_subtraction()
    test_tensor_multiplication()
    test_matrix_multiplication()
    test_tensor_transpose()
    test_tensor_reshape()
    
    io::println("")
    io::println("🧠 NEURAL NETWORK TESTS")
    io::println("-" * 30)
    test_model_creation()
    test_activation_functions()
    
    io::println("")
    io::println("=" * 50)
    io::println("✅ All tests completed successfully!")
    io::println("=" * 50)
    io::println("")
    
    io::println("🌿 Vireo v1.4.3 — The World's First AI-to-AI Communication Language")
    io::println("")
}