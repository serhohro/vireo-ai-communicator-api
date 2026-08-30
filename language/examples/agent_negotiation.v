// ============================================================
// AGENT NEGOTIATION IN VIREO
// ============================================================

// Agent Definitions
agent WeatherAgent {
    identity: "did:key:z6MkhaXk1BZ4fGqFqQrZ..."
    capability predict_weather()
    capability analyze_data()
}

agent ComputeProvider {
    identity: "did:key:z6Mkhw9nBAwZ..."
    capability execute_code()
    capability train_model()
}

// Contract
contract WeatherAgreement {
    max_tokens: Int = 1000
    max_cost_usd: Float = 0.05
    timeout_sec: Int = 30
    max_rounds: Int = 3
    allowed_actions: List[String] = ["predict_weather"]
}

// Negotiation
negotiation WeatherNegotiation {
    party Initiator: WeatherAgent
    party Provider: ComputeProvider
    
    timeout = 10s
    max_rounds = 5
    
    on offer(Agreement: WeatherAgreement) {
        if Agreement.max_tokens <= 500 {
            accept()
        } else if negotiation.round < negotiation.max_rounds {
            propose(counter_offer)
        } else {
            reject("Budget exceeded")
        }
    }
}

// Proposal
propose WeatherAgent {
    task = "Predict weather for 7 days"
    contract = WeatherAgreement {
        max_tokens: 500,
        timeout_sec: 10
    }
}

// Execution
execute ComputeProvider {
    result = predict_weather(7)
    inform(WeatherAgent, result)
}