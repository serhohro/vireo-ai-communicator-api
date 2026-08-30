# ============================================================
# VIREO MODEL SAVER v1.4.3
# Збереження та завантаження моделей
# Підтримує Vireo DSL, Tensor, та стандартні моделі
# ============================================================

import json
import pickle
import os
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

class ModelSaver:
    """
    Клас для збереження та завантаження моделей у форматі Vireo v1.4.3
    
    Підтримує:
    - Vireo DSL моделі
    - Tensor моделі
    - Сумісність з ONNX
    - Метадата у JSON
    - Ваги у різних форматах
    """
    
    VERSION = "1.4.3"
    
    def __init__(self, save_dir='models/'):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    # ============================================================
    # ОСНОВНІ МЕТОДИ
    # ============================================================
    
    def save_model(self, model, name: str, metadata: Optional[Dict] = None, format: str = 'pickle'):
        """
        Зберігає модель у файл
        
        Args:
            model: Модель для збереження
            name: Ім'я моделі
            metadata: Додаткова метадата
            format: Формат збереження ('pickle', 'vireo', 'onnx')
        """
        if metadata is None:
            metadata = {}
        
        # Стандартна метадата Vireo
        metadata.update({
            'name': name,
            'saved_at': datetime.now().isoformat(),
            'version': self.VERSION,
            'type': model.__class__.__name__ if hasattr(model, '__class__') else 'unknown',
            'format': format,
            'vireo_version': self.VERSION
        })
        
        # Зберігаємо модель
        if format == 'vireo':
            result = self._save_vireo_model(model, name, metadata)
        elif format == 'onnx':
            result = self._save_onnx_model(model, name, metadata)
        else:
            result = self._save_pickle_model(model, name, metadata)
        
        # Зберігаємо метадату
        meta_path = self.save_dir / f"{name}.meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        result['meta_path'] = str(meta_path)
        result['metadata'] = metadata
        
        return result
    
    def _save_pickle_model(self, model, name: str, metadata: Dict):
        """Зберігає модель у pickle форматі"""
        model_path = self.save_dir / f"{name}.model"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        return {
            'status': 'success',
            'model_path': str(model_path),
            'format': 'pickle'
        }
    
    def _save_vireo_model(self, model, name: str, metadata: Dict):
        """Зберігає модель у Vireo форматі (JSON)"""
        model_data = {
            'name': name,
            'version': self.VERSION,
            'type': metadata.get('type', 'unknown'),
            'config': getattr(model, 'config', {}),
            'layers': getattr(model, 'layers', []),
            'metadata': metadata
        }
        
        # Зберігаємо у Vireo форматі
        model_path = self.save_dir / f"{name}.vmodel"
        with open(model_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)
        
        # Зберігаємо також як .v (Vireo код)
        if hasattr(model, 'to_vireo'):
            vireo_code = model.to_vireo()
            vireo_path = self.save_dir / f"{name}.v"
            with open(vireo_path, 'w', encoding='utf-8') as f:
                f.write(vireo_code)
        
        return {
            'status': 'success',
            'model_path': str(model_path),
            'format': 'vireo'
        }
    
    def _save_onnx_model(self, model, name: str, metadata: Dict):
        """Зберігає модель у ONNX форматі"""
        try:
            import onnx
            import onnxruntime as ort
            
            # Тут логіка експорту в ONNX
            # Для спрощення повертаємо помилку
            return {
                'status': 'error',
                'message': 'ONNX export not fully implemented yet',
                'format': 'onnx'
            }
        except ImportError:
            return {
                'status': 'error',
                'message': 'ONNX not installed. Install: pip install onnx onnxruntime',
                'format': 'onnx'
            }
    
    def save_weights(self, weights: Dict, name: str, format: str = 'json'):
        """Зберігає ваги моделі"""
        weights_path = self.save_dir / f"{name}.weights"
        
        if format == 'json':
            weights_path = weights_path.with_suffix('.json')
            with open(weights_path, 'w', encoding='utf-8') as f:
                json.dump(weights, f, indent=2, ensure_ascii=False)
        elif format == 'numpy':
            weights_path = weights_path.with_suffix('.npz')
            np.savez_compressed(weights_path, **weights)
        else:
            weights_path = weights_path.with_suffix('.pkl')
            with open(weights_path, 'wb') as f:
                pickle.dump(weights, f)
        
        return str(weights_path)
    
    def save_config(self, config: Dict, name: str):
        """Зберігає конфігурацію моделі у Vireo форматі"""
        config_path = self.save_dir / f"{name}.config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # Також зберігаємо як .v (Vireo код)
        if 'layers' in config:
            vireo_code = self._config_to_vireo(config)
            vireo_path = self.save_dir / f"{name}.config.v"
            with open(vireo_path, 'w', encoding='utf-8') as f:
                f.write(vireo_code)
        
        return str(config_path)
    
    def _config_to_vireo(self, config: Dict) -> str:
        """Конвертує конфігурацію у Vireo код"""
        model_name = config.get('name', 'Model')
        lines = [f"model {model_name} {{"]
        
        for layer in config.get('layers', []):
            if isinstance(layer, dict):
                layer_type = layer.get('type', 'Dense')
                units = layer.get('units', 128)
                lines.append(f"    layer {layer_type}({units})")
                if 'activation' in layer:
                    lines.append(f"    activation {layer['activation']}")
        
        lines.append("}")
        return '\n'.join(lines)
    
    # ============================================================
    # ЗАВАНТАЖЕННЯ
    # ============================================================
    
    def load_model(self, name: str):
        """
        Завантажує модель з файлу
        Підтримує .model (pickle), .vmodel (Vireo), .v (Vireo код)
        """
        # Шукаємо модель у різних форматах
        possible_paths = [
            self.save_dir / f"{name}.model",
            self.save_dir / f"{name}.vmodel",
            self.save_dir / f"{name}.v"
        ]
        
        for path in possible_paths:
            if path.exists():
                if path.suffix == '.model':
                    return self._load_pickle_model(path)
                elif path.suffix == '.vmodel':
                    return self._load_vireo_model(path)
                elif path.suffix == '.v':
                    return self._load_vireo_code(path)
        
        raise FileNotFoundError(f"Model '{name}' not found in {self.save_dir}")
    
    def _load_pickle_model(self, path: Path):
        """Завантажує pickle модель"""
        with open(path, 'rb') as f:
            return pickle.load(f)
    
    def _load_vireo_model(self, path: Path):
        """Завантажує Vireo модель з JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Створюємо просту модель з даних
        class VireoModel:
            def __init__(self, data):
                self.config = data.get('config', {})
                self.layers = data.get('layers', [])
                self.name = data.get('name', 'VireoModel')
                self.metadata = data.get('metadata', {})
            
            def predict(self, x):
                # Проста імітація передбачення
                return [sum(row) for row in x] if x else []
            
            def to_vireo(self):
                lines = [f"model {self.name} {{"]
                for layer in self.layers:
                    lines.append(f"    layer {layer}")
                lines.append("}")
                return '\n'.join(lines)
        
        return VireoModel(data)
    
    def _load_vireo_code(self, path: Path):
        """Завантажує Vireo код"""
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Створюємо модель з Vireo коду
        class VireoCodeModel:
            def __init__(self, code):
                self.code = code
                self.name = path.stem
            
            def predict(self, x):
                return x
        
        return VireoCodeModel(code)
    
    def load_metadata(self, name: str) -> Dict:
        """Завантажує метадату моделі"""
        meta_path = self.save_dir / f"{name}.meta.json"
        if not meta_path.exists():
            return {}
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_weights(self, name: str) -> Dict:
        """Завантажує ваги моделі"""
        possible_paths = [
            self.save_dir / f"{name}.weights.json",
            self.save_dir / f"{name}.weights.npz",
            self.save_dir / f"{name}.weights.pkl"
        ]
        
        for path in possible_paths:
            if path.exists():
                if path.suffix == '.json':
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                elif path.suffix == '.npz':
                    data = np.load(path)
                    return {k: v.tolist() for k, v in data.items()}
                elif path.suffix == '.pkl':
                    with open(path, 'rb') as f:
                        return pickle.load(f)
        
        return {}
    
    def load_config(self, name: str) -> Dict:
        """Завантажує конфігурацію моделі"""
        config_path = self.save_dir / f"{name}.config.json"
        if not config_path.exists():
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # ============================================================
    # ДОДАТКОВІ МЕТОДИ
    # ============================================================
    
    def list_models(self) -> List[str]:
        """Повертає список збережених моделей"""
        models = set()
        for file in self.save_dir.iterdir():
            if file.suffix in ['.model', '.vmodel', '.v']:
                models.add(file.stem)
        return sorted(list(models))
    
    def list_models_with_metadata(self) -> List[Dict]:
        """Повертає список моделей з метадатою"""
        result = []
        for name in self.list_models():
            metadata = self.load_metadata(name)
            result.append({
                'name': name,
                'metadata': metadata,
                'exists': True,
                'files': self._get_model_files(name)
            })
        return result
    
    def _get_model_files(self, name: str) -> Dict:
        """Отримує список файлів моделі"""
        files = {}
        for ext in ['.model', '.vmodel', '.v', '.meta.json', '.weights.json', '.weights.npz', '.config.json']:
            path = self.save_dir / f"{name}{ext}"
            if path.exists():
                files[ext] = str(path)
        return files
    
    def delete_model(self, name: str) -> bool:
        """Видаляє модель та всі пов'язані файли"""
        deleted = False
        for file in self.save_dir.iterdir():
            if file.stem == name:
                file.unlink()
                deleted = True
        return deleted
    
    def get_model_info(self, name: str) -> Dict:
        """Отримує детальну інформацію про модель"""
        metadata = self.load_metadata(name)
        config = self.load_config(name)
        weights = self.load_weights(name)
        files = self._get_model_files(name)
        
        return {
            'name': name,
            'exists': bool(files),
            'metadata': metadata,
            'config': config,
            'weights_count': len(weights),
            'files': files,
            'vireo_version': metadata.get('version', 'unknown')
        }
    
    def export_to_vireo(self, name: str) -> str:
        """Експортує модель у Vireo код"""
        config = self.load_config(name)
        if config:
            return self._config_to_vireo(config)
        
        metadata = self.load_metadata(name)
        return f"// Model: {name}\n// Vireo v{self.VERSION}\nmodel {name} {{\n    // Config not available\n}}"


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("VIREO MODEL SAVER v1.4.3")
    print("=" * 50)
    
    # Створюємо зберігач
    saver = ModelSaver('models/')
    
    # Приклад моделі
    class SimpleModel:
        def __init__(self):
            self.weights = {'w1': 1.0, 'w2': 2.0}
            self.config = {
                'name': 'SimpleModel',
                'layers': [
                    {'type': 'Dense', 'units': 128, 'activation': 'ReLU'},
                    {'type': 'Dense', 'units': 10, 'activation': 'Softmax'}
                ]
            }
            self.layers = ['Dense(128)', 'ReLU', 'Dense(10)', 'Softmax']
        
        def predict(self, x):
            return x * self.weights['w1'] + self.weights['w2']
        
        def to_vireo(self):
            return f"""model SimpleModel {{
    layer Dense(128)
    activation ReLU
    layer Dense(10)
    activation Softmax
}}"""
    
    model = SimpleModel()
    
    # Зберігаємо у різних форматах
    print("\n📦 Saving models...")
    
    # 1. Pickle формат
    result = saver.save_model(model, 'simple_model_pickle', {
        'description': 'Simple linear model',
        'author': 'Vireo Team',
        'format': 'pickle'
    })
    print(f"✅ Pickle: {result['model_path']}")
    
    # 2. Vireo формат
    result = saver.save_model(model, 'simple_model_vireo', {
        'description': 'Vireo model',
        'author': 'Vireo Team',
        'format': 'vireo'
    }, format='vireo')
    print(f"✅ Vireo: {result['model_path']}")
    
    # Зберігаємо конфігурацію
    config_path = saver.save_config(model.config, 'simple_model')
    print(f"✅ Config: {config_path}")
    
    # Список моделей
    print(f"\n📁 Available models: {saver.list_models()}")
    
    # Завантажуємо модель
    print("\n📂 Loading models...")
    loaded_model = saver.load_model('simple_model_pickle')
    print(f"✅ Loaded: {loaded_model.__class__.__name__}")
    
    # Інформація про модель
    info = saver.get_model_info('simple_model_vireo')
    print(f"\n📊 Model info: {info['name']}")
    print(f"   Vireo version: {info['vireo_version']}")
    print(f"   Files: {list(info['files'].keys())}")
    
    # Експорт у Vireo
    vireo_code = saver.export_to_vireo('simple_model')
    print(f"\n📜 Vireo code:\n{vireo_code}")
    
    print("\n" + "=" * 50)
    print("✅ Model Saver v1.4.3 ready")
    print("=" * 50)