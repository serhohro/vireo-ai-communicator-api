// ============================================================
// STANDARD LIBRARY: TENSOR OPERATIONS
// ============================================================
// Version: 1.4.3
// ============================================================

// ============================================================
// ТЕНЗОРНІ ОПЕРАЦІЇ
// ============================================================

// Створення тензора
fn tensor(data) {
    return Tensor(data)
}

// Отримання форми
fn shape(t) {
    return t.shape
}

// Отримання розміру
fn size(t) {
    return t.size()
}

// ============================================================
// АРИФМЕТИЧНІ ОПЕРАЦІЇ
// ============================================================

fn add(t1, t2) {
    return t1 + t2
}

fn sub(t1, t2) {
    return t1 - t2
}

fn mul(t1, t2) {
    return t1 * t2
}

fn div(t1, t2) {
    return t1 / t2
}

fn matmul(t1, t2) {
    return t1.matmul(t2)
}

// ============================================================
// ПЕРЕТВОРЕННЯ
// ============================================================

fn transpose(t) {
    return t.transpose()
}

fn reshape(t, new_shape) {
    return t.reshape(new_shape)
}

fn flatten(t) {
    return t.flatten()
}

fn permute(t, dims) {
    return t.permute(dims)
}

// ============================================================
// РЕДУКЦІЇ
// ============================================================

fn sum(t, axis=None) {
    return t.sum(axis)
}

fn mean(t, axis=None) {
    return t.mean(axis)
}

fn max(t, axis=None) {
    return t.max(axis)
}

fn min(t, axis=None) {
    return t.min(axis)
}

fn std(t, axis=None) {
    return t.std(axis)
}

fn var(t, axis=None) {
    return t.var(axis)
}

// ============================================================
// ПОЕЛЕМЕНТНІ ОПЕРАЦІЇ
// ============================================================

fn exp(t) {
    return t.exp()
}

fn log(t) {
    return t.log()
}

fn sqrt(t) {
    return t.sqrt()
}

fn pow(t, power) {
    return t ** power
}

fn abs(t) {
    return t.abs()
}

fn sign(t) {
    return t.sign()
}

fn clip(t, min_val, max_val) {
    return t.clip(min_val, max_val)
}

// ============================================================
// ПІДСТАНОВКИ
// ============================================================

fn slice(t, start, end) {
    return t[start:end]
}

fn index(t, idx) {
    return t[idx]
}

fn concat(t1, t2, axis=0) {
    return t1.concat(t2, axis)
}

fn stack(tensors, axis=0) {
    return stack(tensors, axis)
}

// ============================================================
// ПЕРЕВІРКИ
// ============================================================

fn is_tensor(x) {
    return type(x) == "Tensor"
}

fn is_same_shape(t1, t2) {
    return t1.shape == t2.shape
}

fn is_square(t) {
    return length(t.shape) == 2 && t.shape[0] == t.shape[1]
}

fn is_symmetric(t) {
    return t == t.transpose()
}

// ============================================================
// КОНВЕРСІЇ
// ============================================================

fn to_list(t) {
    return t.to_list()
}

fn to_numpy(t) {
    return t.to_numpy()
}

fn to_pytorch(t) {
    return t.to_pytorch()
}

fn from_numpy(arr) {
    return Tensor(arr)
}

fn from_pytorch(pt_tensor) {
    return Tensor(pt_tensor)
}

// ============================================================
// ДОДАТКОВІ ОПЕРАЦІЇ
// ============================================================

fn ones(shape) {
    return Tensor.ones(shape)
}

fn zeros(shape) {
    return Tensor.zeros(shape)
}

fn eye(n) {
    return Tensor.eye(n)
}

fn random(shape) {
    return Tensor.random(shape)
}

fn normal(shape, mean=0, std=1) {
    return Tensor.normal(shape, mean, std)
}

fn uniform(shape, low=0, high=1) {
    return Tensor.uniform(shape, low, high)
}