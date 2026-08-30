// ============================================================
// STANDARD LIBRARY: MATHEMATICAL FUNCTIONS
// ============================================================
// Version: 1.4.3
// ============================================================

// ============================================================
// БАЗОВІ ОПЕРАЦІЇ
// ============================================================

fn add(a, b) {
    return a + b
}

fn sub(a, b) {
    return a - b
}

fn mul(a, b) {
    return a * b
}

fn div(a, b) {
    if b == 0 {
        return error("Division by zero")
    }
    return a / b
}

fn pow(a, b) {
    return a ** b
}

fn mod(a, b) {
    if b == 0 {
        return error("Modulo by zero")
    }
    return a % b
}

// ============================================================
// ТРИГОНОМЕТРІЯ
// ============================================================

fn sin(x) {
    return math.sin(x)
}

fn cos(x) {
    return math.cos(x)
}

fn tan(x) {
    return math.tan(x)
}

fn asin(x) {
    return math.asin(x)
}

fn acos(x) {
    return math.acos(x)
}

fn atan(x) {
    return math.atan(x)
}

fn atan2(y, x) {
    return math.atan2(y, x)
}

// ============================================================
// ГІПЕРБОЛІЧНІ ФУНКЦІЇ
// ============================================================

fn sinh(x) {
    return math.sinh(x)
}

fn cosh(x) {
    return math.cosh(x)
}

fn tanh(x) {
    return math.tanh(x)
}

// ============================================================
// ЕКСПОНЕНЦІЙНІ ТА ЛОГАРИФМІЧНІ
// ============================================================

fn exp(x) {
    return math.exp(x)
}

fn log(x) {
    if x <= 0 {
        return error("Logarithm of non-positive number")
    }
    return math.log(x)
}

fn log10(x) {
    if x <= 0 {
        return error("Logarithm of non-positive number")
    }
    return math.log10(x)
}

fn log2(x) {
    if x <= 0 {
        return error("Logarithm of non-positive number")
    }
    return math.log2(x)
}

fn sqrt(x) {
    if x < 0 {
        return error("Square root of negative number")
    }
    return math.sqrt(x)
}

fn cbrt(x) {
    return math.cbrt(x)
}

// ============================================================
// СТАТИСТИЧНІ ФУНКЦІЇ
// ============================================================

fn max(a, b) {
    if a > b {
        return a
    }
    return b
}

fn min(a, b) {
    if a < b {
        return a
    }
    return b
}

fn abs(x) {
    if x < 0 {
        return -x
    }
    return x
}

fn ceil(x) {
    return math.ceil(x)
}

fn floor(x) {
    return math.floor(x)
}

fn round(x) {
    return math.round(x)
}

fn sign(x) {
    if x > 0 {
        return 1
    }
    if x < 0 {
        return -1
    }
    return 0
}

// ============================================================
// СТАТИСТИКА
// ============================================================

fn sum(list) {
    let total = 0
    for item in list {
        total = total + item
    }
    return total
}

fn mean(list) {
    if length(list) == 0 {
        return error("Empty list")
    }
    return sum(list) / length(list)
}

fn median(list) {
    let sorted = sort(list)
    let n = length(sorted)
    if n % 2 == 1 {
        return sorted[n / 2]
    }
    return (sorted[n/2 - 1] + sorted[n/2]) / 2
}

fn variance(list) {
    let m = mean(list)
    let total = 0
    for item in list {
        total = total + (item - m) ** 2
    }
    return total / length(list)
}

fn stddev(list) {
    return sqrt(variance(list))
}

fn min_value(list) {
    let m = list[0]
    for item in list {
        if item < m {
            m = item
        }
    }
    return m
}

fn max_value(list) {
    let m = list[0]
    for item in list {
        if item > m {
            m = item
        }
    }
    return m
}

// ============================================================
// ЛІНІЙНА АЛГЕБРА
// ============================================================

fn dot_product(a, b) {
    if length(a) != length(b) {
        return error("Vectors must have same length")
    }
    let result = 0
    for i in range(length(a)) {
        result = result + a[i] * b[i]
    }
    return result
}

fn vector_norm(v) {
    return sqrt(sum(v * v))
}

fn cross_product(a, b) {
    if length(a) != 3 || length(b) != 3 {
        return error("Cross product requires 3D vectors")
    }
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ]
}

// ============================================================
// КОНСТАНТИ
// ============================================================

let PI = 3.141592653589793
let E = 2.718281828459045
let TAU = 6.283185307179586

// ============================================================
// КОНВЕРСІЇ
// ============================================================

fn radians(degrees) {
    return degrees * PI / 180
}

fn degrees(radians) {
    return radians * 180 / PI
}

fn to_int(x) {
    return int(x)
}

fn to_float(x) {
    return float(x)
}

fn to_string(x) {
    return str(x)
}

// ============================================================
// ПЕРЕВІРКИ
// ============================================================

fn is_number(x) {
    return type(x) == "int" || type(x) == "float"
}

fn is_integer(x) {
    return type(x) == "int"
}

fn is_float(x) {
    return type(x) == "float"
}

fn is_positive(x) {
    return x > 0
}

fn is_negative(x) {
    return x < 0
}

fn is_zero(x) {
    return x == 0
}

fn is_even(x) {
    return x % 2 == 0
}

fn is_odd(x) {
    return x % 2 == 1
}