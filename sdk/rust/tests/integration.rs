// ============================================================
// Vireo Rust SDK - Integration Tests
// ============================================================

use std::time::Duration;
use std::sync::Arc;
use tokio::time::timeout;
use tokio::sync::Mutex;

// Import Vireo modules
use vireo_ai::{
    Agent, AgentConfig, 
    Message, MessageType,
    Protocol, ProtocolState,
    Crypto, KeyPair, Signature,
    WireFormat, WireFormatError,
    Transport, TransportType,
};

// ============================================================
// Test Helpers
// ============================================================

/// Create a test agent with default configuration
fn create_test_agent(name: &str) -> Agent {
    let config = AgentConfig::builder()
        .name(name.to_string())
        .version("1.0.0".to_string())
        .capabilities(vec!["test".to_string(), "integration".to_string()])
        .build()
        .unwrap();
    
    Agent::new(config)
}

/// Create a test message
fn create_test_message(msg_type: &str, payload: serde_json::Value) -> Message {
    Message::builder()
        .msg_type(msg_type.to_string())
        .sender("test_sender".to_string())
        .recipient("test_recipient".to_string())
        .payload(payload)
        .build()
        .unwrap()
}

/// Wait for async operation with timeout
async fn wait_with_timeout<F, T>(future: F, timeout_secs: u64) -> Result<T, String>
where
    F: std::future::Future<Output = T>,
{
    match timeout(Duration::from_secs(timeout_secs), future).await {
        Ok(result) => Ok(result),
        Err(_) => Err("Operation timed out".to_string()),
    }
}

// ============================================================
// Agent Tests
// ============================================================

#[tokio::test]
async fn test_agent_creation() {
    let agent = create_test_agent("TestAgent");
    
    assert_eq!(agent.name(), "TestAgent");
    assert_eq!(agent.version(), "1.0.0");
    assert!(agent.capabilities().contains(&"test".to_string()));
    assert_eq!(agent.status(), "idle");
    assert!(agent.id().starts_with("did:vireo:TestAgent_"));
}

#[tokio::test]
async fn test_agent_start_stop() {
    let mut agent = create_test_agent("StartStopAgent");
    
    // Start agent
    agent.start().await.unwrap();
    assert_eq!(agent.status(), "active");
    
    // Stop agent
    agent.stop().await.unwrap();
    assert_eq!(agent.status(), "stopped");
}

#[tokio::test]
async fn test_agent_message_handling() {
    let mut agent = create_test_agent("MessageAgent");
    
    // Register message handler
    agent.on_message("test", |msg| async move {
        let response = Message::builder()
            .msg_type("test_response".to_string())
            .sender("agent".to_string())
            .recipient(msg.sender().clone())
            .payload(serde_json::json!({
                "status": "ok",
                "echo": msg.payload()
            }))
            .build()
            .unwrap();
        Ok(Some(response))
    });
    
    // Start agent
    agent.start().await.unwrap();
    
    // Send message
    let msg = create_test_message("test", serde_json::json!({"data": "hello"}));
    let response = agent.handle_message(msg).await.unwrap();
    
    assert!(response.is_some());
    let resp = response.unwrap();
    assert_eq!(resp.msg_type(), "test_response");
    assert_eq!(resp.payload()["status"], "ok");
    assert_eq!(resp.payload()["echo"]["data"], "hello");
    
    // Stop agent
    agent.stop().await.unwrap();
}

#[tokio::test]
async fn test_agent_capabilities() {
    let mut agent = create_test_agent("CapabilityAgent");
    
    // Add capabilities
    agent.add_capability("text-generation".to_string());
    agent.add_capability("code-analysis".to_string());
    
    assert!(agent.has_capability("text-generation"));
    assert!(agent.has_capability("code-analysis"));
    assert!(!agent.has_capability("unknown"));
    
    // Get capabilities
    let caps = agent.capabilities();
    assert_eq!(caps.len(), 4); // "test", "integration", plus new ones
    
    // Remove capability
    agent.remove_capability("test");
    assert!(!agent.has_capability("test"));
}

#[tokio::test]
async fn test_agent_status() {
    let agent = create_test_agent("StatusAgent");
    
    let status = agent.get_status();
    assert_eq!(status["name"], "StatusAgent");
    assert_eq!(status["status"], "idle");
    assert!(status["capabilities"].is_array());
    assert!(status["uptime"].is_number());
}

