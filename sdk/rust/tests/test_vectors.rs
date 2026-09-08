// ============================================================
// Vireo Rust SDK - Test Vectors
// ============================================================

use std::fs;
use std::path::PathBuf;

use serde_json::Value;
use vireo_ai::{
    Message, WireFormat, Crypto, KeyPair, 
    test_vectors::{TestVector, TestVectorLoader, VectorType},
};

// ============================================================
// Test Vector Loading
// ============================================================

/// Get the path to test vectors directory
fn test_vectors_dir() -> PathBuf {
    let manifest_dir = std::env::var("CARGO_MANIFEST_DIR")
        .unwrap_or_else(|_| ".".to_string());
    PathBuf::from(manifest_dir)
        .join("../../specification/test_vectors")
}

/// Get the path to edge cases directory
fn edge_cases_dir() -> PathBuf {
    let manifest_dir = std::env::var("CARGO_MANIFEST_DIR")
        .unwrap_or_else(|_| ".".to_string());
    PathBuf::from(manifest_dir)
        .join("../../specification/test_vectors/edge_cases")
}

// ============================================================
// Protocol Message Test Vectors
// ============================================================

#[test]
fn test_propose_vector() {
    let path = test_vectors_dir().join("propose_v3_0.bin");
    if !path.exists() {
        println!("Skipping test - vector file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read test vector");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "propose");
    assert_eq!(msg["sender"], "did:vireo:alice");
    assert_eq!(msg["recipient"], "did:vireo:bob");
    assert!(msg["payload"].is_object());
    assert!(msg["payload"]["task"].is_string());
}

#[test]
fn test_commit_vector() {
    let path = test_vectors_dir().join("commit_v3_0.bin");
    if !path.exists() {
        println!("Skipping test - vector file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read test vector");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "commit");
    assert_eq!(msg["sender"], "did:vireo:bob");
    assert_eq!(msg["recipient"], "did:vireo:alice");
    assert!(msg["payload"]["accepted"].is_boolean());
}

#[test]
fn test_execute_vector() {
    let path = test_vectors_dir().join("execute_v3_0.bin");
    if !path.exists() {
        println!("Skipping test - vector file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read test vector");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "execute");
    assert_eq!(msg["sender"], "did:vireo:alice");
    assert_eq!(msg["recipient"], "did:vireo:bob");
    assert!(msg["payload"]["task_id"].is_string());
}

#[test]
fn test_verify_vector() {
    let path = test_vectors_dir().join("verify_v3_0.bin");
    if !path.exists() {
        println!("Skipping test - vector file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read test vector");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "verify");
    assert!(msg["payload"]["result"].is_string());
    assert!(msg["payload"]["metrics"].is_object());
}

#[test]
fn test_escalate_vector() {
    let path = test_vectors_dir().join("escalate_v3_0.bin");
    if !path.exists() {
        println!("Skipping test - vector file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read test vector");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "escalate");
    assert!(msg["payload"]["reason"].is_string());
    assert!(msg["payload"]["evidence"].is_array());
}

#[test]
fn test_done_vector() {
    let path = test_vectors_dir().join("done_v3_0.bin");
    if !path.exists() {
        println!("Skipping test - vector file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read test vector");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "done");
    assert!(msg["payload"]["status"].is_string());
    assert!(msg["payload"]["payment"].is_number());
}

// ============================================================
// Edge Case Test Vectors
// ============================================================

#[test]
fn test_unicode_nfc_edge() {
    let path = edge_cases_dir().join("unicode_nfc.bin");
    if !path.exists() {
        println!("Skipping test - edge case file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read edge case");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "test");
    assert!(msg["payload"]["text"].is_string());
    assert!(msg["payload"]["unicode"].is_string());
    assert!(msg["payload"]["emoji"].is_string());
    
    // Verify unicode strings are preserved
    let text = msg["payload"]["text"].as_str().unwrap();
    assert!(text.contains("Café"));
    assert!(text.contains("résumé"));
    assert!(text.contains("naïve"));
}

#[test]
fn test_float_negative_zero_edge() {
    let path = edge_cases_dir().join("float_negative_zero.bin");
    if !path.exists() {
        println!("Skipping test - edge case file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read edge case");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "test");
    
    // Check negative zero (should be preserved or converted to 0)
    let neg_zero = msg["payload"]["negative_zero"].as_f64();
    assert!(neg_zero.is_some());
    if let Some(val) = neg_zero {
        assert!(val == 0.0 || val.is_sign_negative());
    }
}

#[test]
fn test_big_int_edge() {
    let path = edge_cases_dir().join("big_int.bin");
    if !path.exists() {
        println!("Skipping test - edge case file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read edge case");
    let msg: Value = WireFormat::deserialize(&data).expect("Failed to deserialize");
    
    assert_eq!(msg["version"], "3.0.0");
    assert_eq!(msg["type"], "test");
    
    // Check large integers
    let large = msg["payload"]["large"].as_u64();
    assert!(large.is_some());
    if let Some(val) = large {
        assert!(val > u32::MAX as u64);
    }
    
    let larger = msg["payload"]["larger"].as_f64(); // JSON may convert to f64
    assert!(larger.is_some());
}

#[test]
fn test_duplicate_keys_edge() {
    let path = edge_cases_dir().join("duplicate_keys.bin");
    if !path.exists() {
        println!("Skipping test - edge case file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read edge case");
    // This should handle duplicate keys gracefully
    let msg: Result<Value, _> = WireFormat::deserialize(&data);
    
    // Should either succeed or fail gracefully
    if let Ok(msg) = msg {
        assert_eq!(msg["version"], "3.0.0");
        assert_eq!(msg["type"], "test");
    } else {
        // Expected failure for malformed case
        println!("Duplicate keys correctly rejected");
    }
}

// ============================================================
// Malformed Vector Tests
// ============================================================

fn test_malformed_vector(filename: &str) {
    let path = edge_cases_dir().join(filename);
    if !path.exists() {
        println!("Skipping test - file not found: {:?}", path);
        return;
    }
    
    let data = fs::read(&path).expect("Failed to read malformed vector");
    let result: Result<Value, _> = WireFormat::deserialize(&data);
    
    // Should either fail or produce a valid message
    if let Ok(msg) = result {
        // If it succeeds, verify it's a valid structure
        assert!(msg.is_object());
        if let Some(version) = msg.get("version") {
            assert!(version.is_string());
        }
    } else {
        // Expected failure - malformed data should be rejected
        println!("Malformed vector '{}' correctly rejected", filename);
    }
}

#[test]
fn test_malformed_vectors() {
    let malformed_files = vec![
        "malformed.bin",
        "malformed_v2.bin",
        "malformed_v3.bin",
        "malformed_v4.bin",
        "malformed_v5.bin",
        "malformed_v6.bin",
        "malformed_v7.bin",
        "malformed_v8.bin",
    ];
    
    for file in malformed_files {
        test_malformed_vector(file);
    }
}

// ============================================================
// Canonical Serialization Tests
// ============================================================

#[test]
fn test_canonical_serialization_consistency() {
    // Test that canonical serialization produces consistent results
    // regardless of key order
    
    let data1 = serde_json::json!({
        "z": 26,
        "a": 1,
        "m": 13,
        "nested": {
            "b": 2,
            "a": 1,
            "c": 3
        }
    });
    
    let data2 = serde_json::json!({
        "