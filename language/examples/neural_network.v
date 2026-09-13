// ============================================================
// NEURAL NETWORK IN VIREO
// ============================================================

// Define Model
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dropout(0.2)
    layer Dense(128, 64)
    activation ReLU
    layer Dense(64, 10)
    activation Softmax
    loss CrossEntropy
    optimizer Adam(lr=0.001)
}

// Train
train MNIST {
    data = "mnist"
    epochs = 10
    batch_size = 64
    lr = 0.001
}

// Predict
predict MNIST {
    data = "test"
}

// Evaluate
evaluate MNIST {
    data = "test"
    metrics = [accuracy, precision, recall, f1]
}

// Save Model
save MNIST {
    path = "models/mnist.vireo"
}

// Load Model
load MNIST {
    path = "models/mnist.vireo"
}