#[tokio::test]
async fn test_agent_info() {
    let agent = create_test_agent("InfoAgent");
    
    let info = agent.get_info();
    assert_eq!(info["name"], "InfoAgent");
    assert_eq!(info["version"], "1.0.0");
    assert_eq!(info["protocol_version"], "3.0.0");
    assert!(info["capabilities"].is_array());
    assert!(info["id"].is_string());
}

#[tokio::test]
async fn test_agent_multiple_handlers() {
    let mut agent = create_test_agent("MultiHandlerAgent");
    
    // Register multiple handlers for same message type
    let counter = Arc::new(Mutex::new(0));
    let counter_clone = counter.clone();
    
    agent.on_message("multi", move |_| {
        let counter = counter_clone.clone();
        async move {
            let mut count = counter.lock().await;
            *count += 1;
            Ok::<Option<Message>, String>(None)
        }
    });
    
    agent.on_message("multi", move |_| {
        let counter = counter_clone.clone();
        async move {
            let mut count = counter.lock().await;
            *count += 1;
            Ok::<Option<Message>, String>(None)
        }
    });
    
    agent.start().await.unwrap();
    
    let msg = create_test_message("multi", serde_json::json!({}));
    let _ = agent.handle_message(msg).await.unwrap();
    
    let count = *counter.lock().await;
    assert_eq!(count, 2);
    
    agent.stop().await.unwrap();
}

// ============================================================
// Message Tests
// ============================================================

#[tokio::test]
async fn test_message_creation() {
    let msg = Message::builder()
        .msg_type("propose".to_string())
        .sender("did:vireo:alice".to_string())
        .recipient("did:vireo:bob".to_string())
        .payload(serde_json::json!({
            "task": "analyze_data",
            "parameters": {
                "dataset": "sample.csv",
                "method": "statistical"
            }
        }))
        .version("3.0.0".to_string())
        .build()
        .unwrap();
    
    assert_eq!(msg.msg_type(), "propose");
    assert_eq!(msg.sender(), "did:vireo:alice");
    assert_eq!(msg.recipient(), "did:vireo:bob");
    assert_eq!(msg.version(), "3.0.0");
    assert!(msg.id().len() > 0);
    assert!(msg.timestamp() > 0);
    assert!(msg.nonce().len() > 0);
}

#[tokio::test]
async fn test_message_serialization() {
    let msg = Message::builder()
        .msg_type("execute".to_string())
        .sender("alice".to_string())
        .recipient("bob".to_string())
        .payload(serde_json::json!({"action": "compute"}))
        .build()
        .unwrap();
    
    // Serialize to JSON
    let json = serde_json::to_string(&msg).unwrap();
    assert!(json.contains("execute"));
    assert!(json.contains("alice"));
    assert!(json.contains("bob"));
    
    // Deserialize from JSON
    let deserialized: Message = serde_json::from_str(&json).unwrap();
    assert_eq!(deserialized.msg_type(), msg.msg_type());
    assert_eq!(deserialized.sender(), msg.sender());
    assert_eq!(deserialized.recipient(), msg.recipient());
    assert_eq!(deserialized.payload()["action"], "compute");
}

#[tokio::test]
async fn test_message_signing() {
    // Generate key pair
    let key_pair = KeyPair::generate().unwrap();
    let public_key = key_pair.public_key();
    
    let msg = Message::builder()
        .msg_type("propose".to_string())
        .sender("alice".to_string())
        .recipient("bob".to_string())
        .payload(serde_json::json!({"data": "test"}))
        .build()
        .unwrap();
    
    // Sign message
    let signed = msg.sign(&key_pair).unwrap();
    assert!(signed.signature().is_some());
    
    // Verify signature
    let verified = signed.verify(public_key).unwrap();
    assert!(verified);
    
    // Tamper with message
    let mut tampered = signed.clone();
    tampered = tampered.with_payload(serde_json::json!({"data": "tampered"}));
    let verified_tampered = tampered.verify(public_key).unwrap();
    assert!(!verified_tampered);
}

#[tokio::test]
async fn test_message_requires_response() {
    let msg1 = Message::builder()
        .msg_type("propose".to_string())
        .sender("alice".to_string())
        .recipient("bob".to_string())
        .payload(serde_json::json!({}))
        .build()
        .unwrap();
    assert!(msg1.requires_response());
    
    let msg2 = Message::builder()
        .msg_type("done".to_string())
        .sender("alice".to_string())
        .recipient("bob".to_string())
        .payload(serde_json::json!({}))
        .build()
        .unwrap();
    assert!(!msg2.requires_response());
}

