# ============================================================
# VIREO MODEL SAVER v1.0.0
# Збереження та завантаження моделей
# ============================================================

import json
import pickle
import os
from typing import Dict, Any, Optional
from datetime import datetime

class ModelSaver:
    """Клас для збереження та завантаження моделей"""
    
    def __init__(self, save_dir='models/'):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    # ============================================================
    # ЗБЕРЕЖЕННЯ
    # ============================================================
    
    def save_model(self, model, name: str, metadata: Optional[Dict] = None):
        """Зберігає модель у файл"""
        if metadata is None:
            metadata = {}
        
        # Додаємо стандартну метадату
        metadata.update({
            'name': name,
            'saved_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'type': model.__class__.__name__ if hasattr(model, '__class__') else 'unknown'
        })
        
        # Зберігаємо модель
        model_path = os.path.join(self.save_dir, f"{name}.model")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Зберігаємо метадату
        meta_path = os.path.join(self.save_dir, f"{name}.meta.json")
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            'status': 'success',
            'model_path': model_path,
            'meta_path': meta_path,
            'name': name,
            'metadata': metadata
        }
    
    def save_weights(self, weights: Dict, name: str):
        """Зберігає ваги моделі"""
        weights_path = os.path.join(self.save_dir, f"{name}.weights.json")
        with open(weights_path, 'w') as f:
            json.dump(weights, f, indent=2)
        return weights_path
    
    def save_config(self, config: Dict, name: str):
        """Зберігає конфігурацію моделі"""
        config_path = os.path.join(self.save_dir, f"{name}.config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return config_path
    
    # ============================================================
    # ЗАВАНТАЖЕННЯ
    # ============================================================
    
    def load_model(self, name: str):
        """Завантажує модель з файлу"""
        model_path = os.path.join(self.save_dir, f"{name}.model")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model {name} not found at {model_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        return model
    
    def load_metadata(self, name: str) -> Dict:
        """Завантажує метадату моделі"""
        meta_path = os.path.join(self.save_dir, f"{name}.meta.json")
        if not os.path.exists(meta_path):
            return {}
        
        with open(meta_path, 'r') as f:
            return json.load(f)
    
    def load_weights(self, name: str) -> Dict:
        """Завантажує ваги моделі"""
        weights_path = os.path.join(self.save_dir, f"{name}.weights.json")
        if not os.path.exists(weights_path):
            return {}
        
        with open(weights_path, 'r') as f:
            return json.load(f)
    
    def load_config(self, name: str) -> Dict:
        """Завантажує конфігурацію моделі"""
        config_path = os.path.join(self.save_dir, f"{name}.config.json")
        if not os.path.exists(config_path):
            return {}
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    # ============================================================
    # ДОДАТКОВІ МЕТОДИ
    # ============================================================
    
    def list_models(self) -> List[str]:
        """Повертає список збережених моделей"""
        models = []
        for file in os.listdir(self.save_dir):
            if file.endswith('.model'):
                models.append(file.replace('.model', ''))
        return models
    
    def delete_model(self, name: str) -> bool:
        """Видаляє модель"""
        model_path = os.path.join(self.save_dir, f"{name}.model")
        meta_path = os.path.join(self.save_dir, f"{name}.meta.json")
        weights_path = os.path.join(self.save_dir, f"{name}.weights.json")
        config_path = os.path.join(self.save_dir, f"{name}.config.json")
        
        for path in [model_path, meta_path, weights_path, config_path]:
            if os.path.exists(path):
                os.remove(path)
        
        return True
    
    def get_model_info(self, name: str) -> Dict:
        """Отримує інформацію про модель"""
        metadata = self.load_metadata(name)
        weights = self.load_weights(name)
        config = self.load_config(name)
        
        return {
            'name': name,
            'exists': os.path.exists(os.path.join(self.save_dir, f"{name}.model")),
            'metadata': metadata,
            'weights_count': len(weights),
            'config': config
        }


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    # Створюємо зберігач
    saver = ModelSaver('models/')
    
    # Приклад моделі
    class SimpleModel:
        def __init__(self):
            self.weights = {'w1': 1.0, 'w2': 2.0}
        
        def predict(self, x):
            return x * self.weights['w1'] + self.weights['w2']
    
    model = SimpleModel()
    
    # Зберігаємо
    result = saver.save_model(model, 'simple_model', {
        'description': 'Simple linear model',
        'author': 'Vireo Team'
    })
    print("✅ Model saved:", result)
    
    # Завантажуємо
    loaded_model = saver.load_model('simple_model')
    print("✅ Model loaded:", loaded_model)
    
    # Список моделей
    models = saver.list_models()
    print("📁 Available models:", models)