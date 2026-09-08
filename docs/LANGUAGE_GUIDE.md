# Vireo Language Guide

Complete reference for the Vireo programming language v3.0.0.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Syntax Basics](#syntax-basics)
3. [Agents](#agents)
4. [Types](#types)
5. [Control Flow](#control-flow)
6. [Functions](#functions)
7. [Extensions](#extensions)
8. [Standard Library](#standard-library)
9. [Examples](#examples)

---

## Overview

Vireo is a domain-specific language designed for AI-to-AI communication. It combines:

- **Functional programming** for declarative agent definitions
- **Pattern matching** for message handling
- **Tensor operations** for ML workloads
- **Protocol primitives** for secure communication

### Key Features

```vireo
// Hello World Agent
agent Greeter {
    name: "HelloWorld"
    version: "1.0.0"
    
    capabilities: ["greeting"]
    
    on message {
        match message.text {
            "hello" => respond("Hello, world!")
            _ => respond("Unknown command")
        }
    }
}
Syntax Basics
Comments
vireo
// Single line comment
/* Multi-line
   comment */
Variables
vireo
// Immutable by default
let name = "Agent-001"
let version = 3.0
let active = true

// Mutable variables (with mut keyword)
mut counter = 0
counter = counter + 1
Constants
vireo
const MAX_RETRIES = 5
const TIMEOUT_MS = 30000
const API_BASE = "https://api.vireo.ai/v1"
String Literals
vireo
let s1 = "Hello, world!"
let s2 = "Multi-line\nstring"
let s3 = """Triple-quoted
    multi-line
    string"""
let s4 = "Interpolated ${name} version ${version}"
Agents
Agent Definition
vireo
agent MyAgent {
    name: "MyAgent"
    version: "1.0.0"
    description: "My AI agent"
    
    capabilities: ["text", "image", "video"]
    
    // Configuration
    config {
        timeout: 30
        retries: 3
        language: "en"
    }
    
    // State
    state {
        messages: []
        session_id: ""
        status: "idle"
    }
    
    // Handlers
    on message { ... }
    on request { ... }
    on event { ... }
    
    // Functions
    fn process(data) { ... }
}
Agent Communication
vireo
// Send message to another agent
send("peer-agent") {
    type: "query"
    payload: {
        question: "What is 2+2?"
    }
}

// Broadcast to all peers
broadcast {
    type: "status_update"
    payload: {
        status: "ready"
    }
}

// Request with response
let response = request("peer-agent") {
    type: "compute"
    payload: {
        expression: "2 + 2"
    }
}
Message Handlers
vireo
agent ChatBot {
    // Match by message type
    on message "greeting" {
        respond("Hello!")
    }
    
    // Match by payload structure
    on message {
        type: "query"
        payload: {
            question: string
        }
    } {
        let answer = process(question)
        respond({
            type: "answer"
            payload: {
                answer: answer
            }
        })
    }
    
    // Catch-all handler
    on message * {
        respond({
            type: "error"
            payload: {
                error: "Unknown message type"
            }
        })
    }
}
Types
Primitive Types
vireo
// Numbers
let int: int = 42
let float: float = 3.14159
let long: long = 1234567890

// Booleans
let bool: bool = true

// Strings
let str: string = "Hello"

// Null
let nothing: null = null

// Any
let any: any = "Can be anything"
Composite Types
vireo
// Arrays
let numbers: [int] = [1, 2, 3, 4, 5]
let mixed: [any] = [1, "two", true]

// Maps (Dictionaries)
let config: {string: any} = {
    "host": "localhost"
    "port": 8080
}

// Tuples
let pair: (int, string) = (42, "answer")

// Structs
struct Point {
    x: float
    y: float
}

let p = Point { x: 10.0, y: 20.0 }
Special Types
vireo
// Tensor
let matrix: tensor[float] = [[1, 2], [3, 4]]
let vector: tensor[float, 3] = [1, 2, 3]

// Message
let msg: Message = {
    type: "propose"
    payload: { data: "hello" }
}

// Contract
let contract: Contract = {
    parties: ["alice", "bob"]
    terms: {
        price: 100
        deadline: "2024-12-31"
    }
}

// DID
let did: DID = did("vireo:1234567890")
Type Aliases
vireo
type UserID = string
type Response = {status: string, data: any}
type Handler = fn(Message) -> Message

let uid: UserID = "user_123"
let resp: Response = {status: "ok", data: null}
Control Flow
If/Else
vireo
let x = 10

if x > 5 {
    println("x is greater than 5")
} else if x == 5 {
    println("x equals 5")
} else {
    println("x is less than 5")
}

// If expression (returns value)
let result = if x > 0 { "positive" } else { "non-positive" }
Match (Pattern Matching)
vireo
let value = "hello"

match value {
    "hello" => println("Greeting")
    "goodbye" => println("Farewell")
    // Pattern with variable
    s: string => println("Unknown string: ${s}")
    // Default
    _ => println("Unknown value")
}

// Match on structure
match data {
    {type: "success", payload: p} => process(p)
    {type: "error", error: e} => handle_error(e)
    _ => println("Unknown data")
}

// Match on type
match value {
    int: i => println("Integer: ${i}")
    string: s => println("String: ${s}")
    tensor: t => println("Tensor: ${t.shape}")
    _ => println("Unknown type")
}
Loops
vireo
// For loop
for i in range(10) {
    println(i)
}

for item in items {
    process(item)
}

for key, value in map {
    println("${key}: ${value}")
}

// While loop
mut count = 0
while count < 5 {
    println(count)
    count = count + 1
}

// Loop with break/continue
for i in range(10) {
    if i == 3 { continue }
    if i == 7 { break }
    println(i)
}
Functions
Function Definition
vireo
// Basic function
fn add(a: int, b: int) -> int {
    return a + b
}

// Function with multiple return values
fn divide(a: float, b: float) -> (float, bool) {
    if b == 0 {
        return (0, false)
    }
    return (a / b, true)
}

// Function with default parameters
fn greet(name: string, prefix: string = "Hello") -> string {
    return "${prefix}, ${name}!"
}

// Function with variable arguments
fn sum(numbers: ...int) -> int {
    let total = 0
    for n in numbers {
        total = total + n
    }
    return total
}
Anonymous Functions (Lambdas)
vireo
let square = fn(x: int) -> int { x * x }

let result = map([1, 2, 3], fn(x) { x * 2 })

// Short syntax
let double = |x| x * 2
let add = |a, b| a + b

// Filter
let even = filter([1, 2, 3, 4], |x| x % 2 == 0)
Higher-Order Functions
vireo
fn apply_twice(f: fn(int) -> int, x: int) -> int {
    return f(f(x))
}

let result = apply_twice(|x| x * 2, 3)  // 12

// Map
fn map(arr: [int], f: fn(int) -> int) -> [int] {
    let result = []
    for x in arr {
        result.push(f(x))
    }
    return result
}

// Filter
fn filter(arr: [int], f: fn(int) -> bool) -> [int] {
    let result = []
    for x in arr {
        if f(x) {
            result.push(x)
        }
    }
    return result
}

// Reduce
fn reduce(arr: [int], f: fn(int, int) -> int, initial: int) -> int {
    let result = initial
    for x in arr {
        result = f(result, x)
    }
    return result
}
Extensions
ML Extension
vireo
// Import ML extension
import ml

// Neural Network
let model = ml.nn.Sequential(
    ml.nn.Linear(784, 128),
    ml.nn.ReLU(),
    ml.nn.Dropout(0.2),
    ml.nn.Linear(128, 10),
    ml.nn.Softmax()
)

// Training
model.train(
    x_train: tensor,
    y_train: tensor,
    epochs: 10,
    batch_size: 32,
    learning_rate: 0.001
)

// Inference
let prediction = model.forward(x_test)
Tensor Extension
vireo
import tensor

// Create tensors
let t1 = tensor.zeros([3, 3])
let t2 = tensor.ones([2, 2])
let t3 = tensor.random([4, 4])

// Operations
let t = t1 + t2
let u = t1 * t2
let v = t1.matmul(t2)

// Reduction
let sum = t.sum()
let mean = t.mean()
let std = t.std()

// Reshape
let reshaped = t.reshape([1, 9])

// Indexing
let element = t[0, 0]
let slice = t[0:2, 0:2]
Vision Extension
vireo
import vision

// Image processing
let image = vision.load_image("image.jpg")
let processed = image
    .resize(224, 224)
    .normalize(mean: [0.485, 0.456, 0.406])
    .to_tensor()

// Object detection
let detections = vision.detect_objects(image)
for detection in detections {
    println("Found: ${detection.label} (${detection.confidence})")
}

// Image generation
let generated = vision.generate(
    prompt: "A sunset over mountains",
    width: 512,
    height: 512
)
NLP Extension
vireo
import nlp

// Tokenization
let tokens = nlp.tokenize("Hello, world!")
let vectors = nlp.embed(tokens)

// Language model
let model = nlp.load_model("gpt-2")
let response = model.generate(
    prompt: "The future of AI is",
    max_tokens: 100
)

// Text classification
let classification = nlp.classify(
    text: "I love this product!",
    labels: ["positive", "negative", "neutral"]
)
Standard Library
Math Module
vireo
import math

// Constants
let pi = math.PI
let e = math.E

// Functions
let result1 = math.sin(pi / 2)        // 1.0
let result2 = math.cos(0)              // 1.0
let result3 = math.sqrt(144)           // 12.0
let result4 = math.pow(2, 10)          // 1024.0
let result5 = math.log(100)            // 4.605...
let result6 = math.floor(3.9)          // 3
let result7 = math.ceil(3.1)           // 4
Protocol Module
vireo
import protocol

// Create protocol
let protocol = protocol.new(
    name: "A2A",
    version: "3.0.0"
)

// Define states
protocol.add_state("IDLE")
protocol.add_state("PROPOSE")
protocol.add_state("COMMIT")
protocol.add_state("EXECUTE")
protocol.add_state("VERIFY")

// Define transitions
protocol.add_transition("IDLE", "PROPOSE", "initiate")
protocol.add_transition("PROPOSE", "COMMIT", "agree")
protocol.add_transition("COMMIT", "EXECUTE", "execute")

// Process message
let result = protocol.process(
    message: msg,
    current_state: "IDLE"
)
Crypto Module
vireo
import crypto

// Key generation
let keypair = crypto.generate_keypair()
let public_key = keypair.public
let private_key = keypair.private

// Signing
let signature = crypto.sign(
    data: "Hello, world!",
    private_key: private_key
)

// Verification
let valid = crypto.verify(
    data: "Hello, world!",
    signature: signature,
    public_key: public_key
)

// Hashing
let hash = crypto.blake2b("Hello, world!")

// DID creation
let did = crypto.create_did(public_key)
IO Module
vireo
import io

// File operations
let content = io.read_file("config.json")
let parsed = io.parse_json(content)

io.write_file("output.txt", "Hello, world!")

// Network operations
let response = io.http_get("https://api.example.com/data")
let result = io.http_post(
    url: "https://api.example.com/submit",
    body: json_data,
    headers: {"Authorization": "Bearer token"}
)

// Console
io.print("Hello, world!")
io.println("With newline")

let input = io.read_line()
Examples
Example 1: Simple Agent
vireo
// simple_agent.vireo
agent SimpleAgent {
    name: "SimpleAgent"
    version: "1.0.0"
    
    capabilities: ["echo", "math"]
    
    on message "echo" {
        let text = message.payload.text
        respond({
            type: "echo_response"
            payload: {
                text: "Echo: ${text}"
                timestamp: now()
            }
        })
    }
    
    on message "calculate" {
        let a = message.payload.a
        let b = message.payload.b
        let operation = message.payload.operation
        
        let result = match operation {
            "add" => a + b
            "sub" => a - b
            "mul" => a * b
            "div" => if b != 0 { a / b } else { error("Division by zero") }
            _ => error("Unknown operation")
        }
        
        respond({
            type: "calculation_result"
            payload: {
                result: result
                operation: operation
                a: a
                b: b
            }
        })
    }
}
Example 2: Negotiation Agent
vireo
// negotiation_agent.vireo
agent Negotiator {
    name: "Negotiator"
    version: "1.0.0"
    
    capabilities: ["negotiation", "contract"]
    
    state {
        current_offer: null
        best_offer: null
        attempts: 0
        max_attempts: 5
    }
    
    on message "propose" {
        let offer = message.payload
        
        // Evaluate offer
        let evaluation = evaluate_offer(offer)
        
        match evaluation {
            {accepted: true} => {
                // Accept offer
                respond({
                    type: "accept"
                    payload: {
                        offer: offer
                        terms: offer.terms
                    }
                })
            }
            {counter: true, terms: t} => {
                // Counter-offer
                if state.attempts < state.max_attempts {
                    state.attempts = state.attempts + 1
                    respond({
                        type: "counter"
                        payload: {
                            terms: t
                            attempt: state.attempts
                            max_attempts: state.max_attempts
                        }
                    })
                } else {
                    // Reject
                    respond({
                        type: "reject"
                        payload: {
                            reason: "Max attempts reached"
                            final_offer: state.best_offer
                        }
                    })
                }
            }
            _ => {
                // Reject
                respond({
                    type: "reject"
                    payload: {
                        reason: "Invalid offer"
                    }
                })
            }
        }
    }
    
    fn evaluate_offer(offer) -> {accepted: bool, counter: bool, terms: any} {
        let price = offer.terms.price
        let deadline = offer.terms.deadline
        
        if price >= 100 and deadline <= 7 {
            return {accepted: true}
        } else if price >= 80 {
            return {
                counter: true
                terms: {
                    price: price + 10
                    deadline: deadline
                }
            }
        } else {
            return {
                counter: true
                terms: {
                    price: price * 1.5
                    deadline: deadline - 2
                }
            }
        }
    }
}
Example 3: ML Training Agent
vireo
// ml_agent.vireo
import ml
import tensor

agent MLAgent {
    name: "MLAgent"
    version: "1.0.0"
    
    capabilities: ["ml_training", "inference"]
    
    state {
        model: null
        trained: false
        accuracy: 0.0
    }
    
    on message "train" {
        let config = message.payload
        
        // Build model
        let model = ml.nn.Sequential(
            ml.nn.Linear(config.input_dim, config.hidden_dim),
            ml.nn.ReLU(),
            ml.nn.Dropout(config.dropout_rate),
            ml.nn.Linear(config.hidden_dim, config.output_dim),
            ml.nn.Softmax()
        )
        
        // Train model
        let train_result = model.train(
            x_train: config.x_train,
            y_train: config.y_train,
            epochs: config.epochs,
            batch_size: config.batch_size,
            learning_rate: config.learning_rate
        )
        
        state.model = model
        state.trained = true
        state.accuracy = train_result.accuracy
        
        respond({
            type: "training_complete"
            payload: {
                accuracy: train_result.accuracy
                loss: train_result.loss
                epochs: config.epochs
                model_hash: hash(model)
            }
        })
    }
    
    on message "predict" {
        if not state.trained {
            respond({
                type: "error"
                payload: {
                    error: "Model not trained"
                }
            })
            return
        }
        
        let prediction = state.model.forward(message.payload.input)
        
        respond({
            type: "prediction"
            payload: {
                output: prediction
                confidence: prediction.max()
                model_accuracy: state.accuracy
            }
        })
    }
}
🔗 Next Steps
Protocol Guide

Security Guide

API Reference

Standard Library Reference

🆘 Need Help?
Join our Discord

Open an Issue

Check the Examples