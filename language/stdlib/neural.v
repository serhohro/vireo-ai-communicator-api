// ============================================================
// STANDARD LIBRARY: NEURAL NETWORKS
// ============================================================
// Version: 3.0.0
// ============================================================

// ============================================================
// МОДЕЛІ
// ============================================================

// Створення моделі
fn create_model(name) {
    return {
        name: name,
        layers: [],
        loss: None,
        optimizer: None,
        metrics: [],
        compiled: false,
        trained: false
    }
}

// Додавання шару
fn add_layer(model, layer) {
    model.layers.append(layer)
    return model
}

// Компіляція моделі
fn compile(model, loss, optimizer, metrics=[]) {
    model.loss = loss
    model.optimizer = optimizer
    model.metrics = metrics
    model.compiled = true
    return model
}

// ============================================================
// ШАРИ
// ============================================================

// Dense шар
fn Dense(units, activation=None) {
    return {
        type: "dense",
        units: units,
        activation: activation
    }
}

// Conv2D шар
fn Conv2D(filters, kernel_size, activation=None) {
    return {
        type: "conv2d",
        filters: filters,
        kernel_size: kernel_size,
        activation: activation
    }
}

// LSTM шар
fn LSTM(units, return_sequences=false) {
    return {
        type: "lstm",
        units: units,
        return_sequences: return_sequences
    }
}

// Dropout шар
fn Dropout(rate) {
    return {
        type: "dropout",
        rate: rate
    }
}

// BatchNorm шар
fn BatchNorm() {
    return {
        type: "batch_norm"
    }
}

// Flatten шар
fn Flatten() {
    return {
        type: "flatten"
    }
}

// ============================================================
// АКТИВАЦІЇ
// ============================================================

fn ReLU() { return "relu" }
fn Sigmoid() { return "sigmoid" }
fn Tanh() { return "tanh" }
fn Softmax() { return "softmax" }
fn LeakyReLU(alpha=0.01) { return {"type": "leaky_relu", "alpha": alpha} }
fn ELU(alpha=1.0) { return {"type": "elu", "alpha": alpha} }
fn GELU() { return "gelu" }

// ============================================================
// ФУНКЦІЇ ВТРАТ
// ============================================================

fn CrossEntropy() { return "cross_entropy" }
fn MSE() { return "mse" }
fn MAE() { return "mae" }
fn Huber(delta=1.0) { return {"type": "huber", "delta": delta} }
fn BinaryCrossEntropy() { return "binary_cross_entropy" }

// ============================================================
// ОПТИМІЗАТОРИ
// ============================================================

fn Adam(lr=0.001, beta1=0.9, beta2=0.999) {
    return {
        type: "adam",
        lr: lr,
        beta1: beta1,
        beta2: beta2
    }
}

fn SGD(lr=0.01, momentum=0.0) {
    return {
        type: "sgd",
        lr: lr,
        momentum: momentum
    }
}

fn RMSprop(lr=0.001, rho=0.9) {
    return {
        type: "rmsprop",
        lr: lr,
        rho: rho
    }
}

// ============================================================
// НАВЧАННЯ
// ============================================================

// Навчання моделі
fn train(model, data, epochs, batch_size) {
    if !model.compiled {
        return error("Model not compiled")
    }
    
    let history = []
    for epoch in range(epochs) {
        let loss = train_epoch(model, data, batch_size)
        history.append({
            epoch: epoch,
            loss: loss
        })
    }
    
    model.trained = true
    return history
}

// Навчання одного епоху
fn train_epoch(model, data, batch_size) {
    let total_loss = 0.0
    let batches = split_batches(data, batch_size)
    
    for batch in batches {
        let loss = train_batch(model, batch)
        total_loss = total_loss + loss
    }
    
    return total_loss / length(batches)
}

// ============================================================
// ПРОГНОЗУВАННЯ
// ============================================================

// Прогнозування
fn predict(model, input) {
    if !model.trained {
        return error("Model not trained")
    }
    
    return forward_pass(model, input)
}

// Оцінка
fn evaluate(model, test_data) {
    if !model.trained {
        return error("Model not trained")
    }
    
    let predictions = []
    let labels = []
    
    for sample in test_data {
        let pred = predict(model, sample.input)
        predictions.append(pred)
        labels.append(sample.label)
    }
    
    return calculate_metrics(model.metrics, predictions, labels)
}

// ============================================================
// ЗБЕРЕЖЕННЯ/ЗАВАНТАЖЕННЯ
// ============================================================

// Збереження моделі
fn save_model(model, path) {
    return File.save(path, model)
}

// Завантаження моделі
fn load_model(path) {
    return File.load(path)
}