// ============================================================
// Protocol Tests
// ============================================================

#[tokio::test]
async fn test_protocol_creation() {
    let protocol = Protocol::new("3.0.0");
    assert_eq!(protocol.version(), "3.0.0");
    assert_eq!(protocol.state(), ProtocolState::Idle);
}

#[tokio::test]
async fn test_protocol_transitions() {
    let mut protocol = Protocol::new("3.0.0");
    
    // IDLE -> PROPOSE
    assert!(protocol.transition(ProtocolState::Propose).is_ok());
    assert_eq!(protocol.state(), ProtocolState::Propose);
    
    // PROPOSE -> COMMIT
    assert!(protocol.transition(ProtocolState::Commit).is_ok());
    assert_eq!(protocol.state(), ProtocolState::Commit);
    
    // COMMIT -> EXECUTE
    assert!(protocol.transition(ProtocolState::Execute).is_ok());
    assert_eq!(protocol.state(), ProtocolState::Execute);
    
    // EXECUTE -> VERIFY
    assert!(protocol.transition(ProtocolState::Verify).is_ok());
    assert_eq!(protocol.state(), ProtocolState::Verify);
    
    // VERIFY -> DONE
    assert!(protocol.transition(ProtocolState::Done).is_ok());
    assert_eq!(protocol.state(), ProtocolState::Done);
}

#[tokio::test]
async fn test_protocol_invalid_transitions() {
    let mut protocol = Protocol::new("3.0.0");
    
    // IDLE -> EXECUTE (invalid)
    assert!(protocol.transition(ProtocolState::Execute).is_err());
    assert_eq!(protocol.state(), ProtocolState::Idle);
    
    // IDLE -> PROPOSE (valid)
    assert!(protocol.transition(ProtocolState::Propose).is_ok());
    assert_eq!(protocol.state(), ProtocolState::Propose);
    
    // PROPOSE -> DONE (invalid)
    assert!(protocol.transition(ProtocolState::Done).is_err());
    assert_eq!(protocol.state(), ProtocolState::Propose);
}

#[tokio::test]
async fn test_protocol_reset() {
    let mut protocol = Protocol::new("3.0.0");
    
    protocol.transition(ProtocolState::Propose).unwrap();
    protocol.transition(ProtocolState::Commit).unwrap();
    assert_eq!(protocol.state(), ProtocolState::Commit);
    
    protocol.reset();
    assert_eq!(protocol.state(), ProtocolState::Idle);
}

#[tokio::test]
async fn test_protocol_history() {
    let mut protocol = Protocol::new("3.0.0");
    
    protocol.transition(ProtocolState::Propose).unwrap();
    protocol.transition(ProtocolState::Commit).unwrap();
    protocol.transition(ProtocolState::Execute).unwrap();
    
    let history = protocol.history();
    assert_eq!(history.len(), 3);
    assert_eq!(history[0], ProtocolState::Propose);
    assert_eq!(history[1], ProtocolState::Commit);
    assert_eq!(history[2], ProtocolState::Execute);
}

// ============================================================
// Crypto Tests
// ============================================================

#[tokio::test]
async fn test_key_pair_generation() {
    let key_pair = KeyPair::generate().unwrap();
    assert!(key_pair.private_key().len() > 0);
    assert!(key_pair.public_key().len() > 0);
}

#[tokio::test]
async fn test_signing_verification() {
    let key_pair = KeyPair::generate().unwrap();
    let data = b"Hello, Vireo!";
    
    let signature = key_pair.sign(data).unwrap();
    assert!(signature.len() > 0);
    
    let verified = key_pair.verify(data, &signature).unwrap();
    assert!(verified);
    
    // Wrong data
    let wrong_data = b"Wrong data!";
    let verified_wrong = key_pair.verify(wrong_data, &signature).unwrap();
    assert!(!verified_wrong);
}

#[tokio::test]
async fn test_derive_shared_secret() {
    let alice = KeyPair::generate().unwrap();
    let bob = KeyPair::generate().unwrap();
    
    let alice_secret = alice.derive_shared_secret(bob.public_key()).unwrap();
    let bob_secret = bob.derive_shared_secret(alice.public_key()).unwrap();
    
    assert_eq!(alice_secret, bob_secret);
}

