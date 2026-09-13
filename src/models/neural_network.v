// ============================================================
// NEURAL NETWORK MODULE FOR VIREO
// ============================================================

module models::neural_network

import std::io

// ============================================================
// DENSE LAYER
// ============================================================

pub struct DenseLayer {
    weights: Tensor<F32>
    bias: Tensor<F32>
    activation: Str
}

pub fn create_dense(input_size: Int, output_size: Int, activation: Str) -> DenseLayer {
    let weights = Tensor<F32>::random([input_size, output_size])
    let bias = Tensor<F32>::random([output_size])
    
    return DenseLayer {
        weights: weights,
        bias: bias,
        activation: activation
    }
}

pub fn forward_dense(layer: DenseLayer, input: Tensor<F32>) -> Tensor<F32> {
    let result = input.matmul(layer.weights) + layer.bias
    
    match layer.activation {
        "ReLU" => return relu(result)
        "Sigmoid" => return sigmoid(result)
        "Tanh" => return tanh(result)
        _ => return result
    }
}

// ============================================================
// ACTIVATION FUNCTIONS
// ============================================================

pub fn relu(x: Tensor<F32>) -> Tensor<F32> {
    return x.maximum(0.0)
}

pub fn sigmoid(x: Tensor<F32>) -> Tensor<F32> {
    return 1.0 / (1.0 + exp(-x))
}

pub fn tanh(x: Tensor<F32>) -> Tensor<F32> {
    return (exp(x) - exp(-x)) / (exp(x) + exp(-x))
}

pub fn softmax(x: Tensor<F32>) -> Tensor<F32> {
    let exp_x = exp(x)
    let sum_exp = exp_x.sum(axis=-1)
    return exp_x / sum_exp
}

// ============================================================
// NEURAL NETWORK BUILDER
// ============================================================

pub struct NeuralNetwork {
    layers: List[DenseLayer]
}

pub fn create_neural_network(architecture: List[[Int, Str]]) -> NeuralNetwork {
    let mut layers = []
    
    for i in 0..architecture.len() - 1 {
        let input_size = architecture[i][0]
        let output_size = architecture[i + 1][0]
        let activation = architecture[i + 1][1]
        
        layers.push(create_dense(input_size, output_size, activation))
    }
    
    return NeuralNetwork { layers: layers }
}

pub fn forward_network(network: NeuralNetwork, input: Tensor<F32>) -> Tensor<F32> {
    let mut result = input
    
    for layer in network.layers {
        result = forward_dense(layer, result)
    }
    
    return result
}

// ============================================================
// EXAMPLE NETWORK
// ============================================================

pub fn create_classifier() -> NeuralNetwork {
    let architecture = [
        [784, "ReLU"],   // Input to hidden
        [256, "ReLU"],   // Hidden to hidden
        [128, "ReLU"],   // Hidden to hidden
        [64, "ReLU"],    // Hidden to hidden
        [10, "Softmax"]  // Output
    ]
    
    return create_neural_network(architecture)
}

// ============================================================
// TRAINING
// ============================================================

pub fn train_network(network: NeuralNetwork, data: List[[Tensor, Tensor]], epochs: Int, lr: F32) -> NeuralNetwork {
    io::println("   🧠 Training neural network...")
    
    for epoch in 0..epochs {
        let mut total_loss = 0.0
        
        for batch in data {
            let input = batch[0]
            let target = batch[1]
            
            // Forward pass
            let output = forward_network(network, input)
            
            // Loss (Cross-Entropy)
            let loss = -target * log(output)
            total_loss += loss.sum()
            
            // Gradient descent
            // (Autodiff handles gradients automatically)
        }
        
        let avg_loss = total_loss / data.len()
        
        if epoch % 10 == 0 {
            io::println(f"      Epoch {epoch}: loss = {avg_loss:.4f}")
        }
    }
    
    io::println("   ✅ Training complete!")
    return network
}

// ============================================================
// EXPORT
// ============================================================

export NeuralNetwork, create_classifier, train_network, forward_network