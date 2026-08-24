// [file name]: examples/negotiation_weather.v
// ============================================================
// NEGOTIATION WEATHER
// Переговори між агентами про погоду
// ============================================================

// ============================================================
// 1. ОГОЛОШЕННЯ ТИПІВ
// ============================================================

type WeatherTask {
    location: String
    days: Int
    features: List[String]
}

type WeatherResult {
    temperature: Float
    precipitation: Float
    humidity: Float
    wind_speed: Float
}

// ============================================================
// 2. КОНТРАКТ ПЕРЕГОВОРІВ
// ============================================================

contract WeatherAgreement {
    task: WeatherTask
    price_tokens: Int
    deadline_sec: Int
    confidence_threshold: Float
}

// ============================================================
// 3. АГЕНТИ
// ============================================================

agent WeatherClient {
    identity: "did:key:client123"
    capability: "request_weather"
    max_price: 100
}

agent WeatherProvider {
    identity: "did:key:provider456"
    capability: "predict_weather"
    min_confidence: 0.85
}

// ============================================================
// 4. ПРОТОКОЛ ПЕРЕГОВОРІВ
// ============================================================

negotiation WeatherNegotiation {
    party Client: WeatherClient
    party Provider: WeatherProvider
    
    timeout = 10s
    max_rounds = 3
    
    // ============================================================
    // ОБРОБКА ПРОПОЗИЦІЇ
    // ============================================================
    
    on offer(Agreement: WeatherAgreement) {
        // Перевірка ціни
        if Agreement.price_tokens > Client.max_price {
            reject("Price too high")
            return
        }
        
        // Перевірка терміну
        if Agreement.deadline_sec < 5 {
            reject("Deadline too short")
            return
        }
        
        // Перевірка впевненості
        if Agreement.confidence_threshold < Provider.min_confidence {
            reject("Confidence too low")
            return
        }
        
        // Перевірка задачі
        if "temperature" not in Agreement.task.features {
            reject("Missing temperature feature")
            return
        }
        
        // Прийняття
        if Agreement.price_tokens <= 50 {
            accept(Agreement)
        } else if negotiation.round < negotiation.max_rounds {
            // Контрпропозиція
            propose(WeatherAgreement {
                task: Agreement.task,
                price_tokens: 50,
                deadline_sec: Agreement.deadline_sec,
                confidence_threshold: Agreement.confidence_threshold
            })
        } else {
            reject("Price too high, rounds exceeded")
        }
    }
    
    // ============================================================
    // ОБРОБКА ПРИЙНЯТТЯ
    // ============================================================
    
    on accept(Agreement: WeatherAgreement) {
        // Виконання задачі
        let result = predict_weather(Agreement.task)
        commit(result)
    }
    
    // ============================================================
    // ТАЙМАУТ
    // ============================================================
    
    on timeout {
        fallback {
            print("⚠️ Negotiation timeout")
            execute_local_forecast()
        }
    }
    
    // ============================================================
    // ВІДХИЛЕННЯ
    // ============================================================
    
    on reject(reason) {
        print(f"❌ Negotiation failed: {reason}")
        use_alternative_provider()
    }
}

// ============================================================
// 5. ФУНКЦІЇ ДЛЯ ВИКОНАННЯ
// ============================================================

model WeatherPrediction {
    layer Dense(10, 64)
    activation ReLU
    layer Dense(64, 32)
    activation ReLU
    layer Dense(32, 4)
}

fn predict_weather(task: WeatherTask) -> WeatherResult {
    let data = prepare_data(task)
    let prediction = predict(WeatherPrediction, data)
    
    return WeatherResult {
        temperature: prediction[0],
        precipitation: prediction[1],
        humidity: prediction[2],
        wind_speed: prediction[3]
    }
}

fn prepare_data(task: WeatherTask) -> Tensor<F32> {
    // Підготовка даних для моделі
    return Tensor::random([1, 10])
}

fn execute_local_forecast() {
    print("🌤️ Executing local forecast")
}

fn use_alternative_provider() {
    print("🔄 Using alternative weather provider")
}

// ============================================================
// 6. НАВЧАННЯ
// ============================================================

train WeatherPrediction {
    data = "weather_historical.csv"
    epochs = 100
    batch_size = 32
    lr = 0.001
    optimizer = Adam
}

// ============================================================
// 7. ПРИКЛАД ВИКОРИСТАННЯ
// ============================================================

fn main() {
    let task = WeatherTask {
        location: "Kyiv, Ukraine",
        days: 7,
        features: ["temperature", "precipitation", "humidity", "wind_speed"]
    }
    
    let agreement = WeatherAgreement {
        task: task,
        price_tokens: 75,
        deadline_sec: 30,
        confidence_threshold: 0.9
    }
    
    print("🌤️ Starting weather negotiation...")
    
    // Запуск переговорів
    let result = negotiate(agreement)
    
    print(f"📊 Result: {result}")
}