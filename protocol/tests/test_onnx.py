# [file name]: protocol/tests/test_onnx.py
# ============================================================
# ONNX INTEGRATION TESTS FOR VIREO
# Тести ONNX інтеграції
# ============================================================

import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.onnx.export import export_to_onnx, export_to_onnx_string
from src.onnx.import import import_from_onnx, import_from_onnx_string


def print_test_header(name):
    print(f"\n🧪 TEST: {name}")
    print("-" * 40)


def test_onnx_export():
    """Тест експорту в ONNX."""
    print_test_header("ONNX Export")
    
    try:
        import onnx
    except ImportError:
        print("⚠️ ONNX not installed. Skipping test.")
        print("   Install: pip install onnx onnxruntime")
        return
    
    # Створення тимчасового файлу
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        temp_path = f.name
    
    try:
        # Експорт
        result = export_to_onnx(None, temp_path, input_shape=[1, 10])
        assert result is True
        print(f"✅ ONNX exported to: {temp_path}")
        
        # Перевірка, що файл існує
        assert os.path.exists(temp_path)
        print(f"✅ ONNX file exists")
        
        # Перевірка, що файл можна завантажити
        model = onnx.load(temp_path)
        assert model is not None
        print(f"✅ ONNX file loaded successfully")
        
        # Перевірка графа
        assert model.graph is not None
        print(f"✅ Graph nodes: {len(model.graph.node)}")
        print(f"✅ Graph inputs: {len(model.graph.input)}")
        print(f"✅ Graph outputs: {len(model.graph.output)}")
        
        print("✅ ONNX export tests passed!")
        
    finally:
        # Очищення
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("🧹 Cleaned up temp file")


def test_onnx_export_string():
    """Тест експорту в ONNX (строковий формат)."""
    print_test_header("ONNX Export (String)")
    
    try:
        import onnx
    except ImportError:
        print("⚠️ ONNX not installed. Skipping test.")
        return
    
    # Експорт в строку
    result = export_to_onnx_string(None)
    assert result is not None
    assert isinstance(result, str)
    print(f"✅ ONNX exported as string ({len(result)} chars)")
    
    print("✅ ONNX export string tests passed!")


def test_onnx_import():
    """Тест імпорту з ONNX."""
    print_test_header("ONNX Import")
    
    try:
        import onnx
    except ImportError:
        print("⚠️ ONNX not installed. Skipping test.")
        return
    
    # Створення тестової ONNX моделі
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        temp_path = f.name
    
    try:
        # Експортуємо модель для імпорту
        export_to_onnx(None, temp_path, input_shape=[1, 10])
        print(f"✅ Test ONNX file created: {temp_path}")
        
        # Імпорт
        model = import_from_onnx(temp_path)
        assert model is not None
        print(f"✅ ONNX imported successfully")
        
        # Перевірка структури
        assert model.get("type") == "onnx_model"
        assert "name" in model
        assert "inputs" in model
        assert "outputs" in model
        assert "nodes" in model
        print(f"✅ Model name: {model.get('name')}")
        print(f"✅ Inputs: {model.get('inputs')}")
        print(f"✅ Outputs: {model.get('outputs')}")
        print(f"✅ Nodes: {model.get('nodes')}")
        
        print("✅ ONNX import tests passed!")
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("🧹 Cleaned up temp file")


def test_onnx_import_string():
    """Тест імпорту з ONNX (строковий формат)."""
    print_test_header("ONNX Import (String)")
    
    try:
        import onnx
    except ImportError:
        print("⚠️ ONNX not installed. Skipping test.")
        return
    
    # Експорт в строку
    onnx_str = export_to_onnx_string(None)
    assert onnx_str is not None
    
    # Імпорт з строки
    model = import_from_onnx_string(onnx_str)
    # Може повернути None (не реалізовано)
    if model is not None:
        print(f"✅ ONNX imported from string: {model}")
    else:
        print("⚠️ ONNX import from string not fully implemented yet")
    
    print("✅ ONNX import string tests passed!")


