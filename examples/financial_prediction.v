// [file name]: examples/financial_prediction.v
// ============================================================
// FINANCIAL PREDICTION SYSTEM
// Прогнозування фінансових ринків
// ============================================================

// ============================================================
// 1. МОДЕЛЬ ДЛЯ АНАЛІЗУ РИНКУ
// ============================================================

model MarketAnalysis {
    layer Dense(10, 64)
    activation ReLU
    layer Dropout(0.2)
    layer Dense(64, 32)
    activation ReLU
    layer Dropout(0.2)
    layer Dense(32, 1)
}

// ============================================================
// 2. МОДЕЛЬ ДЛЯ ПРОГНОЗУВАННЯ ТРЕНДІВ
// ============================================================

model TrendPrediction {
    layer LSTM(50, 128, return_sequences=True)
    layer Dropout(0.3)
    layer LSTM(128, 64)
    layer Dropout(0.3)
    layer Dense(64, 32)
    activation ReLU
    layer Dense(32, 1)
}

// ============================================================
// 3. МОДЕЛЬ ДЛЯ ОЦІНКИ РИЗИКІВ
// ============================================================

model RiskAssessment {
    layer Dense(20, 128)
    activation ReLU
    layer BatchNorm(128)
    layer Dense(128, 64)
    activation ReLU
    layer BatchNorm(64)
    layer Dense(64, 32)
    activation ReLU
    layer Dense(32, 1)
    activation Sigmoid
}

// ============================================================
// 4. МОДЕЛЬ ДЛЯ ОПТИМІЗАЦІЇ ПОРТФЕЛЯ
// ============================================================

model PortfolioOptimization {
    layer Dense(50, 256)
    activation ReLU
    layer Dropout(0.3)
    layer Dense(256, 128)
    activation ReLU
    layer Dropout(0.3)
    layer Dense(128, 64)
    activation ReLU
    layer Dense(64, 10)
    activation Softmax
}

// ============================================================
// 5. ФУНКЦІЇ ДЛЯ КОЖНОГО АГЕНТА
// ============================================================

fn analyze_market(data) {
    return predict(MarketAnalysis, data)
}

fn predict_trend(data) {
    return predict(TrendPrediction, data)
}

fn assess_risk(data) {
    return predict(RiskAssessment, data)
}

fn optimize_portfolio(data) {
    return predict(PortfolioOptimization, data)
}

// ============================================================
// 6. ГОЛОВНА ФУНКЦІЯ - ІНТЕГРАЦІЯ ВСІХ МОДЕЛЕЙ
// ============================================================

fn generate_financial_report(market_data, historical_data, risk_factors, portfolio_data) {
    let market_analysis = analyze_market(market_data)
    let trend_forecast = predict_trend(historical_data)
    let risk_score = assess_risk(risk_factors)
    let optimal_allocation = optimize_portfolio(portfolio_data)
    
    return {
        market_analysis: market_analysis,
        trend_forecast: trend_forecast,
        risk_score: risk_score,
        optimal_allocation: optimal_allocation,
        recommendation: trend_forecast > 0.5 ? "BUY" : "HOLD",
        confidence: 1.0 - risk_score
    }
}

// ============================================================
// 7. НАВЧАННЯ
// ============================================================

train MarketAnalysis {
    data = "market_data.csv"
    epochs = 50
    batch_size = 32
    lr = 0.001
    optimizer = Adam
}

train TrendPrediction {
    data = "historical_prices.csv"
    epochs = 100
    batch_size = 64
    lr = 0.0005
    optimizer = Adam
}

train RiskAssessment {
    data = "risk_factors.csv"
    epochs = 30
    batch_size = 16
    lr = 0.001
    optimizer = Adam
}

train PortfolioOptimization {
    data = "portfolio_data.csv"
    epochs = 80
    batch_size = 32
    lr = 0.0005
    optimizer = Adam
}

// ============================================================
// 8. ПРИКЛАД ВИКОРИСТАННЯ
// ============================================================

fn main() {
    let market = [1.2, 3.4, 5.6, 7.8, 9.0]
    let history = [100.0, 101.5, 102.0, 101.8, 103.2]
    let risk = [0.1, 0.2, 0.3, 0.4, 0.5]
    let portfolio = [0.1, 0.2, 0.3, 0.4, 0.0]
    
    let report = generate_financial_report(market, history, risk, portfolio)
    
    print("📊 Financial Report:")
    print(f"   Market Analysis: {report.market_analysis:.2f}")
    print(f"   Trend Forecast: {report.trend_forecast:.2f}")
    print(f"   Risk Score: {report.risk_score:.2f}")
    print(f"   Recommendation: {report.recommendation}")
    print(f"   Confidence: {report.confidence:.2%}")
}