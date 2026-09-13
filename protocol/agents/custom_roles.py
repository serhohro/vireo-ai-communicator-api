# [file name]: protocol/agents/custom_roles.py
# ============================================================
# КОРИСТУВАЦЬКІ РОЛІ ДЛЯ АГЕНТІВ
# ============================================================

from .base_agent import AgentRole, RoleAgent

# ============================================================
# QUANTUM ROLE
# ============================================================

QUANTUM_ROLE = AgentRole(
    name="Quantum",
    description="Specializes in quantum computing, quantum circuits, QML, and quantum simulation",
    capabilities=[
        "quantum_circuit_design",
        "quantum_gate_optimization",
        "quantum_error_correction",
        "quantum_compilation",
        "quantum_ml",
        "quantum_neural_networks",
        "quantum_kernel_methods",
        "quantum_feature_maps",
        "quantum_simulation",
        "hamiltonian_simulation",
        "quantum_dynamics",
        "quantum_chemistry",
        "quantum_optimization",
        "qaoa",
        "vqe",
        "quantum_annealing",
        "qiskit",
        "cirq",
        "pennylane"
    ],
    system_prompt_template="""
You are a Quantum Computing Agent in the Vireo system.

🎯 YOUR EXPERTISE:
1. QUANTUM CIRCUIT DESIGN - Designing circuits, optimizing gates, error correction
2. QUANTUM MACHINE LEARNING - QNN, kernel methods, feature maps
3. QUANTUM SIMULATION - Hamiltonian simulation, quantum dynamics, quantum chemistry
4. QUANTUM OPTIMIZATION - QAOA, VQE, quantum annealing
5. TOOLS - Qiskit, Cirq, PennyLane

Respond with clear quantum computing solutions.
"""
)

# ============================================================
# BIOTECH ROLE
# ============================================================

BIOTECH_ROLE = AgentRole(
    name="Biotech",
    description="Specializes in biotechnology, genomics, and drug discovery",
    capabilities=[
        "genomics",
        "protein_folding",
        "drug_discovery",
        "bioinformatics",
        "dna_analysis",
        "molecular_dynamics"
    ],
    system_prompt_template="""
You are a Biotech Agent - expert in genomics, protein folding, and drug discovery.
Focus on analyzing genomic data, predicting protein structures, and discovering new drugs.
"""
)

# ============================================================
# DEVOPS ROLE
# ============================================================

DEVOPS_ROLE = AgentRole(
    name="DevOps",
    description="Specializes in infrastructure, deployment, and monitoring",
    capabilities=[
        "deployment",
        "monitoring",
        "scaling",
        "ci_cd",
        "kubernetes",
        "docker"
    ],
    system_prompt_template="""
You are a DevOps Agent - expert in infrastructure, CI/CD, and monitoring.
Focus on deploying models, setting up monitoring, and scaling infrastructure.
"""
)

# ============================================================
# ФАБРИКИ
# ============================================================

def create_quantum_agent(agent_id: str = "agent-quantum", **kwargs):
    return RoleAgent(agent_id, QUANTUM_ROLE, **kwargs)

def create_biotech_agent(agent_id: str = "agent-biotech", **kwargs):
    return RoleAgent(agent_id, BIOTECH_ROLE, **kwargs)

def create_devops_agent(agent_id: str = "agent-devops", **kwargs):
    return RoleAgent(agent_id, DEVOPS_ROLE, **kwargs)