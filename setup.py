# ============================================================
# VIREO v3.0.0 — Setup
# The World's First AI-to-AI Communication Language
# — Open Wire Protocol · WASM · Rust · Formal Verification —
# ============================================================

import os
import re
from setuptools import setup, find_packages
from pathlib import Path

# ============================================================
# ВЕРСІЯ
# ============================================================

def get_version():
    """Отримує версію з core/__init__.py або __init__.py"""
    version_file = Path(__file__).parent / "core" / "__init__.py"
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    
    # Fallback
    return "3.0.0"

VERSION = get_version()

# ============================================================
# README
# ============================================================

def get_readme():
    """Отримує README.md"""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Vireo — The World's First AI-to-AI Communication Language"

# ============================================================
# ЗАЛЕЖНОСТІ
# ============================================================

# Core dependencies (always required)
REQUIRED = [
    # Language
    "lark>=1.1.0",
    "click>=8.1.0",
    
    # Crypto
    "cryptography>=41.0.0",
    "pynacl>=1.5.0",
    "blake3>=0.3.0",
    
    # Protocol
    "protobuf>=4.21.0",
    "flatbuffers>=23.0.0",
    "msgpack>=1.0.0",
    
    # Transport
    "redis>=4.5.0",
    "websockets>=11.0.0",
    "grpcio>=1.54.0",
    "aiohttp>=3.8.0",
    
    # Runtime
    "llvmlite>=0.40.0",
    "numba>=0.57.0",
    
    # Web
    "flask>=2.3.0",
    "flask-cors>=4.0.0",
    "flask-socketio>=5.3.0",
    "python-socketio>=5.9.0",
    "python-dotenv>=1.0.0",
    
    # Utils
    "pyyaml>=6.0",
    "pydantic>=2.0.0",
    "click>=8.1.0",
]

# Extra: GPU support
GPU_REQUIRES = [
    "cupy-cuda11x>=12.0.0",  # CUDA
    "pyopencl>=2022.3.0",     # OpenCL
]

# Extra: WASM runtime
WASM_REQUIRES = [
    "wasmtime>=8.0.0",
]

# Extra: ML models
ML_REQUIRES = [
    "numpy>=1.24.0",
    "torch>=2.0.0",
    "transformers>=4.30.0",
    "torchvision>=0.15.0",
    "pillow>=10.0.0",
]

# Extra: European LLMs
EU_LLM_REQUIRES = [
    "mistralai>=0.1.0",
    "requests>=2.31.0",
]

# Extra: Testing
TEST_REQUIRES = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-benchmark>=4.0.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.3.0",
    "hypothesis>=6.75.0",
]

# Extra: Development
DEV_REQUIRES = [
    "black>=23.0.0",
    "ruff>=0.0.270",
    "mypy>=1.4.0",
    "pre-commit>=3.3.0",
    "isort>=5.12.0",
    "bandit>=1.7.0",
    "safety>=2.3.0",
    "pip-audit>=2.5.0",
]

# Extra: Documentation
DOCS_REQUIRES = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocs-autorefs>=0.4.0",
    "mkdocs-include-markdown-plugin>=4.0.0",
    "mkdocstrings>=0.22.0",
    "mkdocstrings-python>=1.0.0",
]

# Extra: Production
PROD_REQUIRES = [
    "gunicorn>=21.0.0",
    "uvicorn>=0.23.0",
    "python-multipart>=0.0.6",
    "email-validator>=2.0.0",
]

# ============================================================
# SETUP
# ============================================================