// ============================================================
// WireFormat Tests
// ============================================================

#[tokio::test]
async fn test_wire_format_serialize_deserialize() {
    let data = serde_json::json!({
        "version": "3.0.0",
        "type": "test",
        "sender": "alice",
        "recipient": "bob",
        "payload": {
            "key": "value",
            "number": 42,
            "array": [1, 2, 3]
        }
    });
    
    let bytes = WireFormat::serialize(&data).unwrap();
    assert!(bytes.len() > 0);
    
    let deserialized: serde_json::Value = WireFormat::deserialize(&bytes).unwrap();
    assert_eq!(deserialized["version"], "3.0.0");
    assert_eq!(deserialized["type"], "test");
    assert_eq!(deserialized["payload"]["number"], 42);
}

#[tokio::test]
async fn test_wire_format_canonical() {
    let data1 = serde_json::json!({
        "b": 2,
        "a": 1,
        "c": 3
    });
    
    let data2 = serde_json::json!({
        "c": 3,
        "a": 1,
        "b": 2
    });
    
    // Both should produce the same canonical serialization
    let bytes1 = WireFormat::serialize_canonical(&data1).unwrap();
    let bytes2 = WireFormat::serialize_canonical(&data2).unwrap();
    assert_eq!(bytes1, bytes2);
}

#[tokio::test]
async fn test_wire_format_roundtrip() {
    let original = serde_json::json!({
        "nested": {
            "a": 1,
            "b": 2,
            "c": [3, 4, 5]
        },
        "string": "hello",
        "boolean": true,
        "null": null
    });
    
    let bytes = WireFormat::serialize(&original).unwrap();
    let deserialized: serde_json::Value = WireFormat::deserialize(&bytes).unwrap();
    assert_eq!(deserialized, original);
}

// ============================================================
// Integration Tests
// ============================================================

#[tokio::test]
async fn test_agent_to_agent_communication() {
    let mut agent1 = create_test_agent("Agent1");
    let mut agent2 = create_test_agent("Agent2");
    
    // Register handler on agent2
    agent2.on_message("ping", |msg| async move {
        let response = Message::builder()
            .msg_type("pong".to_string())
            .sender("agent2".to_string())
            .recipient(msg.sender().clone())
            .payload(serde_json::json!({
                "status": "ok",
                "timestamp": chrono::Utc::now().to_rfc3339()
            }))
            .build()
            .unwrap();
        Ok(Some(response))
    });
    
    // Start agents
    agent1.start().await.unwrap();
    agent2.start().await.unwrap();
    
    // Send message from agent1 to agent2
    let msg = Message::builder()
        .msg_type("ping".to_string())
        .sender("agent1".to_string())
        .recipient("agent2".to_string())
        .payload(serde_json::json!({"message": "hello"}))
        .build()
        .unwrap();
    
    let response = agent2.handle_message(msg).await.unwrap();
    
    assert!(response.is_some());
    let resp = response.unwrap();
    assert_eq!(resp.msg_type(), "pong");
    assert_eq!(resp.payload()["status"], "ok");
    
    agent1.stop().await.unwrap();
    agent2.stop().await.unwrap();
}

#[tokio::test]
async fn test_full_negotiation_flow() {
    let mut negotiator = create_test_agent("Negotiator");
    let mut responder = create_test_agent("Responder");
    
    // Setup negotiator handler
    negotiator.on_message("propose", |msg| async move {
        let proposal = msg.payload();
        let price = proposal["price"].as_u64().unwrap_or(0);
        
        if price >= 100 {
            let response = Message::builder()
                .msg_type("commit".to_string())
                .sender("negotiator".to_string())
                .recipient(msg.sender().clone())
                .payload(serde_json::json!({
                    "accepted": true,
                    "price": price,
                    "status": "committed"
                }))
                .build()
                .unwrap();
            Ok(Some(response))
        } else {
            let response = Message::builder()
                .msg_type("counter".to_string())
                .sender("negotiator".to_string())
                .recipient(msg.sender().clone())
                .payload(serde_json::json!({
                    "accepted": false,
                    "counter_price": price + 50,
                    "reason": "Price too low"
                }))
                .build()
                .unwrap();
            Ok(Some(response))
        }
    });
    
    // Start agents
    negotiator.start().await.unwrap();
    responder.start().await.unwrap();
    
    // Test low price -> counter
    let msg = Message::builder()
        .msg_type("propose".to_string())
        .sender("responder".to_string())
        .recipient("negotiator".to_string())
        .payload(serde_json::json!({
            "price": 50,
            "task": "data_analysis"
        }))
        .build()
        .unwrap();
    
    let response = negotiator.handle_message(msg).await.unwrap();
    assert!(response.is_some());
    let resp = response.unwrap();
    assert_eq!(resp.msg_type(), "counter");
    assert_eq!(resp.payload()["counter_price"], 100);
    
    // Test high price -> commit
    let msg2 = Message::builder()
        .msg_type("propose".to_string())
        .sender("responder".to_string())
        .recipient("negotiator".to_string())
        .payload(serde_json::json!({
            "price": 150,
            "task": "data_analysis"
        }))
        .build()
        .unwrap();
    
    let response2 = negotiator.handle_message(msg2).await.unwrap();
    assert!(response2.is_some());
    let resp2 = response2.unwrap();
    assert_eq!(resp2.msg_type(), "commit");
    assert_eq!(resp2.payload()["accepted"], true);
    
    negotiator.stop().await.unwrap();
    responder.stop().await.unwrap();
}

