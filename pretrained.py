# ============================================================
# PRETRAINED MODELS FOR VIREO v1.4.3
# РЕАЛЬНІ МОДЕЛІ З ПОПЕРЕДНІМ НАВЧАННЯМ!
# The World's First AI-to-AI Communication Language
# ============================================================
#
# ⚠️ ВИМАГАЄ ВСТАНОВЛЕННЯ ЗАЛЕЖНОСТЕЙ:
#    pip install torch torchvision transformers
# ============================================================

VERSION = "1.4.3"

import logging
from typing import List, Dict, Optional, Union, Any

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vireo.pretrained")

# ============================================================
# ПЕРЕВІРКА ЗАЛЕЖНОСТЕЙ
# ============================================================

try:
    import torch
    import torch.nn as nn
    import torchvision.models as tv_models
    from transformers import (
        BertModel, BertTokenizer,
        GPT2LMHeadModel, GPT2Tokenizer,
        pipeline
    )
    DEPS_AVAILABLE = True
    logger.info("✅ All dependencies loaded (PyTorch, torchvision, transformers)")
except ImportError as e:
    DEPS_AVAILABLE = False
    logger.warning(f"⚠️ Missing dependencies: {e}")
    logger.warning("   Install: pip install torch torchvision transformers")


# ============================================================
# 1. БАЗОВИЙ КЛАС ДЛЯ ВСІХ МОДЕЛЕЙ
# ============================================================

class VireoPretrainedModel:
    """Базовий клас для всіх попередньо навчених моделей."""
    
    def __init__(self, model, tokenizer=None, device=None):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        if hasattr(model, 'to'):
            self.model.to(self.device)
        
        self.model.eval()
        logger.info(f"✅ Model loaded on {self.device}")
    
    def predict(self, *args, **kwargs):
        """Запускає інференс моделі."""
        raise NotImplementedError
    
    def to_dict(self) -> Dict:
        """Повертає інформацію про модель."""
        return {
            "type": self.__class__.__name__,
            "device": self.device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "version": VERSION
        }


# ============================================================
# 2. RESNET (ВСІ ВАРІАНТИ)
# ============================================================

class ResNetModel(VireoPretrainedModel):
    """ResNet модель з попереднім навчанням на ImageNet."""
    
    SUPPORTED_VARIANTS = {
        "resnet18": tv_models.resnet18,
        "resnet34": tv_models.resnet34,
        "resnet50": tv_models.resnet50,
        "resnet101": tv_models.resnet101,
        "resnet152": tv_models.resnet152,
    }
    
    def __init__(self, variant: str = "resnet18", pretrained: bool = True, device=None):
        if not DEPS_AVAILABLE:
            raise ImportError("PyTorch/torchvision not installed")
        
        if variant not in self.SUPPORTED_VARIANTS:
            raise ValueError(f"Unsupported variant: {variant}. Choose from: {list(self.SUPPORTED_VARIANTS.keys())}")
        
        logger.info(f"🔄 Loading {variant}...")
        model_fn = self.SUPPORTED_VARIANTS[variant]
        model = model_fn(weights="DEFAULT" if pretrained else None)
        model.eval()
        
        super().__init__(model, device=device)
        self.variant = variant
        self.pretrained = pretrained
        
        # Нормалізація для ImageNet
        self.mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
    
    def predict(self, image: Union[torch.Tensor, List], top_k: int = 5) -> Dict:
        """
        Передбачає клас зображення.
        
        Args:
            image: Тензор (3, H, W) або список
            top_k: Кількість топ-класів для повернення
        
        Returns:
            Dict: Топ-класи з ймовірностями
        """
        if not isinstance(image, torch.Tensor):
            image = torch.tensor(image, dtype=torch.float32)
        
        if image.dim() == 3:
            image = image.unsqueeze(0)
        
        image = image.to(self.device)
        image = (image / 255.0 - self.mean.to(self.device)) / self.std.to(self.device)
        
        with torch.no_grad():
            output = self.model(image)
            probs = torch.nn.functional.softmax(output, dim=1)
            top_probs, top_indices = probs.topk(top_k, dim=1)
        
        labels = self._get_imagenet_labels()
        results = []
        for i in range(top_k):
            idx = top_indices[0][i].item()
            results.append({
                "class": labels.get(idx, f"Class_{idx}"),
                "probability": top_probs[0][i].item()
            })
        
        return {
            "predictions": results,
            "model": self.variant,
            "pretrained": self.pretrained
        }
    
    def _get_imagenet_labels(self) -> Dict[int, str]:
        """Повертає словник міток ImageNet (спрощено)."""
        return {
            0: "tench", 1: "goldfish", 2: "great white shark",
            3: "tiger shark", 4: "hammerhead shark", 5: "electric ray",
            6: "stingray", 7: "cock", 8: "hen", 9: "ostrich",
            10: "brambling", 11: "goldfinch", 12: "house finch",
            13: "junco", 14: "indigo bunting", 15: "robin",
            # Повний список можна завантажити з:
            # https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt
        }


