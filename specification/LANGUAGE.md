
```markdown
# 📝 Vireo Language Specification

**Version:** 2.0.1  
**Status:** Draft  
**Last Updated:** 2026-01-15

---

## 1. Overview

Vireo is a domain-specific language designed for defining AI agents, their capabilities, and contracts between them.

### Design Goals

1. **Human-readable** — Clear syntax for defining agents
2. **Machine-executable** — Interpretable by Vireo runtime
3. **Secure** — Type-safe and bounded operations
4. **Declarative** — Focus on WHAT, not HOW

---

## 2. Basic Syntax

### Comments

```vireo
// Single-line comment
/* Multi-line
   comment */
Program Structure
vireo
// Import standard library
import math
import crypto

// Define an agent
agent "my_agent" {
    // Agent definition
}

// Define a contract
contract "my_contract" {
    // Contract definition
}

// Execute an action
execute my_action(args) -> result
3. Agents
Agent Definition
vireo
agent <name> {
    [extends: <parent_agent>]
    [description: <string>]
    
    capability <name> {
        input: <type> <name>
        [output: <type> <name>]
        action: <string>
        [cost: <number>]
        [estimated_tokens: <number>]
    }
    
    [state: {
        <key>: <value>
    }]
}
Example
vireo
agent "image_analyzer" {
    description: "Analyzes medical images"
    
    capability "analyze" {
        input: image_url: string
        input: model: string
        output: result: json
        action: "Analyze image using {model}"
        cost: 1.0
        estimated_tokens: 500
    }
    
    capability "report" {
        input: analysis: json
        output: report: string
        action: "Generate report from analysis"
        cost: 0.5
        estimated_tokens: 200
    }
}
4. Capabilities
Capability Structure
vireo
capability <name> {
    input: <type> <name> [= <default>]
    [output: <type> <name>]
    [action: <string>]
    [cost: <number>]
    [estimated_tokens: <number>]
    [timeout_sec: <number>]
    [requires: [<capability1>, <capability2>]]
    [async: true|false]
}
Types
Type	Description	Example
string	Text	"hello"
number	Integer or float	42, 3.14
boolean	True/False	true, false
json	JSON object	{"key": "value"}
array<T>	List of T	[1, 2, 3]
map<K,V>	Key-value map	{"a": 1}
Example
vireo
capability "train_model" {
    input: dataset: string
    input: epochs: number = 10
    input: batch_size: number = 32
    output: model: string
    action: "Train model on {dataset} for {epochs} epochs"
    cost: 10.0
    estimated_tokens: 5000
    async: true
}
5. Contracts
Contract Structure
vireo
contract <name> {
    parties: [<agent1>, <agent2>, ...]
    
    terms: {
        max_tokens: <number>
        timeout_sec: <number>
        max_cost_usd: <number>
        max_rounds: <number>
        [deadline: <date>]
    }
    
    obligations: {
        <agent_name>: {
            action: <capability_name>
            input: {
                <param>: <value>
            }
            [output: {
                <field>: <value>
            }]
        }
    }
    
    [condition: <boolean_expression>]
    [on_failure: "cancel" | "escalate" | "retry"]
}
Example
vireo
contract "medical_analysis_contract" {
    parties: [image_analyzer, reporter]
    
    terms: {
        max_tokens: 1000
        timeout_sec: 120
        max_cost_usd: 5.0
        max_rounds: 3
    }
    
    obligations: {
        image_analyzer: {
            action: analyze
            input: {
                image_url: "s3://medical/scan.jpg"
                model: "resnet50"
            }
            output: {
                result: $ref.analysis
            }
        }
        reporter: {
            action: report
            input: {
                analysis: $ref.image_analyzer.analysis
            }
        }
    }
    
    condition: analysis.confidence > 0.85
    on_failure: "escalate"
}
6. Expressions
Literals
vireo
// String
"hello world"

// Number
42
3.14

// Boolean
true
false

// Null
null

// Array
[1, 2, 3]

// Object
{"key": "value"}

// Reference
$ref.agent.capability.output
Operators
Operator	Description
+	Addition/Concatenation
-	Subtraction
*	Multiplication
/	Division
==	Equality
!=	Inequality
<	Less than
>	Greater than
<=	Less than or equal
>=	Greater than or equal
&&	Logical AND
||	Logical OR
!	Logical NOT
?:	Ternary
Example
vireo
// Arithmetic
total = price * quantity
discount = total * 0.1
final = total - discount

// Comparison
if confidence > 0.95 {
    result = "high_confidence"
} else if confidence > 0.8 {
    result = "medium_confidence"
} else {
    result = "low_confidence"
}

// Ternary
status = is_valid ? "valid" : "invalid"
7. Control Flow
If-Else
vireo
if <condition> {
    // code
} else if <condition> {
    // code
} else {
    // code
}
Loop
vireo
loop <number> {
    // code
}

