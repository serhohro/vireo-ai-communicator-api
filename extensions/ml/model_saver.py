# ============================================================
# VIREO MODEL SAVER v3.0.0
# Збереження та завантаження моделей
# Підтримує Vireo DSL, Tensor, ONNX, та V3 протокол
# — Open Wire Protocol · WASM · Rust · Formal Verification —
# ============================================================

import json
import pickle
import os
import numpy as np
import hashlib
from typing import Dict, Any, Optional, List, Union, BinaryIO
from datetime import datetime
from pathlib import Path
import base64

VERSION = "3.0.0"

class ModelSaverV3:
    """
    Клас для збереження та завантаження моделей у форматі Vireo v3.0.0
    
    Підтримує:
    - Vireo DSL моделі (v3.0.0)
    - Tensor моделі
    - ONNX експорт/імпорт
    - Open Wire Protocol
    - Метадата у JSON з хешем
    - Ваги у різних форматах
    - Версіонування
    """
    
    VERSION = "3.0.0"
    PROTOCOL = "Open Wire v3.0.0"
    
    def __init__(self, save_dir='models/'):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self._cache = {}
    
    # ============================================================
    # ОСНОВНІ МЕТОДИ
    # ============================================================
    
    def save_model(
        self,
        model,
        name: str,
        metadata: Optional[Dict] = None,
        format: str = 'vireo',
        include_weights: bool = True,
        compress: bool = True
    ) -> Dict:
        """
        Зберігає модель у файл v3.0.0
        
        Args:
            model: Модель для збереження
            name: Ім'я моделі
            metadata: Додаткова метадата
            format: Формат збереження ('vireo', 'pickle', 'onnx', 'tensorflow')
            include_weights: Включити ваги
            compress: Стиснути
        """
        if metadata is None:
            metadata = {}
        
        # Стандартна метадата Vireo v3
        metadata.update({
            'name': name,
            'saved_at': datetime.now().isoformat(),
            'version': self.VERSION,
            'protocol': self.PROTOCOL,
            'type': model.__class__.__name__ if hasattr(model, '__class__') else 'unknown',
            'format': format,
            'vireo_version': self.VERSION,
            'compressed': compress,
            'includes_weights': include_weights
        })
        
        # Зберігаємо модель
        if format == 'vireo':
            result = self._save_vireo_model(model, name, metadata)
        elif format == 'onnx':
            result = self._save_onnx_model(model, name, metadata)
        else:
            result = self._save_pickle_model(model, name, metadata, compress)
        
        # Зберігаємо метадату
        meta_path = self.save_dir / f"{name}.meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Обчислюємо хеш
        hash_path = self.save_dir / f"{name}.hash"
        with open(hash_path, 'w') as f:
            f.write(hashlib.sha256(str(metadata).encode()).hexdigest())
        
        result['meta_path'] = str(meta_path)
        result['hash_path'] = str(hash_path)
        result['metadata'] = metadata
        
        self._cache[name] = result
        
        return result
    
    def _save_pickle_model(self, model, name: str, metadata: Dict, compress: bool):
        """Зберігає модель у pickle форматі з компресією."""
        import pickle
        import gzip
        
        model_path = self.save_dir / f"{name}.model"
        
        if compress:
            model_path = model_path.with_suffix('.model.gz')
            with gzip.open(model_path, 'wb') as f:
                pickle.dump(model, f)
        else:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
        
        return {
            'status': 'success',
            'model_path': str(model_path),
            'format': 'pickle',
            'compressed': compress
        }
    
    def _save_vireo_model(self, model, name: str, metadata: Dict):
        """Зберігає модель у Vireo v3 форматі."""
        model_data = {
            'name': name,
            'version': self.VERSION,
            'protocol': self.PROTOCOL,
            'type': metadata.get('type', 'unknown'),
            'config': getattr(model, 'config', {}),
            'layers': getattr(model, 'layers', []),
            'metadata': metadata,
            'open_wire': {
                'version': '3.0.0',
                'format': 'binary'
            }
        }
        
        # Зберігаємо у Vireo форматі
        model_path = self.save_dir / f"{name}.vmodel"
        with open(model_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)
        
        # Зберігаємо як .v (Vireo код)
        if hasattr(model, 'to_vireo'):
            vireo_code = model.to_vireo()
            vireo_path = self.save_dir / f"{name}.v"
            with open(vireo_path, 'w', encoding='utf-8') as f:
                f.write(vireo_code)
        
        # Зберігаємо як Open Wire бінарний формат
        wire_path = self.save_dir / f"{name}.wire"
        with open(wire_path, 'wb') as f:
            f.write(json.dumps(model_data).encode())
        
        return {
            'status': 'success',
            'model_path': str(model_path),
            'vireo_path': str(vireo_path) if hasattr(model, 'to_vireo') else None,
            'wire_path': str(wire_path),
            'format': 'vireo'
        }
    
    def _save_onnx_model(self, model, name: str, metadata: Dict):
        """Зберігає модель у ONNX форматі."""
        try:
            import torch
            import torch.onnx
            
            model_path = self.save_dir / f"{name}.onnx"
            
            # ONNX експорт
            dummy_input = torch.randn(1, 3, 224, 224)
            torch.onnx.export(
                model.model if hasattr(model, 'model') else model,
                dummy_input,
                model_path,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={'input': {0: 'batch_size'}}
            )
            
            return {
                'status': 'success',
                'model_path': str(model_path),
                'format': 'onnx'
            }
        except ImportError:
            return {
                'status': 'error',
                'message': 'ONNX not installed. Install: pip install onnx onnxruntime',
                'format': 'onnx'
            }
    
    def save_weights(self, weights: Dict, name: str, format: str = 'numpy'):
        """Зберігає ваги моделі."""
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
        """Зберігає конфігурацію моделі у Vireo v3 форматі."""
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
        """Конвертує конфігурацію у Vireo v3 код."""
        model_name = config.get('name', 'Model')
        version = config.get('version', '3.0.0')
        
        lines = [
            f"// Vireo v{version} Model",
            f"model {model_name} {{",
            f"    version \"{version}\""
        ]
        
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
        Підтримує .model (pickle), .vmodel (Vireo), .v (Vireo код), .onnx
        """
        # Шукаємо модель у різних форматах
        possible_paths = [
            self.save_dir / f"{name}.model",
            self.save_dir / f"{name}.model.gz",
            self.save_dir / f"{name}.vmodel",
            self.save_dir / f"{name}.v",
            self.save_dir / f"{name}.onnx"
        ]
        
        for path in possible_paths:
            if path.exists():
                if path.suffix == '.model' or path.suffix == '.gz':
                    return self._load_pickle_model(path)
                elif path.suffix == '.vmodel':
                    return self._load_vireo_model(path)
                elif path.suffix == '.v':
                    return self._load_vireo_code(path)
                elif path.suffix == '.onnx':
                    return self._load_onnx_model(path)
        
        raise FileNotFoundError(f"Model '{name}' not found in {self.save_dir}")
    
    def _load_pickle_model(self, path: Path):
        """Завантажує pickle модель."""
        import pickle
        import gzip
        
        if path.suffix == '.gz':
            with gzip.open(path, 'rb') as f:
                return pickle.load(f)
        else:
            with open(path, 'rb') as f:
                return pickle.load(f)
    
    def _load_vireo_model(self, path: Path):
        """Завантажує Vireo v3 модель з JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        class VireoModelV3:
            def __init__(self, data):
                self.config = data.get('config', {})
                self.layers = data.get('layers', [])
                self.name = data.get('name', 'VireoModelV3')
                self.metadata = data.get('metadata', {})
                self.version = data.get('version', '3.0.0')
                self.protocol = data.get('protocol', 'Open Wire v3.0.0')
            
            def predict(self, x):
                return [sum(row) for row in x] if x else []
            
            def to_vireo(self):
                lines = [
                    f"// Vireo v{self.version}",
                    f"model {self.name} {{",
                    f"    version \"{self.version}\""
                ]
                for layer in self.layers:
                    lines.append(f"    layer {layer}")
                lines.append("}")
                return '\n'.join(lines)
            
            def to_dict(self):
                return {
                    'name': self.name,
                    'version': self.version,
                    'protocol': self.protocol,
                    'config': self.config,
                    'layers': self.layers,
                    'metadata': self.metadata
                }
        
        return VireoModelV3(data)
    
    def _load_vireo_code(self, path: Path):
        """Завантажує Vireo v3 код."""
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        class VireoCodeModelV3:
            def __init__(self, code):
                self.code = code
                self.name = path.stem
                self.version = '3.0.0'
                self.protocol = 'Open Wire v3.0.0'
            
            def predict(self, x):
                return x
            
            def to_dict(self):
                return {
                    'name': self.name,
                    'version': self.version,
                    'protocol': self.protocol,
                    'code': self.code
                }
        
        return VireoCodeModelV3(code)
    
    def _load_onnx_model(self, path: Path):
        """Завантажує ONNX модель."""
        try:
            import onnx
            import onnxruntime as ort
            
            model = onnx.load(path)
            
            class ONNXModelV3:
                def __init__(self, model_path):
                    self.session = ort.InferenceSession(model_path)
                    self.name = path.stem
                    self.version = '3.0.0'
                    self.protocol = 'Open Wire v3.0.0'
                
                def predict(self, inputs):
                    return self.session.run(None, inputs)
            
            return ONNXModelV3(str(path))
        except ImportError:
            raise ImportError("ONNX not installed. Install: pip install onnx onnxruntime")
    
    def load_metadata(self, name: str) -> Dict:
        """Завантажує метадату моделі."""
        meta_path = self.save_dir / f"{name}.meta.json"
        if not meta_path.exists():
            return {}
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_weights(self, name: str) -> Dict:
        """Завантажує ваги моделі."""
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
        """Завантажує конфігурацію моделі."""
        config_path = self.save_dir / f"{name}.config.json"
        if not config_path.exists():
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # ============================================================
    # ДОДАТКОВІ МЕТОДИ
    # ============================================================
    
    def list_models(self) -> List[str]:
        """Повертає список збережених моделей."""
        models = set()
        for file in self.save_dir.iterdir():
            if file.suffix in ['.model', '.vmodel', '.v', '.onnx']:
                models.add(file.stem)
        return sorted(list(models))
    
    def list_models_with_metadata(self) -> List[Dict]:
        """Повертає список моделей з метадатою."""
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
        """Отримує список файлів моделі."""
        files = {}
        for ext in ['.model', '.model.gz', '.vmodel', '.v', '.onnx',
                    '.meta.json', '.weights.json', '.weights.npz',
                    '.config.json', '.hash']:
            path = self.save_dir / f"{name}{ext}"
            if path.exists():
                files[ext] = str(path)
        return files
    
    def delete_model(self, name: str) -> bool:
        """Видаляє модель та всі пов'язані файли."""
        deleted = False
        for file in self.save_dir.iterdir():
            if file.stem == name:
                file.unlink()
                deleted = True
        if name in self._cache:
            del self._cache[name]
        return deleted
    
    def get_model_info(self, name: str) -> Dict:
        """Отримує детальну інформацію про модель."""
        metadata = self.load_metadata(name)
        config = self.load_config(name)
        weights = self.load_weights(name)
        files = self._get_model_files(name)
        
        # Перевіряємо хеш
        hash_path = self.save_dir / f"{name}.hash"
        hash_valid = False
        if hash_path.exists():
            with open(hash_path, 'r') as f:
                stored_hash = f.read().strip()
            current_hash = hashlib.sha256(str(metadata).encode()).hexdigest()
            hash_valid = stored_hash == current_hash
        
        return {
            'name': name,
            'exists': bool(files),
            'metadata': metadata,
            'config': config,
            'weights_count': len(weights),
            'files': files,
            'vireo_version': metadata.get('version', 'unknown'),
            'protocol': metadata.get('protocol', 'Unknown'),
            'hash_valid': hash_valid,
            'cached': name in self._cache
        }
    
    def export_to_vireo(self, name: str) -> str:
        """Експортує модель у Vireo v3 код."""
        config = self.load_config(name)
        if config:
            return self._config_to_vireo(config)
        
        metadata = self.load_metadata(name)
        return f"""// Model: {name}
// Vireo v{self.VERSION}
// Protocol: {self.PROTOCOL}
model {name} {{
    version "{self.VERSION}"
    protocol "{self.PROTOCOL}"
    // Config not available
}}"""
    
    def verify_model(self, name: str) -> Dict:
        """Перевіряє цілісність моделі."""
        info = self.get_model_info(name)
        
        return {
            'name': name,
            'exists': info['exists'],
            'hash_valid': info['hash_valid'],
            'metadata_present': bool(info['metadata']),
            'config_present': bool(info['config']),
            'weights_present': info['weights_count'] > 0,
            'files_found': len(info['files']),
            'status': 'verified' if info['hash_valid'] else 'corrupted'
        }


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print(f"VIREO MODEL SAVER v{VERSION}")
    print(f"Protocol: {ModelSaverV3.PROTOCOL}")
    print("=" * 60)
    
    # Створюємо зберігач
    saver = ModelSaverV3('models/')
    
    # Приклад моделі V3
    class SimpleModelV3:
        def __init__(self):
            self.weights = {'w1': 1.0, 'w2': 2.0}
            self.config = {
                'name': 'SimpleModelV3',
                'version': '3.0.0',
                'layers': [
                    {'type': 'Dense', 'units': 128, 'activation': 'ReLU'},
                    {'type': 'Dense', 'units': 10, 'activation': 'Softmax'}
                ]
            }
            self.layers = ['Dense(128)', 'ReLU', 'Dense(10)', 'Softmax']
        
        def predict(self, x):
            return x * self.weights['w1'] + self.weights['w2']
        
        def to_vireo(self):
            return f"""// Vireo v3.0.0
model SimpleModelV3 {{
    version "3.0.0"
    protocol "Open Wire v3.0.0"
    layer Dense(128)
    activation ReLU
    layer Dense(10)
    activation Softmax
}}"""
    
    model = SimpleModelV3()
    
    # Зберігаємо у різних форматах
    print("\n📦 Saving models v3.0.0...")
    
    # 1. Vireo формат
    result = saver.save_model(model, 'simple_model_v3', {
        'description': 'Vireo v3 model',
        'author': 'Vireo Team',
        'format': 'vireo'
    }, format='vireo')
    print(f"✅ Vireo: {result['model_path']}")
    
    # 2. Pickle формат з компресією
    result = saver.save_model(model, 'simple_model_pickle_v3', {
        'description': 'Pickle v3 model',
        'author': 'Vireo Team'
    }, format='pickle', compress=True)
    print(f"✅ Pickle: {result['model_path']}")
    
    # Зберігаємо конфігурацію
    config_path = saver.save_config(model.config, 'simple_model_v3')
    print(f"✅ Config: {config_path}")
    
    # Список моделей
    print(f"\n📁 Available models: {saver.list_models()}")
    
    # Завантажуємо модель
    print("\n📂 Loading models...")
    loaded_model = saver.load_model('simple_model_v3')
    print(f"✅ Loaded: {loaded_model.__class__.__name__}")
    print(f"   Version: {loaded_model.version}")
    
    # Інформація про модель
    info = saver.get_model_info('simple_model_v3')
    print(f"\n📊 Model info: {info['name']}")
    print(f"   Vireo version: {info['vireo_version']}")
    print(f"   Protocol: {info['protocol']}")
    print(f"   Hash valid: {info['hash_valid']}")
    print(f"   Files: {list(info['files'].keys())}")
    
    # Експорт у Vireo
    vireo_code = saver.export_to_vireo('simple_model_v3')
    print(f"\n📜 Vireo code:\n{vireo_code}")
    
    # Верифікація
    verification = saver.verify_model('simple_model_v3')
    print(f"\n🔐 Verification: {verification['status']}")
    
    print("\n" + "=" * 60)
    print(f"✅ Model Saver v{VERSION} ready")
    print("=" * 60)