// ============================================================
// Performance Tests
// ============================================================

#[tokio::test]
async fn test_benchmark_message_handling() {
    let mut agent = create_test_agent("BenchmarkAgent");
    
    // Simple echo handler
    agent.on_message("echo", |msg| async move {
        let response = Message::builder()
            .msg_type("echo_response".to_string())
            .sender("agent".to_string())
            .recipient(msg.sender().clone())
            .payload(serde_json::json!({
                "echo": msg.payload()
            }))
            .build()
            .unwrap();
        Ok(Some(response))
    });
    
    agent.start().await.unwrap();
    
    let start = std::time::Instant::now();
    let iterations = 100;
    
    for i in 0..iterations {
        let msg = Message::builder()
            .msg_type("echo".to_string())
            .sender("test".to_string())
            .recipient("agent".to_string())
            .payload(serde_json::json!({
                "iteration": i,
                "data": "test_data_".to_string() + &i.to_string()
            }))
            .build()
            .unwrap();
        
        let response = agent.handle_message(msg).await.unwrap();
        assert!(response.is_some());
    }
    
    let duration = start.elapsed();
    let avg_time = duration.as_micros() / iterations;
    
    println!("Processed {} messages in {:?}", iterations, duration);
    println!("Average time per message: {} µs", avg_time);
    
    agent.stop().await.unwrap();
}

// ============================================================
// Error Handling Tests
// ============================================================

#[tokio::test]
async fn test_agent_error_handling() {
    let mut agent = create_test_agent("ErrorAgent");
    
    // Handler that returns error
    agent.on_message("error", |_| async move {
        Err::<Option<Message>, _>("Intentional error".to_string())
    });
    
    agent.start().await.unwrap();
    
    let msg = create_test_message("error", serde_json::json!({}));
    let result = agent.handle_message(msg).await;
    
    // Should still return an error response
    assert!(result.is_err());
    
    agent.stop().await.unwrap();
}

#[tokio::test]
async fn test_invalid_message_handling() {
    let mut agent = create_test_agent("InvalidAgent");
    agent.start().await.unwrap();
    
    // Message without required fields
    let msg = Message::builder()
        .msg_type("".to_string())
        .sender("".to_string())
        .recipient("".to_string())
        .payload(serde_json::json!({}))
        .build()
        .unwrap();
    
    let result = agent.handle_message(msg).await;
    assert!(result.is_ok()); // Should return error message
    let response = result.unwrap();
    assert!(response.is_some());
    let resp = response.unwrap();
    assert_eq!(resp.msg_type(), "error");
    
    agent.stop().await.unwrap();
}

#[tokio::test]
async fn test_timeout_handling() {
    let mut agent = create_test_agent("TimeoutAgent");
    
    // Slow handler
    agent.on_message("slow", |_| async move {
        tokio::time::sleep(Duration::from_secs(2)).await;
        Ok::<Option<Message>, String>(None)
    });
    
    agent.start().await.unwrap();
    
    let msg = create_test_message("slow", serde_json::json!({}));
    let start = std::time::Instant::now();
    
    // Should timeout after 1 second
    let result = wait_with_timeout(agent.handle_message(msg), 1).await;
    assert!(result.is_err());
    
    agent.stop().await.unwrap();
}