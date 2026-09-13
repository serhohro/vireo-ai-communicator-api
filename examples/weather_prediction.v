// [file name]: examples/weather_prediction.v
// ============================================================
// WEATHER PREDICTION SYSTEM
// Прогнозування погоди з 2 моделями
// ============================================================

// ============================================================
// 1. МОДЕЛЬ ДЛЯ ТЕМПЕРАТУРИ
// ============================================================

model TemperatureModel {
    layer Dense(10, 64)
    activation ReLU
    layer Dropout(0.2)
    layer Dense(64, 32)
    activation ReLU
    layer Dropout(0.2)
    layer Dense(32, 1)
}

// ============================================================
// 2. МОДЕЛЬ ДЛЯ ОПАДІВ
// ============================================================

model PrecipitationModel {
    layer Dense(10, 64)
    activation ReLU
    layer Dropout(0.3)
    layer Dense(64, 32)
    activation ReLU
    layer Dense(32, 1)
    activation Sigmoid
}

// ============================================================
// 3. ФУНКЦІЯ ПРОГНОЗУВАННЯ
// ============================================================

fn weather_forecast(data) {
    let temperature = predict(TemperatureModel, data)
    let precipitation = predict(PrecipitationModel, data)
    
    return {
        temperature: temperature,
        precipitation_probability: precipitation,
        summary: temperature > 25 ? "Warm" : "Cool"
    }
}

// ============================================================
// 4. НАВЧАННЯ МОДЕЛЕЙ
// ============================================================

train TemperatureModel {
    data = "weather_dataset.csv"
    epochs = 50
    batch_size = 32
    lr = 0.001
    optimizer = Adam
}

train PrecipitationModel {
    data = "weather_dataset.csv"
    epochs = 50
    batch_size = 32
    lr = 0.001
    optimizer = Adam
}

// ============================================================
// 5. ПЕРЕДБАЧЕННЯ
// ============================================================

predict TemperatureModel {
    data = "test_weather.csv"
    output = "temperature_predictions.csv"
}

predict PrecipitationModel {
    data = "test_weather.csv"
    output = "precipitation_predictions.csv"
}

// ============================================================
// 6. ОЦІНКА
// ============================================================

evaluate TemperatureModel {
    data = "test_weather.csv"
    metrics = [mse, mae, r2]
}

evaluate PrecipitationModel {
    data = "test_weather.csv"
    metrics = [accuracy, precision, recall, f1]
}

// ============================================================
// 7. ПРИКЛАД ВИКОРИСТАННЯ
// ============================================================

fn main() {
    let sample_data = [22.5, 45.0, 1013.0, 65.0, 5.0]
    let forecast = weather_forecast(sample_data)
    
    print("🌤️ Weather Forecast:")
    print(f"   Temperature: {forecast.temperature:.1f}°C")
    print(f"   Precipitation: {forecast.precipitation_probability * 100:.0f}%")
    print(f"   Summary: {forecast.summary}")
}