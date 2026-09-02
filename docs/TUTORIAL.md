# 📚 Vireo Tutorial — Complete Guide

**Version:** 2.0.1  
**Last Updated:** 2026-01-15

---

## Table of Contents

- [Part 1: Your First Agent](#part-1-your-first-agent)
- [Part 2: Contracts](#part-2-contracts)
- [Part 3: Multi-Agent Negotiation](#part-3-multi-agent-negotiation)
- [Part 4: Run the System](#part-4-run-the-system)
- [Part 5: Full Example — Multi-Agent Medical Image Analysis](#part-5-full-example--multi-agent-medical-image-analysis)
- [Next Steps](#next-steps)

---

## Part 1: Your First Agent

### 1.1 What is an Agent?

An agent in Vireo is an autonomous entity that can:
- **Discover** capabilities of other agents
- **Negotiate** contracts
- **Execute** tasks
- **Verify** results

### 1.2 Creating a Simple Agent

Create a file `first_agent.py`:

```python
from core.agent.base import BaseAgent, AgentRole
from core.agent.registry import AgentRegistry

class CalculatorAgent(BaseAgent):
    """A simple calculator agent"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            role=AgentRole.WORKER,
            capabilities=["add", "subtract", "multiply", "divide"],
            description="Basic arithmetic operations"
        )
        
        # Register capabilities
        self.register_capability("add", self.add)
        self.register_capability("subtract", self.subtract)
        self.register_capability("multiply", self.multiply)
        self.register_capability("divide", self.divide)
    
    def add(self, a: float, b: float) -> float:
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    
    def start(self):
        print(f"✅ {self.name} agent started")
        print(f"   ID: {self.agent_id}")
        print(f"   Capabilities: {', '.join(self.capabilities)}")
    
    def stop(self):
        print(f"🛑 {self.name} agent stopped")
1.3 Using the Agent
python
# Create agent
agent = CalculatorAgent()
agent.start()

# Register with registry
registry = AgentRegistry()
registry.register(agent)

# Execute capabilities
result = agent.execute("add", {"a": 5, "b": 3})
print(f"5 + 3 = {result['result']}")

result = agent.execute("multiply", {"a": 4, "b": 7})
print(f"4 * 7 = {result['result']}")

# Stop agent
agent.stop()
1.4 Output
text
✅ calculator agent started
   ID: agent-a1b2c3d4
   Capabilities: add, subtract, multiply, divide
5 + 3 = 8
4 * 7 = 28
🛑 calculator agent stopped
Part 2: Contracts
2.1 What is a Contract?
A contract is an agreement between agents specifying:

Parties: Who is involved

Terms: Constraints and limits

Obligations: What each party must do

Conditions: When the contract is valid

On Failure: What happens if something goes wrong

2.2 Creating a Contract
Create contract_example.py:

python
from core.contract.contract import Contract, Terms, Obligation
from core.contract.validator import ContractValidator
from core.agent.base import BaseAgent, AgentRole
from core.agent.registry import AgentRegistry

# Create agents
class DataProviderAgent(BaseAgent):
    def __init__(self):
        super().__init__("data_provider", AgentRole.WORKER, ["provide_data"])
        self.register_capability("provide_data", self.provide_data)
        self._data = {"temperature": 25.5, "humidity": 60, "pressure": 1013}
    
    def provide_data(self, dataset: str = "weather") -> dict:
        print(f"📊 Providing data from {dataset}")
        return self._data
    
    def start(self):
        print(f"✅ {self.name} started")
    
    def stop(self):
        print(f"🛑 {self.name} stopped")

class DataAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("data_analyzer", AgentRole.ANALYST, ["analyze_data"])
        self.register_capability("analyze_data", self.analyze_data)
    
    def analyze_data(self, data: dict) -> dict:
        print(f"🔍 Analyzing data: {data}")
        return {
            "summary": f"Temperature: {data['temperature']}°C, Humidity: {data['humidity']}%",
            "status": "normal" if data["temperature"] < 30 else "warning"
        }
    
    def start(self):
        print(f"✅ {self.name} started")
    
    def stop(self):
        print(f"🛑 {self.name} stopped")

# Create contract
contract = Contract(
    contract_id="data_analysis_001",
    parties=["data_provider", "data_analyzer"],
    terms=Terms(
        max_tokens=500,
        timeout_sec=30,
        max_cost_usd=1.0,
        max_rounds=3
    ),
    obligations={
        "data_provider": Obligation(
            action="provide_data",
            input={"dataset": "weather"},
            output={"data": "weather_data"}
        ),
        "data_analyzer": Obligation(
            action="analyze_data",
            input={"data": "$ref.data_provider.data"},
            output={"summary": "analysis_result"}
        )
    },
    condition="data_analyzer.status == 'normal'",
    on_failure="escalate"
)

# Validate contract
validator = ContractValidator()
errors = validator.validate(contract)
if errors:
    print("❌ Contract validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ Contract is valid")
2.3 Executing a Contract
python
from core.execution.runner import ExecutionRunner

# Initialize agents
provider = DataProviderAgent()
analyzer = DataAnalyzerAgent()

provider.start()
analyzer.start()

# Register agents
registry = AgentRegistry()
registry.register(provider)
registry.register(analyzer)

# Execute contract
runner = ExecutionRunner()

# Register executors
runner.register_executor("provide_data", provider.provide_data)
runner.register_executor("analyze_data", analyzer.analyze_data)

# Execute
result = runner.execute_contract(contract)

if result.status.value == "completed":
    print("\n✅ Contract executed successfully!")
    print(f"Results: {result.result}")
else:
    print(f"\n❌ Execution failed: {result.error}")

provider.stop()
analyzer.stop()
2.4 Output
text
✅ data_provider started
✅ data_analyzer started
📊 Providing data from weather
🔍 Analyzing data: {'temperature': 25.5, 'humidity': 60, 'pressure': 1013}

✅ Contract executed successfully!
Results: {'data_provider': {'success': True, 'result': {'temperature': 25.5, 'humidity': 60, 'pressure': 1013}}, 'data_analyzer': {'success': True, 'result': {'summary': 'Temperature: 25.5°C, Humidity: 60%', 'status': 'normal'}}}
🛑 data_provider stopped
🛑 data_analyzer stopped
Part 3: Multi-Agent Negotiation
3.1 Setting Up Negotiation
Create negotiation.py:

python
import asyncio
from core.agent.base import BaseAgent, AgentRole
from core.agent.registry import AgentRegistry
from core.protocol.state import StateMachine, ProtocolState, ProtocolEvent
from core.contract.contract import Contract, Terms, Obligation
from core.execution.runner import ExecutionRunner
from core.verification.verifier import Verifier

class BuyerAgent(BaseAgent):
    """Agent that negotiates to buy items"""
    
    def __init__(self, max_budget: float = 100.0):
        super().__init__("buyer", AgentRole.WORKER, 
                        ["propose_price", "accept_counter", "final_decision"])
        self.max_budget = max_budget
        self.current_proposal = None
        self.counter_offers = []
        
        self.register_capability("propose_price", self.propose_price)
        self.register_capability("accept_counter", self.accept_counter)
        self.register_capability("final_decision", self.final_decision)
    
    def propose_price(self, item: str = "item") -> dict:
        """Propose an initial price"""
        price = self.max_budget * 0.6  # Start at 60% of max
        self.current_proposal = {"item": item, "price": price}
        print(f"🛒 Buyer proposes {price:.2f} for {item}")
        return {"item": item, "price": price}
    
    def accept_counter(self, counter_price: float) -> dict:
        """Accept or reject a counter offer"""
        self.counter_offers.append(counter_price)
        accepted = counter_price <= self.max_budget
        
        if accepted:
            print(f"✅ Buyer accepts {counter_price:.2f}")
        else:
            print(f"❌ Buyer rejects {counter_price:.2f} (max: {self.max_budget:.2f})")
        
        return {"accepted": accepted, "counter": counter_price}
    
    def final_decision(self, final_price: float) -> dict:
        """Make final decision"""
        accepted = final_price <= self.max_budget
        print(f"📝 Final decision: {'Accepted' if accepted else 'Rejected'} at {final_price:.2f}")
        return {"accepted": accepted, "final_price": final_price}
    
    def start(self):
        print(f"✅ Buyer ready (budget: ${self.max_budget:.2f})")
    
    def stop(self):
        print("🛑 Buyer stopped")

class SellerAgent(BaseAgent):
    """Agent that negotiates to sell items"""
    
    def __init__(self, min_price: float = 50.0):
        super().__init__("seller", AgentRole.WORKER,
                        ["respond_offer", "counter_offer", "final_confirm"])
        self.min_price = min_price
        self.current_offer = None
        
        self.register_capability("respond_offer", self.respond_offer)
        self.register_capability("counter_offer", self.counter_offer)
        self.register_capability("final_confirm", self.final_confirm)
    
    def respond_offer(self, price: float, item: str = "item") -> dict:
        """Respond to a buyer's offer"""
        self.current_offer = {"price": price, "item": item}
        accepted = price >= self.min_price
        
        if accepted:
            print(f"✅ Seller accepts {price:.2f}")
        else:
            print(f"❌ Seller rejects {price:.2f} (min: {self.min_price:.2f})")
        
        return {"accepted": accepted, "price": price}
    
    def counter_offer(self, buyer_price: float) -> dict:
        """Make a counter offer"""
        counter = max(self.min_price, buyer_price * 1.2)
        counter = min(counter, self.min_price * 1.5)
        print(f"🔄 Seller counters with {counter:.2f}")
        return {"counter_price": counter}
    
    def final_confirm(self, final_price: float) -> dict:
        """Confirm final price"""
        accepted = final_price >= self.min_price
        print(f"📝 Final confirm: {'Accepted' if accepted else 'Rejected'} at {final_price:.2f}")
        return {"accepted": accepted, "final_price": final_price}
    
    def start(self):
        print(f"✅ Seller ready (min price: ${self.min_price:.2f})")
    
    def stop(self):
        print("🛑 Seller stopped")
3.2 Running Negotiation
python
async def run_negotiation():
    # Create agents
    buyer = BuyerAgent(max_budget=120.0)
    seller = SellerAgent(min_price=80.0)
    
    buyer.start()
    seller.start()
    
    # Register
    registry = AgentRegistry()
    registry.register(buyer)
    registry.register(seller)
    
    # Create negotiation contract
    contract = Contract(
        contract_id="negotiation_001",
        parties=["buyer", "seller"],
        terms=Terms(
            max_rounds=10,
            timeout_sec=120,
            max_tokens=1000
        ),
        obligations={
            "buyer": Obligation(
                action="propose_price",
                input={"item": "laptop"}
            ),
            "seller": Obligation(
                action="respond_offer",
                input={"price": "$ref.buyer.proposal.price"}
            )
        },
        on_failure="escalate"
    )
    
    # State machine
    state_machine = StateMachine(ProtocolState.PROPOSE)
    
    # Run negotiation rounds
    print("\n🔄 Starting negotiation...\n")
    
    for round_num in range(10):
        print(f"--- Round {round_num + 1} ---")
        
        # Buyer proposes
        buyer_result = buyer.execute("propose_price", {"item": "laptop"})
        proposal = buyer_result["result"]
        price = proposal["price"]
        
        # Check if we should counter
        if price < seller.min_price:
            seller_result = seller.execute("counter_offer", {"buyer_price": price})
            counter = seller_result["result"]["counter_price"]
            
            buyer_result = buyer.execute("accept_counter", {"counter_price": counter})
            
            if buyer_result["result"]["accepted"]:
                price = counter
                print(f"🎉 Agreement reached at {price:.2f}")
                state_machine.transition(ProtocolEvent.ACCEPT)
                break
        else:
            # Seller accepts
            seller_result = seller.execute("respond_offer", {"price": price})
            if seller_result["result"]["accepted"]:
                print(f"🎉 Agreement reached at {price:.2f}")
                state_machine.transition(ProtocolEvent.ACCEPT)
                break
        
        # Final decision
        final_decision = buyer.execute("final_decision", {"final_price": price})
        if final_decision["result"]["accepted"]:
            seller.execute("final_confirm", {"final_price": price})
            print(f"🎉 Final agreement at {price:.2f}")
            break
        
        print("❌ No agreement this round\n")
    
    # Final state
    print(f"\n📊 Negotiation complete. State: {state_machine.state.value}")
    
    buyer.stop()
    seller.stop()

# Run
asyncio.run(run_negotiation())
3.3 Output
text
✅ Buyer ready (budget: $120.00)
✅ Seller ready (min price: $80.00)

🔄 Starting negotiation...

--- Round 1 ---
🛒 Buyer proposes 72.00 for laptop
❌ Seller rejects 72.00 (min: 80.00)
🔄 Seller counters with 86.40
✅ Buyer accepts 86.40
🎉 Agreement reached at 86.40

📊 Negotiation complete. State: accept
🛑 Buyer stopped
🛑 Seller stopped
Part 4: Run the System
4.1 Start the API Server
bash
# Start Redis (required for multi-agent)
redis-server

# Start Vireo API server
python api/server.py
4.2 API Endpoints
Endpoint	Method	Description
/api/agents	GET	List all agents
/api/agents	POST	Create agent
/api/agents/{id}	GET	Get agent details
/api/agents/{id}/execute	POST	Execute capability
/api/contracts	POST	Create contract
/api/contracts/{id}	GET	Get contract details
/api/contracts/{id}/execute	POST	Execute contract
/api/contracts/{id}/verify	POST	Verify contract
/api/state	GET	Get system state
4.3 API Usage Examples
bash
# Create an agent
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "test_agent", "role": "worker", "capabilities": ["analyze"]}'

# Execute capability
curl -X POST http://localhost:8000/api/agents/agent-123/execute \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze", "inputs": {"data": "test"}}'

# Create contract
curl -X POST http://localhost:8000/api/contracts \
  -H "Content-Type: application/json" \
  -d '{"parties": ["agent-123", "agent-456"], "terms": {"timeout_sec": 60}}'
4.4 Web Interface
Open in browser: http://localhost:8000/api/docs

You'll see an interactive Swagger UI for testing all API endpoints.

Part 5: Full Example — Multi-Agent Medical Image Analysis
5.1 Overview
This example demonstrates a complete multi-agent system for medical image analysis:

Radiologist Agent — Analyzes medical images

Diagnosis Agent — Generates diagnosis from analysis

Report Agent — Creates a report

Guardian Agent — Verifies and validates results

5.2 Implementation
Create medical_analysis.py:

python
import asyncio
import json
from typing import Dict, Any
from datetime import datetime

from core.agent.base import BaseAgent, AgentRole
from core.agent.registry import AgentRegistry
from core.contract.contract import Contract, Terms, Obligation
from core.contract.validator import ContractValidator
from core.execution.runner import ExecutionRunner
from core.verification.verifier import Verifier
from core.protocol.state import StateMachine, ProtocolState, ProtocolEvent


class RadiologistAgent(BaseAgent):
    """Agent that analyzes medical images"""
    
    def __init__(self):
        super().__init__(
            "radiologist", 
            AgentRole.WORKER,
            ["analyze_image", "detect_anomalies"],
            "Medical image analysis specialist"
        )
        self.register_capability("analyze_image", self.analyze_image)
        self.register_capability("detect_anomalies", self.detect_anomalies)
    
    def analyze_image(self, image_url: str, model: str = "resnet50") -> dict:
        """Analyze a medical image"""
        print(f"🩻 Analyzing image: {image_url} using {model}")
        
        # Simulate analysis
        import random
        confidence = random.uniform(0.85, 0.98)
        findings = random.choice([
            "Normal", "Benign lesion", "Malignant tumor", 
            "Inflammation", "Infection"
        ])
        
        return {
            "image_url": image_url,
            "model": model,
            "findings": findings,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_anomalies(self, image_url: str) -> dict:
        """Detect anomalies in image"""
        print(f"🔍 Detecting anomalies in: {image_url}")
        
        import random
        anomalies = []
        if random.random() > 0.7:
            anomalies.append({
                "type": "suspicious_region",
                "location": "upper_lobe",
                "size": random.randint(5, 20)
            })
        
        return {
            "image_url": image_url,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies)
        }
    
    def start(self):
        print(f"✅ Radiologist agent ready")
    
    def stop(self):
        print(f"🛑 Radiologist agent stopped")


class DiagnosisAgent(BaseAgent):
    """Agent that generates diagnosis from analysis"""
    
    def __init__(self):
        super().__init__(
            "diagnostician",
            AgentRole.ANALYST,
            ["generate_diagnosis", "assess_risk"],
            "Medical diagnosis specialist"
        )
        self.register_capability("generate_diagnosis", self.generate_diagnosis)
        self.register_capability("assess_risk", self.assess_risk)
    
    def generate_diagnosis(self, analysis: dict) -> dict:
        """Generate diagnosis from analysis"""
        print(f"📋 Generating diagnosis from: {analysis['findings']}")
        
        findings = analysis["findings"]
        confidence = analysis["confidence"]
        
        diagnosis = {
            "primary_diagnosis": findings,
            "confidence_score": confidence,
            "severity": "high" if "malignant" in findings.lower() else "medium",
            "recommendations": []
        }
        
        if findings == "Normal":
            diagnosis["recommendations"].append("No immediate action required")
            diagnosis["severity"] = "low"
        elif "tumor" in findings.lower():
            diagnosis["recommendations"].extend([
                "Schedule follow-up scan",
                "Consider biopsy",
                "Consult with specialist"
            ])
            diagnosis["severity"] = "high"
        else:
            diagnosis["recommendations"].append("Monitor and follow-up")
        
        return diagnosis
    
    def assess_risk(self, diagnosis: dict) -> dict:
        """Assess risk level"""
        severity_map = {"low": 1, "medium": 2, "high": 3}
        risk_level = severity_map.get(diagnosis["severity"], 2)
        
        return {
            "risk_level": diagnosis["severity"],
            "risk_score": risk_level,
            "requires_immediate_action": risk_level >= 3,
            "priority": "high" if risk_level >= 3 else "normal"
        }
    
    def start(self):
        print(f"✅ Diagnosis agent ready")
    
    def stop(self):
        print(f"🛑 Diagnosis agent stopped")


class ReportAgent(BaseAgent):
    """Agent that generates medical reports"""
    
    def __init__(self):
        super().__init__(
            "reporter",
            AgentRole.WORKER,
            ["generate_report", "format_report"],
            "Medical report generator"
        )
        self.register_capability("generate_report", self.generate_report)
        self.register_capability("format_report", self.format_report)
    
    def generate_report(self, diagnosis: dict, patient_id: str) -> dict:
        """Generate a medical report"""
        print(f"📄 Generating report for patient: {patient_id}")
        
        report = {
            "patient_id": patient_id,
            "diagnosis": diagnosis["primary_diagnosis"],
            "confidence": diagnosis["confidence_score"],
            "severity": diagnosis["severity"],
            "recommendations": diagnosis["recommendations"],
            "generated_at": datetime.utcnow().isoformat(),
            "report_id": f"RPT-{datetime.utcnow().strftime('%Y%m%d')}-{patient_id}"
        }
        
        return report
    
    def format_report(self, report: dict, format: str = "json") -> dict:
        """Format report in specified format"""
        print(f"📝 Formatting report as {format}")
        
        if format == "json":
            return {"format": "json", "content": report}
        elif format == "html":
            html = f"""
            <html>
            <head><title>Medical Report</title></head>
            <body>
                <h1>Medical Report</h1>
                <p><strong>Patient ID:</strong> {report['patient_id']}</p>
                <p><strong>Diagnosis:</strong> {report['diagnosis']}</p>
                <p><strong>Confidence:</strong> {report['confidence']:.2%}</p>
                <p><strong>Severity:</strong> {report['severity']}</p>
                <h2>Recommendations</h2>
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report['recommendations'])}
                </ul>
            </body>
            </html>
            """
            return {"format": "html", "content": html}
        else:
            return {"format": format, "content": report}
    
    def start(self):
        print(f"✅ Report agent ready")
    
    def stop(self):
        print(f"🛑 Report agent stopped")


class GuardianAgent(BaseAgent):
    """Agent that verifies and validates results"""
    
    def __init__(self):
        super().__init__(
            "guardian",
            AgentRole.GUARDIAN,
            ["verify_analysis", "validate_report", "check_compliance"],
            "Verification and compliance specialist"
        )
        self.register_capability("verify_analysis", self.verify_analysis)
        self.register_capability("validate_report", self.validate_report)
        self.register_capability("check_compliance", self.check_compliance)
    
    def verify_analysis(self, analysis: dict) -> dict:
        """Verify analysis results"""
        print(f"🔒 Verifying analysis")
        
        issues = []
        
        if analysis["confidence"] < 0.80:
            issues.append("Low confidence detected")
        
        if analysis["findings"] == "Normal" and analysis["confidence"] > 0.99:
            issues.append("Suspiciously high confidence for normal finding")
        
        return {
            "verified": len(issues) == 0,
            "issues": issues,
            "trust_score": 1.0 - (len(issues) * 0.1)
        }
    
    def validate_report(self, report: dict) -> dict:
        """Validate report completeness"""
        print(f"🔒 Validating report")
        
        required_fields = ["patient_id", "diagnosis", "confidence", "severity"]
        missing = [f for f in required_fields if f not in report]
        
        return {
            "valid": len(missing) == 0,
            "missing_fields": missing,
            "completeness": 1.0 - (len(missing) / len(required_fields))
        }
    
    def check_compliance(self, report: dict) -> dict:
        """Check regulatory compliance"""
        print(f"🔒 Checking compliance")
        
        compliance_issues = []
        
        if "diagnosis" not in report:
            compliance_issues.append("Missing diagnosis")
        
        if report.get("severity") == "high":
            compliance_issues.append("High severity requires specialist review")
        
        return {
            "compliant": len(compliance_issues) == 0,
            "issues": compliance_issues,
            "requires_review": len(compliance_issues) > 0
        }
    
    def start(self):
        print(f"✅ Guardian agent ready")
    
    def stop(self):
        print(f"🛑 Guardian agent stopped")
5.3 Running the Full Example
python
async def run_medical_analysis():
    print("🏥 Starting Medical Image Analysis System\n" + "="*50)
    
    # Create agents
    radiologist = RadiologistAgent()
    diagnostician = DiagnosisAgent()
    reporter = ReportAgent()
    guardian = GuardianAgent()
    
    radiologist.start()
    diagnostician.start()
    reporter.start()
    guardian.start()
    
    # Register agents
    registry = AgentRegistry()
    for agent in [radiologist, diagnostician, reporter, guardian]:
        registry.register(agent)
    
    # Create contract
    contract = Contract(
        contract_id="medical_analysis_001",
        parties=["radiologist", "diagnostician", "reporter", "guardian"],
        terms=Terms(
            max_tokens=5000,
            timeout_sec=300,
            max_cost_usd=25.0,
            max_rounds=5
        ),
        obligations={
            "radiologist": Obligation(
                action="analyze_image",
                input={"image_url": "s3://medical/scan_20260115.dcm"},
                output={"analysis": "analysis_result"}
            ),
            "diagnostician": Obligation(
                action="generate_diagnosis",
                input={"analysis": "$ref.radiologist.analysis"},
                output={"diagnosis": "diagnosis_result"}
            ),
            "reporter": Obligation(
                action="generate_report",
                input={
                    "diagnosis": "$ref.diagnostician.diagnosis",
                    "patient_id": "P-12345"
                },
                output={"report": "report_result"}
            ),
            "guardian": Obligation(
                action="verify_analysis",
                input={"analysis": "$ref.radiologist.analysis"},
                output={"verification": "verification_result"}
            )
        },
        condition="diagnostician.diagnosis.confidence_score > 0.85",
        on_failure="escalate"
    )
    
    # Validate contract
    validator = ContractValidator()
    errors = validator.validate(contract)
    if errors:
        print("❌ Contract validation failed:")
        for error in errors:
            print(f"  - {error}")
        return
    
    # Setup execution
    runner = ExecutionRunner()
    runner.register_executor("analyze_image", radiologist.analyze_image)
    runner.register_executor("generate_diagnosis", diagnostician.generate_diagnosis)
    runner.register_executor("generate_report", reporter.generate_report)
    runner.register_executor("verify_analysis", guardian.verify_analysis)
    
    # Execute contract
    print("\n🚀 Executing medical analysis contract...\n")
    result = runner.execute_contract(contract)
    
    if result.status.value == "completed":
        print("✅ Analysis complete!")
        print("\n📊 Results:")
        
        # Extract results
        rad_result = result.result.get("radiologist", {})
        diag_result = result.result.get("diagnostician", {})
        rep_result = result.result.get("reporter", {})
        guard_result = result.result.get("guardian", {})
        
        if rad_result.get("success"):
            analysis = rad_result["result"]
            print(f"\n🩻 Image Analysis:")
            print(f"  Findings: {analysis['findings']}")
            print(f"  Confidence: {analysis['confidence']:.2%}")
        
        if diag_result.get("success"):
            diagnosis = diag_result["result"]
            print(f"\n📋 Diagnosis:")
            print(f"  Primary: {diagnosis['primary_diagnosis']}")
            print(f"  Severity: {diagnosis['severity']}")
            print(f"  Recommendations: {', '.join(diagnosis['recommendations'])}")
        
        if rep_result.get("success"):
            report = rep_result["result"]
            print(f"\n📄 Report:")
            print(f"  Report ID: {report['report_id']}")
            print(f"  Generated: {report['generated_at']}")
        
        if guard_result.get("success"):
            verification = guard_result["result"]
            print(f"\n🔒 Verification:")
            print(f"  Verified: {verification['verified']}")
            print(f"  Trust Score: {verification['trust_score']:.2%}")
            if verification['issues']:
                print(f"  Issues: {', '.join(verification['issues'])}")
        
        # Generate final report
        print("\n" + "="*50)
        print("📋 FINAL REPORT SUMMARY")
        print("="*50)
        
        if guard_result.get("success") and verification['verified']:
            print("✅ ALL VERIFICATIONS PASSED")
            print("🏥 Report is ready for clinical use")
        else:
            print("⚠️ VERIFICATION ISSUES FOUND")
            print("🔴 Report requires human review")
    else:
        print(f"❌ Execution failed: {result.error}")
    
    # Stop agents
    for agent in [radiologist, diagnostician, reporter, guardian]:
        agent.stop()

# Run the example
if __name__ == "__main__":
    asyncio.run(run_medical_analysis())
5.4 Output
text
🏥 Starting Medical Image Analysis System
==================================================
✅ Radiologist agent ready
✅ Diagnosis agent ready
✅ Report agent ready
✅ Guardian agent ready

🚀 Executing medical analysis contract...

🩻 Analyzing image: s3://medical/scan_20260115.dcm using resnet50
📋 Generating diagnosis from: Malignant tumor
📄 Generating report for patient: P-12345
🔒 Verifying analysis

✅ Analysis complete!

📊 Results:

🩻 Image Analysis:
  Findings: Malignant tumor
  Confidence: 92.50%

📋 Diagnosis:
  Primary: Malignant tumor
  Severity: high
  Recommendations: Schedule follow-up scan, Consider biopsy, Consult with specialist

📄 Report:
  Report ID: RPT-20260115-P-12345
  Generated: 2026-01-15T10:30:00Z

🔒 Verification:
  Verified: True
  Trust Score: 100.00%

==================================================
📋 FINAL REPORT SUMMARY
==================================================
✅ ALL VERIFICATIONS PASSED
🏥 Report is ready for clinical use
🛑 Radiologist agent stopped
🛑 Diagnosis agent stopped
🛑 Report agent stopped
🛑 Guardian agent stopped
Next Steps
What You've Learned
✅ How to create and run Vireo agents

✅ How to define and execute contracts

✅ How to run multi-agent negotiations

✅ How to use the API and web interface

✅ How to build a complete multi-agent system

Recommended Next Steps
Explore the specification: Read specification/ for formal details

Check out examples: Browse examples/ for more use cases

Write your own agents: Create agents for your specific needs

Contribute: Submit PRs and RFCs to the project

Join the community: Connect with other Vireo developers

Additional Resources
QUICKSTART.md — Quick start guide

API Documentation — API reference

Roadmap — Project roadmap

Contributing Guide — How to contribute

