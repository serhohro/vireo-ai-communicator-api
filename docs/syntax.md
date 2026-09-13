# Vireo Language Syntax

**Version:** v1.4.3

This document describes the complete syntax of the Vireo programming language.

---

## 📋 ЗМІСТ

1. [Overview](#overview)
2. [Basic Syntax](#basic-syntax)
3. [Variables](#variables)
4. [Functions](#functions)
5. [Control Flow](#control-flow)
6. [Neural Networks](#neural-networks)
7. [Agents](#agents)
8. [Contracts](#contracts)
9. [Negotiation](#negotiation)
10. [Tensor Operations](#tensor-operations)
11. [Standard Library](#standard-library)
12. [Comments](#comments)

---

## 1. Overview

Vireo is a declarative programming language designed for AI-to-AI communication. It combines:

- **Neural Network Definition** — `model` blocks
- **Agent Definition** — `agent` blocks with capabilities
- **Contract Definition** — `contract` blocks with resource limits
- **Negotiation** — `negotiation` blocks with state machines
- **General Programming** — variables, functions, control flow

---

## 2. Basic Syntax

### Program Structure

```vireo
// Import modules
import math
import tensor

// Variables
let x = 5
let name = "Vireo"

// Functions
fn add(a, b) {
    return a + b
}

// Models
model MNIST { ... }

// Agents
agent WeatherAgent { ... }

// Contracts
contract Agreement { ... }

// Negotiation
negotiation WeatherNegotiation { ... }
3. Variables
Declaration
vireo
let x = 5
let name = "Vireo"
let is_ready = true
let list = [1, 2, 3, 4, 5]
let map = {name: "Vireo", version: "1.4.3"}
Types
Type	Example	Description
Int	5	Integer number
Float	3.14	Floating point number
String	"hello"	Text string
Bool	true, false	Boolean value
Tensor	Tensor([1,2,3])	Tensor data structure
List	[1, 2, 3]	List of values
Map	{key: value}	Key-value map
4. Functions
Definition
vireo
fn add(a, b) {
    return a + b
}

fn greet(name) {
    return "Hello, " + name + "!"
}

fn calculate(x, y) {
    let sum = x + y
    let product = x * y
    return {sum: sum, product: product}
}
Function Call
vireo
let result = add(7, 3)
print(result)  // Output: 10
5. Control Flow
If Statement
vireo
if x > 10 {
    print("x is large")
} else if x > 5 {
    print("x is medium")
} else {
    print("x is small")
}
While Loop
vireo
let i = 0
while i < 10 {
    print(i)
    i = i + 1
}
For Loop
vireo
for item in list {
    print(item)
}
Break and Continue
vireo
while i < 10 {
    if i == 5 {
        break
    }
    if i % 2 == 0 {
        i = i + 1
        continue
    }
    print(i)
    i = i + 1
}
6. Neural Networks
Model Definition
vireo
model MNIST {
    layer Dense(784, 128)
    activation ReLU
    layer Dropout(0.2)
    layer Dense(128, 64)
    activation ReLU
    layer Dense(64, 10)
    activation Softmax
    loss CrossEntropy
    optimizer Adam(lr=0.001)
}
Layers
Layer	Description	Example
Dense	Fully connected layer	Dense(784, 128)
Conv2D	Convolutional layer	Conv2D(3, 64, 3)
MaxPool2D	Max pooling	MaxPool2D(2, 2)
BatchNorm	Batch normalization	BatchNorm(128)
Dropout	Dropout regularization	Dropout(0.2)
Flatten	Flatten layer	Flatten()
LSTM	LSTM layer	LSTM(128, 64)
Attention	Attention layer	Attention(128)
Activations
Activation	Description
ReLU	Rectified Linear Unit
Sigmoid	Sigmoid activation
Tanh	Hyperbolic tangent
Softmax	Softmax activation
LeakyReLU	Leaky ReLU
ELU	Exponential Linear Unit
GELU	Gaussian Error Linear Unit
Swish	Swish activation
Loss Functions
Loss	Description
CrossEntropy	Cross-entropy loss
MSE	Mean squared error
MAE	Mean absolute error
Huber	Huber loss
KLDiv	KL divergence
BCE	Binary cross entropy
Optimizers
Optimizer	Description
Adam	Adam optimizer
SGD	Stochastic gradient descent
RMSprop	RMSprop optimizer
AdamW	AdamW optimizer
Adamax	Adamax optimizer
Nadam	Nadam optimizer
Lion	Lion optimizer
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
7. Agents
Agent Definition
vireo
agent VisionAgent {
    identity: "did:key:z6MkhaXk1BZ4fGqFqQrZ..."
    capability process_image()
    capability detect_objects()
    role: "vision"
}
Agent Fields
Field	Description	Example
identity	Decentralized identifier	"did:key:z6Mkha..."
capability	Agent capability	process_image()
role	Agent role	"vision"
Agent Communication
vireo
propose VisionAgent {
    task = "Process medical images"
    contract = Agreement {
        max_tokens: 500
    }
}

execute ExecutorAgent {
    contract = Agreement {
        max_tokens: 500
    }
    result = process_images()
    inform(VisionAgent, result)
}
8. Contracts
Contract Definition
vireo
contract Agreement {
    max_tokens: Int = 1000
    max_cost_usd: Float = 0.05
    timeout_sec: Int = 30
    max_rounds: Int = 3
    allowed_actions: List[String] = ["train_model", "predict"]
    condition {
        if max_tokens > 500 {
            requires_approval = true
        }
    }
}
Contract Fields
Field	Type	Default	Description
max_tokens	Int	1000	Maximum tokens
max_cost_usd	Float	0.05	Maximum cost in USD
timeout_sec	Int	30	Timeout in seconds
max_rounds	Int	3	Maximum negotiation rounds
allowed_actions	List[String]	[]	Allowed actions
Contract Conditions
vireo
contract ConditionalContract {
    max_tokens: Int = 500
    timeout_sec: Int = 10
    requires_approval: Bool = true
    
    condition {
        if max_tokens > 200 {
            requires_approval = true
        } else {
            requires_approval = false
        }
    }
}
9. Negotiation
Negotiation Definition
vireo
negotiation SecureNegotiation {
    party Initiator: WeatherAgent
    party Provider: ComputeProvider
    party Guardian: GuardianAgent
    
    timeout = 10s
    max_rounds = 5
    
    on offer(Agreement: agreement) {
        if agreement.max_tokens <= 500 {
            accept()
        } else if negotiation.round < negotiation.max_rounds {
            propose(counter_offer)
        } else {
            reject("Budget exceeded")
        }
    }
}
Negotiation Fields
Field	Description	Example
party	Party in negotiation	party Initiator: WeatherAgent
timeout	Timeout duration	timeout = 10s
max_rounds	Maximum negotiation rounds	max_rounds = 5
on offer	Handler for offers	on offer(Agreement: contract) { ... }
Negotiation Actions
Action	Description
accept()	Accept the offer
reject(reason)	Reject the offer with reason
propose(new_offer)	Propose a counter-offer
request_approval()	Request approval from Guardian
guardian_check()	Perform Guardian security check
10. Tensor Operations
Tensor Creation
vireo
let t1 = Tensor([1, 2, 3, 4, 5])
let t2 = Tensor([[1, 2], [3, 4]])
let t3 = Tensor(5)  // All zeros
Tensor Operations
Operation	Description	Example
+	Addition	t1 + t2
-	Subtraction	t1 - t2
*	Multiplication	t1 * t2
/	Division	t1 / t2
matmul	Matrix multiplication	t1.matmul(t2)
transpose	Transpose	t1.transpose()
reshape	Reshape	t1.reshape([5, 1])
flatten	Flatten	t1.flatten()
sum	Sum	t1.sum()
mean	Mean	t1.mean()
max	Maximum	t1.max()
min	Minimum	t1.min()
11. Standard Library
Math Module (math.v)
vireo
import math

let result = math.add(5, 3)   // 8
let result2 = math.sqrt(16)   // 4
let result3 = math.pow(2, 3)  // 8
Tensor Module (tensor.v)
vireo
import tensor

let t = tensor.Tensor([1, 2, 3])
let t2 = tensor.Tensor([4, 5, 6])
let sum = tensor.add(t, t2)
Agent Module (agent.v)
vireo
import agent

let a = agent.Agent("weather")
agent.register_capability(a, "predict")
agent.propose(a, "Predict weather")
Contract Module (contract.v)
vireo
import contract

let c = contract.Contract(max_tokens=1000)
contract.validate(c)
contract.execute(c, task)
Crypto Module (crypto.v)
vireo
import crypto

let keys = crypto.generate_keys()
let signature = crypto.sign(message, keys.private)
let valid = crypto.verify(message, signature, keys.public)
12. Comments
Single-line Comments
vireo
// This is a single-line comment
let x = 5  // This is also a comment
Multi-line Comments
vireo
/*
This is a multi-line comment
It can span multiple lines
*/
📋 KEYWORDS
Keyword	Description
let	Variable declaration
fn	Function definition
return	Return value
if	Conditional
else	Else branch
while	While loop
for	For loop
print	Print output
model	Neural network model
layer	Neural network layer
activation	Activation function
loss	Loss function
optimizer	Optimizer
train	Training block
predict	Prediction block
evaluate	Evaluation block
agent	Agent definition
identity	Agent identity
capability	Agent capability
role	Agent role
contract	Contract definition
condition	Contract condition
negotiation	Negotiation definition
party	Negotiation party
timeout	Timeout setting
max_rounds	Maximum rounds
on	Event handler
offer	Offer handler
accept	Accept action
reject	Reject action
propose	Propose action
execute	Execute action
inform	Inform action
import	Import module