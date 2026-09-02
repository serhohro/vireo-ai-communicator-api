---
```python
#!/usr/bin/env python3
"""Download Vireo models

Usage:
    python scripts/download_model.py [model_name] [--output-dir DIR]
"""

import os
import sys
import argparse
import json
import requests
from tqdm import tqdm
from pathlib import Path


MODELS = {
    "resnet50": {
        "url": "https://huggingface.co/microsoft/resnet-50/resolve/main/model.pt",
        "description": "ResNet50 image classification model",
        "size_mb": 180
    },
    "bert-base": {
        "url": "https://huggingface.co/google-bert/bert-base-uncased/resolve/main/model.safetensors",
        "description": "BERT base model for NLP",
        "size_mb": 440
    },
    "roberta-base": {
        "url": "https://huggingface.co/FacebookAI/roberta-base/resolve/main/model.safetensors",
        "description": "RoBERTa base model for NLP",
        "size_mb": 490
    },
}


def download_model(model_name: str, output_dir: str = "./models/zoo"):
    """Download a model"""
    if model_name not in MODELS:
        print(f"Error: Model '{model_name}' not found")
        print(f"Available models: {', '.join(MODELS.keys())}")
        return False
    
    model_info = MODELS[model_name]
    output_path = Path(output_dir) / model_name
    output_path.mkdir(parents=True, exist_ok=True)
    
    file_path = output_path / "model.pt"
    
    print(f"📥 Downloading {model_name}")
    print(f"   Description: {model_info['description']}")
    print(f"   Size: {model_info['size_mb']} MB")
    
    # Download with progress bar
    try:
        response = requests.get(model_info["url"], stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(file_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=model_name) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        print(f"✅ Downloaded to {file_path}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


def list_models():
    """List available models"""
    print("📋 Available models:")
    print("-" * 50)
    for name, info in MODELS.items():
        print(f"  {name}: {info['description']}")
        print(f"    Size: {info['size_mb']} MB")


def main():
    parser = argparse.ArgumentParser(description="Download Vireo models")
    parser.add_argument("model", nargs="?", help="Model name to download")
    parser.add_argument("--output-dir", default="./models/zoo", help="Output directory")
    parser.add_argument("--list", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
        return
    
    if not args.model:
        print("Error: Please specify a model name")
        print("Usage: python scripts/download_model.py [model_name]")
        list_models()
        sys.exit(1)
    
    success = download_model(args.model, args.output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()