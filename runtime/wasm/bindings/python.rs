// ============================================================
// VIREO WASM PYTHON BINDINGS
// Python зв'язки для WASM
// ============================================================

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use wasmtime::{Engine, Module, Store, Instance, Linker};

/// WASM Python біндінг
#[pyclass]
struct WASMPythonBinding {
    engine: Engine,
    store: Store<()>,
    linker: Linker<()>,
    modules: std::collections::HashMap<String, Module>,
}

#[pymethods]
impl WASMPythonBinding {
    #[new]
    fn new() -> PyResult<Self> {
        let engine = Engine::default();
        let store = Store::new(&engine, ());
        let linker = Linker::new(&engine);
        
        Ok(WASMPythonBinding {
            engine,
            store,
            linker,
            modules: std::collections::HashMap::new(),
        })
    }
    
    /// Компілює WASM модуль
    fn compile(&mut self, name: String, wasm_bytes: Vec<u8>) -> PyResult<bool> {
        match Module::new(&self.engine, &wasm_bytes) {
            Ok(module) => {
                self.modules.insert(name, module);
                Ok(true)
            }
            Err(e) => {
                Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                    format!("WASM compilation failed: {}", e)
                ))
            }
        }
    }
    
    /// Виконує WASM модуль
    fn execute(&mut self, name: String, func_name: String) -> PyResult<PyObject> {
        let module = self.modules.get(&name)
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>(
                format!("Module '{}' not found", name)
            ))?;
        
        match Instance::new(&mut self.store, &module, &[]) {
            Ok(instance) => {
                match instance.get_typed_func::<(), i32>(&mut self.store, &func_name) {
                    Ok(func) => {
                        match func.call(&mut self.store, ()) {
                            Ok(result) => Ok(Python::with_gil(|py| result.into_py(py))),
                            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                                format!("WASM function call failed: {}", e)
                            )),
                        }
                    }
                    Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                        format!("WASM function not found: {}", e)
                    )),
                }
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("WASM instantiation failed: {}", e)
            )),
        }
    }
}

/// Python модуль
#[pymodule]
fn wasm_bindings(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<WASMPythonBinding>()?;
    Ok(())
}