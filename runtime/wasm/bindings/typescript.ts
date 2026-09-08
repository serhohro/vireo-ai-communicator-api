/**
 * Vireo WASM TypeScript Bindings
 * 
 * TypeScript зв'язки для WASM
 */

export interface WASMModule {
  /** Завантажує WASM модуль */
  load(wasmBytes: Uint8Array): Promise<void>;
  
  /** Виконує функцію */
  execute(funcName: string, ...args: any[]): Promise<any>;
  
  /** Отримує експорти */
  getExports(): string[];
}

export class WASMTypeScriptBinding implements WASMModule {
  private instance: WebAssembly.Instance | null = null;
  private module: WebAssembly.Module | null = null;
  private memory: WebAssembly.Memory | null = null;

  /**
   * Завантажує WASM модуль
   */
  async load(wasmBytes: Uint8Array): Promise<void> {
    this.module = await WebAssembly.compile(wasmBytes);
    
    const imports = {
      env: {
        memory: new WebAssembly.Memory({ initial: 1, maximum: 100 }),
        print: (value: number) => {
          console.log(`WASM print: ${value}`);
        },
      },
    };
    
    this.instance = new WebAssembly.Instance(this.module, imports);
    this.memory = imports.env.memory;
  }

  /**
   * Виконує функцію
   */
  async execute(funcName: string, ...args: any[]): Promise<any> {
    if (!this.instance) {
      throw new Error('WASM module not loaded');
    }

    const func = this.instance.exports[funcName] as CallableFunction;
    if (!func) {
      throw new Error(`Function '${funcName}' not found`);
    }

    return func(...args);
  }

  /**
   * Отримує експорти
   */
  getExports(): string[] {
    if (!this.instance) {
      return [];
    }
    return Object.keys(this.instance.exports);
  }

  /**
   * Перевіряє чи завантажено модуль
   */
  isLoaded(): boolean {
    return this.instance !== null;
  }
}

/**
 * Створює WASM біндінг
 */
export function createWASMBinding(): WASMTypeScriptBinding {
  return new WASMTypeScriptBinding();
}