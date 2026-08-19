// ============================================================
// IMAGE EXAMPLE - COMPUTER VISION ON VIREO
// ============================================================

module examples::image_example

import std::io

// ============================================================
// SIMPLE IMAGE PROCESSING
// ============================================================

pub fn process_image(image: Tensor<F32, [3, 224, 224]>) -> Tensor<F32, [1, 1000]> {
    @neural
    fn image_classifier(input: Tensor<F32, [1, 3, 224, 224]>) -> Tensor<F32, [1, 1000]> {
        let x = conv2d(input, 64, 3, stride=1, padding=1)
        let x = batch_norm(x)
        let x = relu(x)
        let x = maxpool2d(x, 2, stride=2)
        
        let x = conv2d(x, 128, 3, stride=1, padding=1)
        let x = batch_norm(x)
        let x = relu(x)
        let x = maxpool2d(x, 2, stride=2)
        
        let x = conv2d(x, 256, 3, stride=1, padding=1)
        let x = batch_norm(x)
        let x = relu(x)
        let x = maxpool2d(x, 2, stride=2)
        
        let x = x.flatten()
        let x = dense(x, 512, ReLU)
        let x = dropout(x, 0.5)
        let x = dense(x, 256, ReLU)
        let x = dropout(x, 0.5)
        
        return dense(x, 1000, Softmax)
    }
    
    return image_classifier(image)
}

// ============================================================
// DEMO
// ============================================================

pub fn demo_image_processing() {
    io::println("   🖼️ Creating sample image...")
    
    let image: Tensor<F32, [1, 3, 224, 224]> = Tensor::random()
    
    io::println("   📐 Image shape: 1x3x224x224")
    io::println("   🧠 Running classification...")
    
    let result = process_image(image)
    let max_prob = result.max()
    let predicted_class = result.argmax()
    
    io::println(f"   🎯 Predicted class: {predicted_class}")
    io::println(f"   📊 Confidence: {max_prob * 100:.2f}%")
}

// ============================================================
// EXPORT
// ============================================================

export process_image, demo_image_processing