setup(
    name="vireo-ai",
    version=VERSION,
    description="Vireo — The World's First AI-to-AI Communication Language",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    author="Serhii",
    author_email="serhohro@vireo.ai",
    license="Apache-2.0",
    license_files=["LICENSE"],
    url="https://github.com/serhohro/vireo-ai-communicator-4",
    project_urls={
        "Documentation": "https://docs.vireo.ai",
        "Source Code": "https://github.com/serhohro/vireo-ai-communicator-4",
        "Issue Tracker": "https://github.com/serhohro/vireo-ai-communicator-4/issues",
        "Changelog": "https://github.com/serhohro/vireo-ai-communicator-4/blob/main/CHANGELOG.md",
    },
    
    # Packages
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
            "examples",
            "examples.*",
            "scripts",
            "scripts.*",
            "docs",
            "docs.*",
            "web",
            "web.*",
            "evaluations",
            "evaluations.*",
        ]
    ),
    
    # Package data
    package_data={
        "language": [
            "*.lark",
            "stdlib/*.vireo",
            "stdlib/**/*.vireo",
        ],
        "specification": [
            "*.md",
            "*.json",
            "*.proto",
            "*.ebnf",
        ],
        "core": [
            "*.pyi",
            "crypto/*.pyi",
            "protocol/*.pyi",
            "identity/*.pyi",
        ],
    },
    include_package_data=True,
    
    # Entry points
    entry_points={
        "console_scripts": [
            "vireo=cli.main:cli",
            "vireo-server=api.server:main",
            "vireo-wasm=runtime.wasm.compiler:main",
        ],
        "vireo.providers": [
            "mistral=protocol.llm_provider_eu:MistralProvider",
            "aleph_alpha=protocol.llm_provider_eu:AlephAlphaProvider",
            "cohere=protocol.llm_provider_eu:CohereProvider",
        ],
        "vireo.transports": [
            "redis=protocol.transport.redis:RedisTransport",
            "websocket=protocol.transport.websocket:WebSocketTransport",
            "grpc=protocol.transport.grpc:GRPCTransport",
        ],
        "vireo.sandboxes": [
            "level1=core.sandbox.level1:SandboxLevel1",
            "level2=core.sandbox.level2:SandboxLevel2",
            "level3=core.sandbox.level3:SandboxLevel3",
        ],
        "pytest11": [
            "vireo=conftest",
        ],
    },
    
    # Dependencies
    install_requires=REQUIRED,
    extras_require={
        "gpu": GPU_REQUIRES,
        "wasm": WASM_REQUIRES,
        "ml": ML_REQUIRES,
        "eu-llm": EU_LLM_REQUIRES,
        "test": TEST_REQUIRES,
        "dev": DEV_REQUIRES,
        "docs": DOCS_REQUIRES,
        "prod": PROD_REQUIRES,
        "all": (
            GPU_REQUIRES + WASM_REQUIRES + ML_REQUIRES + 
            EU_LLM_REQUIRES + TEST_REQUIRES + DEV_REQUIRES + 
            DOCS_REQUIRES + PROD_REQUIRES
        ),
    },
    
    # Python version
    python_requires=">=3.9",
    
    # Classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Human-Machine Interfaces",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: System :: Distributed Computing",
        "Topic :: Security :: Cryptography",
    ],
    
    # Keywords
    keywords=[
        "vireo",
        "ai",
        "llm",
        "multi-agent",
        "protocol",
        "open-wire",
        "wasm",
        "rust",
        "formal-verification",
        "communication",
        "ai-to-ai",
        "language",
        "compiler",
        "runtime",
        "trust",
        "did",
        "federated-trust",
        "zk-snarks",
    ],
    
    # Options
    zip_safe=False,
    include_package_data=True,
    
    # Build options
    options={
        "build": {
            "build_base": "build",
        },
        "egg_info": {
            "tag_build": "",
            "tag_date": 0,
        },
    },
)

# ============================================================
# POST-INSTALL HOOKS
# ============================================================

# Перевірка після встановлення
if __name__ == "__main__":
    import sys
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("vireo.setup")
    
    logger.info("🌿 Vireo v3.0.0 installed successfully!")
    logger.info("")
    logger.info("📦 Dependencies:")
    logger.info(f"   - Python: {sys.version}")
    logger.info(f"   - Core: {len(REQUIRED)} packages")
    logger.info("")
    logger.info("🔄 Extra features:")
    logger.info("   - GPU:   pip install vireo-ai[gpu]")
    logger.info("   - WASM:  pip install vireo-ai[wasm]")
    logger.info("   - ML:    pip install vireo-ai[ml]")
    logger.info("   - EU LLM: pip install vireo-ai[eu-llm]")
    logger.info("   - All:   pip install vireo-ai[all]")
    logger.info("")
    logger.info("🚀 Quick start:")
    logger.info("   $ vireo --help")
    logger.info("   $ vireo-server")