# ============================================================
# 3. BERT (ВСІ ВАРІАНТИ)
# ============================================================

class BERTModel(VireoPretrainedModel):
    """BERT модель з попереднім навчанням."""
    
    SUPPORTED_VARIANTS = {
        "bert-base-uncased": "bert-base-uncased",
        "bert-large-uncased": "bert-large-uncased",
        "bert-base-cased": "bert-base-cased",
        "bert-large-cased": "bert-large-cased",
    }
    
    def __init__(self, variant: str = "bert-base-uncased", device=None):
        if not DEPS_AVAILABLE:
            raise ImportError("transformers not installed")
        
        if variant not in self.SUPPORTED_VARIANTS:
            raise ValueError(f"Unsupported variant: {variant}")
        
        logger.info(f"🔄 Loading {variant}...")
        model_name = self.SUPPORTED_VARIANTS[variant]
        model = BertModel.from_pretrained(model_name)
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model.eval()
        
        super().__init__(model, tokenizer, device)
        self.variant = variant
    
    def predict(self, text: Union[str, List[str]], max_length: int = 512) -> Dict:
        """
        Отримує ембеддинги тексту через BERT.
        
        Args:
            text: Текст або список текстів
            max_length: Максимальна довжина послідовності
        
        Returns:
            Dict: Ембеддинги та інформація
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length
        )
        
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state
        
        return {
            "embeddings": embeddings.cpu().numpy(),
            "shape": embeddings.shape,
            "model": self.variant,
            "text": text if isinstance(text, str) else text[:2]
        }


# ============================================================
# 4. GPT-2 (ВСІ ВАРІАНТИ)
# ============================================================

class GPT2Model(VireoPretrainedModel):
    """GPT-2 модель з попереднім навчанням для генерації тексту."""
    
    SUPPORTED_VARIANTS = {
        "gpt2": "gpt2",
        "gpt2-medium": "gpt2-medium",
        "gpt2-large": "gpt2-large",
        "gpt2-xl": "gpt2-xl",
    }
    
    def __init__(self, variant: str = "gpt2", device=None):
        if not DEPS_AVAILABLE:
            raise ImportError("transformers not installed")
        
        if variant not in self.SUPPORTED_VARIANTS:
            raise ValueError(f"Unsupported variant: {variant}")
        
        logger.info(f"🔄 Loading {variant}...")
        model_name = self.SUPPORTED_VARIANTS[variant]
        model = GPT2LMHeadModel.from_pretrained(model_name)
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model.eval()
        
        super().__init__(model, tokenizer, device)
        self.variant = variant
    
    def predict(self, prompt: str, max_new_tokens: int = 50, temperature: float = 0.7) -> Dict:
        """
        Генерує текст на основі промпту.
        
        Args:
            prompt: Початковий текст
            max_new_tokens: Максимум нових токенів
            temperature: Температура генерації
        
        Returns:
            Dict: Згенерований текст
        """
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
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
            "prompt": prompt,
            "generated": generated_text,
            "model": self.variant,
            "tokens_generated": len(outputs[0]) - len(inputs["input_ids"][0])
        }


# ============================================================
# 5. ФАБРИКА МОДЕЛЕЙ
# ============================================================

class ModelFactory:
    """Фабрика для створення моделей."""
    
    _instances = {}
    
    @classmethod
    def get_model(cls, model_type: str, variant: str = None, **kwargs):
        """
        Отримує модель (з кешуванням).
        
        Args:
            model_type: "resnet", "bert", "gpt2"
            variant: Варіант моделі
            **kwargs: Додаткові параметри
        
        Returns:
            VireoPretrainedModel: Екземпляр моделі
        """
        if not DEPS_AVAILABLE:
            raise ImportError("Dependencies not installed. Run: pip install torch torchvision transformers")
        
        key = f"{model_type}:{variant or 'default'}"
        
        if key not in cls._instances:
            if model_type == "resnet":
                variant = variant or "resnet18"
                model = ResNetModel(variant, **kwargs)
            elif model_type == "bert":
                variant = variant or "bert-base-uncased"
                model = BERTModel(variant, **kwargs)
            elif model_type == "gpt2":
                variant = variant or "gpt2"
                model = GPT2Model(variant, **kwargs)
            else:
                raise ValueError(f"Unknown model type: {model_type}. Choose from: resnet, bert, gpt2")
            
            cls._instances[key] = model
        
        return cls._instances[key]
    
    @classmethod
    def clear_cache(cls):
        """Очищує кеш моделей."""
        cls._instances = {}
        logger.info("🧹 Model cache cleared")


# ============================================================
# 6. API-СУМІСНІ ФУНКЦІЇ
# ============================================================

def load_model(model_name: str, **kwargs) -> Any:
    """
    Завантажує модель за назвою.
    
    Args:
        model_name: resnet18, resnet50, bert_base, gpt2, etc.
    
    Returns:
        VireoPretrainedModel: Екземпляр моделі
    """
    model_map = {
        # ResNet
        "resnet18": ("resnet", "resnet18"),
        "resnet34": ("resnet", "resnet34"),
        "resnet50": ("resnet", "resnet50"),
        "resnet101": ("resnet", "resnet101"),
        "resnet152": ("resnet", "resnet152"),
        # BERT
        "bert_base": ("bert", "bert-base-uncased"),
        "bert_large": ("bert", "bert-large-uncased"),
        "bert_base_cased": ("bert", "bert-base-cased"),
        "bert_large_cased": ("bert", "bert-large-cased"),
        # GPT-2
        "gpt2": ("gpt2", "gpt2"),
        "gpt2_medium": ("gpt2", "gpt2-medium"),
        "gpt2_large": ("gpt2", "gpt2-large"),
        "gpt2_xl": ("gpt2", "gpt2-xl"),
    }
    
    if model_name not in model_map:
        available = ', '.join(model_map.keys())
        raise ValueError(f"Unknown model: {model_name}. Available: {available}")
    
    model_type, variant = model_map[model_name]
    return ModelFactory.get_model(model_type, variant, **kwargs)


def list_models() -> List[str]:
    """Повертає список доступних моделей."""
    return [
        # ResNet
        "resnet18", "resnet34", "resnet50", "resnet101", "resnet152",
        # BERT
        "bert_base", "bert_large", "bert_base_cased", "bert_large_cased",
        # GPT-2
        "gpt2", "gpt2_medium", "gpt2_large", "gpt2_xl"
    ]


# ============================================================
# 7. ТЕСТУВАННЯ
# ============================================================

def run_tests():
    """Запускає тести для всіх моделей."""
    print("=" * 60)
    print("🧪 VIREO PRETRAINED MODELS v1.4.3 - TEST SUITE")
    print("The World's First AI-to-AI Communication Language")
    print("=" * 60)
    
    if not DEPS_AVAILABLE:
        print("\n❌ Dependencies not available!")
        print("   Run: pip install torch torchvision transformers")
        return False
    
    print("\n✅ Dependencies loaded:")
    print(f"   PyTorch: {torch.__version__}")
    
    try:
        import transformers
        print(f"   Transformers: {transformers.__version__}")
    except:
        pass
    
    print("\n" + "-" * 40)
    
    try:
        # 1. ResNet
        print("\n📦 Testing ResNet models...")
        for variant in ["resnet18", "resnet50", "resnet152"]:
            model = load_model(variant)
            print(f"   ✅ {variant} loaded on {model.device}")
            print(f"      Parameters: {sum(p.numel() for p in model.model.parameters()):,}")
        
        # 2. BERT
        print("\n📦 Testing BERT models...")
        for variant in ["bert_base", "bert_large"]:
            model = load_model(variant)
            print(f"   ✅ {variant} loaded on {model.device}")
            print(f"      Parameters: {sum(p.numel() for p in model.model.parameters()):,}")
        
        # 3. GPT-2
        print("\n📦 Testing GPT-2 models...")
        for variant in ["gpt2", "gpt2_medium"]:
            model = load_model(variant)
            print(f"   ✅ {variant} loaded on {model.device}")
            print(f"      Parameters: {sum(p.numel() for p in model.model.parameters()):,}")
        
        # 4. Тест генерації GPT-2
        print("\n🧪 Testing GPT-2 generation...")
        model = load_model("gpt2")
        result = model.predict("The future of AI is", max_new_tokens=20)
        print(f"   Prompt: {result['prompt']}")
        print(f"   Generated: {result['generated']}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


# ============================================================
# 8. ЗАПУСК
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🌿 VIREO PRETRAINED MODELS v1.4.3")
    print("The World's First AI-to-AI Communication Language")
    print("=" * 60)
    print("\n📋 Available models:", list_models())
    print("\n⚠️ First run will download model weights (~1-2GB)")
    print("=" * 60)
    
    run_tests()