loop while <condition> {
    // code
}

loop for <item> in <collection> {
    // code
}
Example
vireo
loop 10 {
    result = process(i)
}

loop while not done {
    response = call_agent(target)
    done = response.finished
}

loop for item in items {
    results[item.id] = analyze(item)
}
8. Standard Library
Math
vireo
math.add(a, b)
math.subtract(a, b)
math.multiply(a, b)
math.divide(a, b)
math.pow(a, b)
math.sqrt(a)
math.sin(a)
math.cos(a)
math.tan(a)
math.log(a)
math.exp(a)
math.max(a, b)
math.min(a, b)
math.clamp(x, min, max)
Tensor (for ML)
vireo
tensor.create(data, shape)
tensor.reshape(tensor, shape)
tensor.add(a, b)
tensor.subtract(a, b)
tensor.multiply(a, b)
tensor.dot(a, b)
tensor.transpose(tensor)
tensor.mean(tensor)
tensor.std(tensor)
tensor.normalize(tensor)
tensor.conv2d(input, kernel, stride, padding)
tensor.relu(tensor)
tensor.softmax(tensor)
tensor.max_pool2d(input, kernel_size, stride)
Agent
vireo
agent.discover(requirements)
agent.propose(contract)
agent.accept(proposal_id)
agent.reject(proposal_id)
agent.commit(contract_id)
agent.verify(contract_id)
agent.escalate(issue)
Contract
vireo
contract.create(parties, terms, obligations)
contract.validate(contract)
contract.sign(contract, private_key)
contract.verify_signature(contract, public_key)
contract.execute(contract)
contract.check_terms(contract)
Crypto
vireo
crypto.generate_keypair()
crypto.sign(message, private_key)
crypto.verify(message, signature, public_key)
crypto.hash(message, algorithm: "sha256")
crypto.encrypt(data, key)
crypto.decrypt(data, key)
Network
vireo
network.send(message, recipient)
network.receive(timeout_sec)
network.broadcast(message)
network.status()
9. Examples
Hello World
vireo
// hello_world.v
agent "greeter" {
    capability "greet" {
        input: name: string
        output: message: string
        action: "Hello, {name}!"
    }
}

execute greet("World") -> result
output result
Neural Network Training
vireo
// neural_network.v
import tensor

agent "trainer" {
    capability "train" {
        input: dataset: string
        input: epochs: number = 10
        input: learning_rate: number = 0.001
        output: model: string
        
        action: "Train neural network on {dataset}"
    }
}

agent "evaluator" {
    capability "evaluate" {
        input: model: string
        input: test_data: string
        output: accuracy: number
        
        action: "Evaluate model on test data"
    }
}

contract "training_contract" {
    parties: [trainer, evaluator]
    terms: {
        max_tokens: 10000
        timeout_sec: 3600
        max_cost_usd: 50.0
    }
    obligations: {
        trainer: {
            action: train
            input: {
                dataset: "s3://data/dataset.csv"
                epochs: 20
            }
            output: { model: $ref.model }
        }
        evaluator: {
            action: evaluate
            input: {
                model: $ref.trainer.model
                test_data: "s3://data/test.csv"
            }
            output: { accuracy: $ref.accuracy }
        }
    }
}

execute training_contract -> result
if result.accuracy > 0.9 {
    output "Model passed evaluation!"
} else {
    output "Model needs improvement."
}
Multi-Agent Negotiation
vireo
// multi_agent_negotiation.v
agent "buyer" {
    capability "buy" {
        input: item: string
        input: max_price: number
        output: purchased: boolean
        
        action: "Buy item for up to {max_price}"
    }
}

agent "seller" {
    capability "sell" {
        input: item: string
        input: min_price: number
        output: sold: boolean
        
        action: "Sell item for at least {min_price}"
    }
}

// Negotiation loop
loop 10 {
    // Buyer proposes price
    buyer.propose(price: 10 + i)
    
    // Seller responds
    if seller.accepts(price) {
        output "Deal reached at price: {price}"
        break
    }
    
    // Seller counters
    counter = seller.get_counter_price()
    output "Seller counter: {counter}"
}
10. Grammar (EBNF)
ebnf
program = { import_statement | agent_definition | contract_definition | execute_statement }

import_statement = "import" IDENTIFIER

agent_definition = "agent" STRING "{" { capability_definition | state_definition } "}"

capability_definition = "capability" IDENTIFIER "{" 
    { input_definition }
    [ output_definition ]
    [ "action" ":" STRING ]
    [ "cost" ":" number ]
    [ "estimated_tokens" ":" number ]
"}"
11. Future Extensions
Pattern Matching — Advanced pattern matching on types

Generics — Generic capabilities and contracts

Modules — Code organization across files

Macros — Compile-time code generation

Async/Await — Native asynchronous operations