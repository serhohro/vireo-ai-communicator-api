# 📝 Vireo Syntax Reference

## Overview

Vireo syntax combines readability of Python with the power of Rust.

---

## Variables

```vireo
let x = 5
let name = "Vireo"
let is_ai = True
let pi = 3.14159
Constants
vireo
const MAX_EPOCHS = 100
const LEARNING_RATE = 0.001
Functions
vireo
fn add(a, b) {
    return a + b
}

fn greet(name: Str) -> Str {
    return "Hello, " + name
}
Conditionals
vireo
let x = 10

if x > 5 {
    print "x is greater than 5"
} else {
    print "x is less than or equal to 5"
}
Loops
For Loop
vireo
for i in 0..10 {
    print i
}
While Loop
vireo
let x = 0
while x < 5 {
    print x
    x = x + 1
}
Neural Networks
Model Definition
vireo
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dense(128, 10)
    activation Softmax
    loss CrossEntropy
    optimizer Adam(lr=0.001)
}
Training
vireo
train MNIST {
    data = "mnist"
    epochs = 10
    batch_size = 64
    lr = 0.001
}
Prediction
vireo
predict MNIST {
    data = "test"
}
Evaluation
vireo
evaluate MNIST {
    data = "test"
    metrics = [accuracy, precision, recall, f1]
}
Tensors
vireo
let t = Tensor([1, 2, 3, 4, 5])
let m = Tensor([[1, 2], [3, 4]])
let zeros = Tensor::zeros([3, 3])
let ones = Tensor::ones([2, 4])
let random = Tensor::random([4, 4])
Tensor Operations
vireo
let sum = a + b
let product = a * b
let matmul = a.matmul(b)
let transposed = a.transpose()
let reshaped = a.reshape([4])
Agent Communication
Agent Definition
vireo
agent WeatherAgent {
    identity: "did:key:z6Mkha..."
    public_key: "0x1234..."
    capability temperature_prediction
    capability precipitation_prediction
}
Capability Discovery
vireo
find_agent(capability = "temperature_prediction")
Negotiation
vireo
negotiation WeatherNegotiation {
    party Initiator: WeatherAgent
    party Provider: ComputeAgent
    
    timeout = 5s
    max_rounds = 3
    
    on offer(Agreement) {
        if Agreement.price <= 500 {
            accept(Agreement)
        } else {
            reject("Price too high")
        }
    }
}
Crypto
Signatures
vireo
fn sign(data, private_key) -> Signature {
    return crypto::sign(data, private_key)
}

fn verify(signature, public_key, data) -> Bool {
    return crypto::verify(signature, public_key, data)
}
DID
vireo
let did = did::generate()
let doc = did::create_document(did, public_key)
Comments
vireo
// Single line comment

/*
   Multi-line comment
   Multi-line comment
*/
Keywords
Keyword	Description
let	Variable declaration
const	Constant declaration
fn	Function definition
return	Return value
if / else	Conditional
for / while	Loops
model	Neural network model
train	Training
predict	Prediction
evaluate	Evaluation
agent	Agent definition
negotiation	Negotiation protocol
contract	Contract definition