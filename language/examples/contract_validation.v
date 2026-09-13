// ============================================================
// CONTRACT VALIDATION EXAMPLES
// Vireo v2.0.2 — Demonstrates contract features
// ============================================================

// ============================================================
// 1. BASIC CONTRACT
// ============================================================

contract BasicAgreement {
    // Resource limits
    max_tokens: Int = 1000
    timeout_sec: Int = 30
    max_cost_usd: Float = 0.05
    
    // Verification condition
    verify { result.accuracy > 0.9 }
    
    // Invariant (must always hold)
    invariant { max_tokens <= 5000 }
    
    // Condition (must be met before execution)
    condition { max_cost_usd <= 0.10 }
}

// ============================================================
// 2. CONTRACT WITH VERIFY TIMEOUT
// ============================================================

contract ResearchContract {
    max_tokens: Int = 5000
    timeout_sec: Int = 300
    verify_timeout_sec: Int = 60  // Separate timeout for verification
    max_rounds: Int = 5
    
    verify { 
        result.confidence >= 0.95 
        AND result.sources >= 5 
        AND result.accuracy > 0.9
    }
    
    condition { max_cost_usd <= 0.10 }
}

// ============================================================
// 3. MULTI-SIGNATURE CONTRACT
// ============================================================

contract MultiSigContract {
    max_tokens: Int = 10000
    timeout_sec: Int = 600
    required_approvals: Int = 3  // Requires 3 agent approvals
    
    allowed_actions: List[String] = [
        "train_model",
        "predict",
        "evaluate",
        "deploy"
    ]
    
    verify { 
        result.approvals >= required_approvals 
        AND result.accuracy > 0.95
    }
}

// ============================================================
// 4. NEGOTIATION WITH CONTRACT
// ============================================================

agent Researcher {
    capability research
    role researcher
}

agent Analyst {
    capability data_analysis
    role analyst
}

contract AnalysisContract {
    max_tokens: Int = 2000
    timeout_sec: Int = 120
    verify { result.confidence >= 0.90 }
}

negotiate Researcher -> Analyst {
    party Researcher: "research-team"
    party Analyst: "analysis-team"
    
    timeout = 60s
    max_rounds = 3
    verify_timeout = 30s
    
    on offer(contract: AnalysisContract) {
        if contract.max_tokens <= 1500 {
            accept()
        } else {
            negotiate "Reduce tokens to 1500"
        }
    }
    
    on commit {
        print("Contract committed")
    }
    
    on verify {
        if result.confidence >= 0.90 {
            accept()
        } else {
            escalate("Confidence too low")
        }
    }
    
    on escalate {
        print("Escalated to Guardian: " + reason)
    }
}

// ============================================================
// 5. NEGOTIATION WITH CONTRACT
// ============================================================

contract WithAllowedActions {
    max_tokens: Int = 3000
    timeout_sec: Int = 180
    allowed_actions: List[String] = ["analyze", "report"]
    
    verify { result.quality >= 0.85 }
}

agent DataAnalyst {
    capability analyze
    capability report
    role analyst
}

negotiate DataAnalyst -> DataAnalyst {
    on offer(contract: WithAllowedActions) {
        if contract.max_tokens <= 2000 {
            accept()
        } else {
            reject("Too many tokens")
        }
    }
}

// ============================================================
// 6. CONTRACT WITH COMPLEX VERIFICATION
// ============================================================

contract MedicalAnalysis {
    max_tokens: Int = 8000
    timeout_sec: Int = 600
    verify_timeout_sec: Int = 120
    
    // Complex verification condition
    verify {
        result.accuracy > 0.95 
        AND result.sensitivity > 0.90 
        AND result.specificity > 0.90 
        AND result.f1_score > 0.92
    }
    
    allowed_actions: List[String] = [
        "analyze_image",
        "detect_anomaly",
        "classify_tissue"
    ]
}

// ============================================================
// 7. CONTRACT WITH REQUIREMENTS
// ============================================================

contract RequirementsContract {
    max_tokens: Int = 4000
    timeout_sec: Int = 240
    
    // Input requirements
    condition { input.size >= 100 AND input.size <= 10000 }
    
    // Output requirements
    verify { 
        output.accuracy >= 0.90 
        AND output.recall >= 0.85 
        AND output.precision >= 0.85
    }
    
    // Invariant
    invariant { max_tokens <= 5000 AND timeout_sec <= 300 }
}

// ============================================================
// 8. FULL EXAMPLE WITH ALL FEATURES
// ============================================================

agent VisionModel {
    capability image_analysis
    capability object_detection
    role vision
}

contract VisionContract {
    max_tokens: Int = 5000
    timeout_sec: Int = 300
    verify_timeout_sec: Int = 60
    max_rounds: Int = 5
    required_approvals: Int = 2
    
    allowed_actions: List[String] = [
        "analyze_image",
        "detect_objects",
        "classify_scene"
    ]
    
    condition { input.image_count >= 1 AND input.image_count <= 1000 }
    
    verify { 
        result.accuracy > 0.90 
        AND result.confidence > 0.85 
        AND result.processed_count > 0
    }
}

negotiate VisionModel -> VisionModel {
    party VisionModel: "vision-team"
    
    timeout = 120s
    max_rounds = 3
    verify_timeout = 30s
    
    on offer(contract: VisionContract) {
        if contract.max_tokens <= 3000 {
            accept()
        } else {
            negotiate "Reduce tokens to 3000"
        }
    }
    
    on commit {
        print("Contract committed successfully")
    }
    
    on verify {
        if result.accuracy > 0.90 {
            accept()
        } else {
            escalate("Accuracy below threshold")
        }
    }
    
    on escalate {
        print("Escalation triggered: " + reason)
        // Notify Guardian
        guardian.notify("VisionContract", reason)
    }
}