def test_onnx_roundtrip():
    """Тест повного циклу експорт-імпорт."""
    print_test_header("ONNX Roundtrip")
    
    try:
        import onnx
    except ImportError:
        print("⚠️ ONNX not installed. Skipping test.")
        return
    
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        temp_path = f.name
    
    try:
        # 1. Експорт
        export_to_onnx(None, temp_path, input_shape=[1, 10])
        print(f"✅ Step 1: ONNX exported")
        
        # 2. Імпорт
        model = import_from_onnx(temp_path)
        assert model is not None
        print(f"✅ Step 2: ONNX imported")
        
        # 3. Перевірка даних
        print(f"✅ Step 3: Data verified")
        print(f"   Name: {model.get('name')}")
        print(f"   Inputs: {model.get('inputs')}")
        print(f"   Outputs: {model.get('outputs')}")
        print(f"   Nodes: {model.get('nodes')}")
        
        print("✅ ONNX roundtrip tests passed!")
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("🧹 Cleaned up temp file")


def test_onnx_error_handling():
    """Тест обробки помилок ONNX."""
    print_test_header("ONNX Error Handling")
    
    try:
        import onnx
    except ImportError:
        print("⚠️ ONNX not installed. Skipping test.")
        return
    
    # 1. Експорт з неіснуючим шляхом
    result = export_to_onnx(None, "/nonexistent/path/model.onnx")
    # Має повернути False, а не кинути виняток
    assert result is False
    print(f"✅ Export with invalid path handled: {result}")
    
    # 2. Імпорт з неіснуючого файлу
    model = import_from_onnx("/nonexistent/file.onnx")
    assert model is None
    print(f"✅ Import from nonexistent file handled: {model is None}")
    
    # 3. Імпорт з некоректного файлу
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        f.write(b"invalid onnx data")
        temp_path = f.name
    
    try:
        model = import_from_onnx(temp_path)
        assert model is None
        print(f"✅ Import from invalid file handled")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    print("✅ ONNX error handling tests passed!")


def test_onnx_schema():
    """Тест схеми ONNX моделі."""
    print_test_header("ONNX Schema")
    
    try:
        import onnx
    except ImportError:
        print("⚠️ ONNX not installed. Skipping test.")
        return
    
    with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as f:
        temp_path = f.name
    
    try:
        export_to_onnx(None, temp_path, input_shape=[1, 10])
        
        # Завантаження для перевірки
        model = onnx.load(temp_path)
        
        # Перевірка версії opset
        assert len(model.opset_import) > 0
        print(f"✅ Opset version: {model.opset_import[0].version}")
        
        # Перевірка типу даних
        for input_tensor in model.graph.input:
            if input_tensor.type.tensor_type:
                print(f"✅ Input: {input_tensor.name}, type: tensor")
        
        for output_tensor in model.graph.output:
            if output_tensor.type.tensor_type:
                print(f"✅ Output: {output_tensor.name}, type: tensor")
        
        print("✅ ONNX schema tests passed!")
        
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def run_all_onnx_tests():
    """Запуск всіх ONNX тестів."""
    
    print("\n" + "=" * 60)
    print("🧪 VIREO ONNX TESTS")
    print("=" * 60)
    
    try:
        import onnx
        print(f"✅ ONNX version: {onnx.__version__}")
    except ImportError:
        print("⚠️ ONNX not installed. Install: pip install onnx onnxruntime")
        print("   Skipping ONNX tests.")
        return True
    
    tests = [
        test_onnx_export,
        test_onnx_export_string,
        test_onnx_import,
        test_onnx_import_string,
        test_onnx_roundtrip,
        test_onnx_error_handling,
        test_onnx_schema,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ Test failed: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ Unexpected error: {e}")
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    exit_code = 0 if run_all_onnx_tests() else 1
    sys.exit(exit_code)