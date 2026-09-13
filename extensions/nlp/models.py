# ============================================================
# VIREO NLP MODELS
# ============================================================
"""
Natural Language Processing models for Vireo.

Supports:
- Text embeddings (BERT)
- Text generation (GPT-2)
- Text classification (placeholder)
"""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class NLPModel:
    """Base class for NLP models."""
    
    def __init__(self, model_name: str, device: Optional[str] = None):
        self.model_name = model_name
        self.device = device or "cpu"
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
    
    def load(self):
        raise NotImplementedError
    
    def predict(self, text, **kwargs):
        raise NotImplementedError
    
    def info(self) -> Dict[str, Any]:
        return {
            "name": self.model_name,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "type": self.__class__.__name__
        }


class TextEmbedder(NLPModel):
    """Text embedder using BERT."""
    
    SUPPORTED = ["bert_base", "bert_large"]
    
    def __init__(self, model_name: str = "bert_base", device: Optional[str] = None):
        super().__init__(model_name, device)
        self.max_length = 512
    
    def load(self):
        if self.is_loaded:
            return self
        
        try:
            from transformers import BertModel, BertTokenizer
            
            model_map = {
                "bert_base": "bert-base-uncased",
                "bert_large": "bert-large-uncased",
            }
            
            model_id = model_map[self.model_name]
            self.tokenizer = BertTokenizer.from_pretrained(model_id)
            self.model = BertModel.from_pretrained(model_id)
            self.model.eval()
            
            if self.device == "cuda":
                self.model = self.model.cuda()
            
            self.is_loaded = True
            logger.info(f"✅ TextEmbedder {self.model_name} loaded")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load embedder: {e}")
        
        return self
    
    def predict(self, text: str, **kwargs):
        if not self.is_loaded:
            self.load()
        
        try:
            import torch
            
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=True
            )
            
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return {
                "model": self.model_name,
                "embeddings": embeddings.cpu().numpy().tolist(),
                "shape": list(embeddings.shape),
                "text": text[:100] + ("..." if len(text) > 100 else "")
            }
            
        except Exception as e:
            return {"error": str(e)}


class TextGenerator(NLPModel):
    """Text generator using GPT-2."""
    
    SUPPORTED = ["gpt2", "gpt2_medium", "gpt2_large"]
    
    def load(self):
        if self.is_loaded:
            return self
        
        try:
            from transformers import GPT2LMHeadModel, GPT2Tokenizer
            
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
            self.model.eval()
            
            if self.device == "cuda":
                self.model = self.model.cuda()
            
            self.is_loaded = True
            logger.info(f"✅ TextGenerator {self.model_name} loaded")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load generator: {e}")
        
        return self
    
    def predict(self, prompt: str, max_new_tokens: int = 50, temperature: float = 0.7):
        if not self.is_loaded:
            self.load()
        
        try:
            import torch
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "model": self.model_name,
                "prompt": prompt,
                "generated": generated_text,
                "new_tokens": max_new_tokens
            }
            
        except Exception as e:
            return {"error": str(e)}


class TextClassifier(NLPModel):
    """Text classifier (placeholder)."""
    
    SUPPORTED = ["classifier"]
    
    def load(self):
        if self.is_loaded:
            return self
        
        self.is_loaded = True
        logger.info(f"✅ TextClassifier {self.model_name} loaded (placeholder)")
        return self
    
    def predict(self, text: str, **kwargs):
        return {
            "model": self.model_name,
            "status": "Text classification is available as a placeholder",
            "note": "Full implementation requires fine-tuned models",
            "labels": ["positive", "neutral", "negative"],
            "confidence": [0.85, 0.10, 0.05]
        }


# ============================================================
# FACTORY
# ============================================================

_NLP_MODELS = {
    "bert_base": TextEmbedder,
    "bert_large": TextEmbedder,
    "gpt2": TextGenerator,
    "gpt2_medium": TextGenerator,
    "gpt2_large": TextGenerator,
    "classifier": TextClassifier,
}


def load_nlp_model(model_name: str, **kwargs) -> NLPModel:
    """Load an NLP model."""
    if model_name not in _NLP_MODELS:
        raise ValueError(f"Unknown model: {model_name}. Available: {list_nlp_models()}")
    
    model = _NLP_MODELS[model_name](model_name, **kwargs)
    model.load()
    return model


def list_nlp_models() -> List[str]:
    """List all available NLP models."""
    return list(_NLP_MODELS.keys())