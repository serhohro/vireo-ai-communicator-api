# Vireo Language Syntax

## 1. Variables
```vireo
let x = 5
let name = "Vireo"
let is_ready = true
let list = [1, 2, 3]
let map = {name: "Vireo", version: "1.4.3"}
2. Functions
vireo
fn add(a, b) {
    return a + b
}

let result = add(7, 3)
print(result)  // Output: 10
3. Neural Networks
vireo
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dense(128, 10)
    activation Softmax
    loss CrossEntropy
    optimizer Adam(lr=0.001)
}

train MNIST {
    data = "mnist"
    epochs = 10
    batch_size = 64
    lr = 0.001
}
4. Agents
vireo
agent VisionAgent {
    identity: "did:key:z6MkhaXk1BZ4fGqFqQrZ..."
    capability process_image()
    capability detect_objects()
    role: "vision"
}
5. Contracts
vireo
contract Agreement {
    max_tokens: Int = 1000
    max_cost_usd: Float = 0.05
    timeout_sec: Int = 30
    max_rounds: Int = 3
    allowed_actions: List[String] = ["train_model", "predict"]
    condition { max_tokens > 0 }
}
6. Negotiation
vireo
negotiation SecureNegotiation {
    party Initiator: WeatherAgent
    party Provider: ComputeProvider
    timeout = 10s
    max_rounds = 5
    on offer(Agreement: Agreement) {
        if Agreement.max_tokens <= 500 {
            accept()
        } else if negotiation.round < negotiation.max_rounds {
            propose(counter_offer)
        } else {
            reject("Budget exceeded")
        }
    }
}
7. Control Flow
vireo
if x > 10 {
    print("x is large")
} else {
    print("x is small")
}

while i < 10 {
    print(i)
    i = i + 1
}

for item in list {
    print(item)
}
8. Tensor Operations
vireo
let t = Tensor([1, 2, 3, 4, 5])
let t2 = Tensor([5, 4, 3, 2, 1])
let sum = t + t2
let dot = t.matmul(t2)
let transposed = t.transpose()
9. Comments
vireo
// Single line comment

/*
Multi-line
comment
*/
10. Imports
vireo
import math
import tensor
import agent
import contract
import crypto
11. Standard Library
math.v
add(a, b) — Addition

sub(a, b) — Subtraction

mul(a, b) — Multiplication

div(a, b) — Division

pow(a, b) — Power

sqrt(x) — Square root

exp(x) — Exponential

log(x) — Logarithm

sin(x) — Sine

cos(x) — Cosine

tan(x) — Tangent

max(a, b) — Maximum

min(a, b) — Minimum

tensor.v
Tensor(data) — Create tensor

matmul(a, b) — Matrix multiplication

transpose(t) — Transpose

reshape(t, shape) — Reshape

flatten(t) — Flatten

sum(t) — Sum

mean(t) — Mean

max(t) — Maximum

min(t) — Minimum

agent.v
agent — Agent definition

propose — Propose task

commit — Commit to task

reject — Reject task

execute — Execute task

inform — Inform result

contract.v
contract — Contract definition

validate — Validate contract

check — Check condition

crypto.v
generate_keys() — Generate Ed25519 keys

sign(message, private_key) — Sign message

verify(message, signature, public_key) — Verify signature

create_did(public_key) — Create DID