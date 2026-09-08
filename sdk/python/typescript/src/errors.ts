/**
 * Vireo TypeScript SDK - Error Classes
 * 
 * @module errors
 */

export class VireoError extends Error {
  public readonly code: string;
  public readonly details: Record<string, any>;

  constructor(message: string, code: string = 'VIREO_0000', details: Record<string, any> = {}) {
    super(message);
    this.name = 'VireoError';
    this.code = code;
    this.details = details;
    Object.setPrototypeOf(this, new.target.prototype);
  }

  public toJSON(): Record<string, any> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      details: this.details,
      stack: this.stack,
    };
  }
}

export class ProtocolError extends VireoError {
  constructor(message: string, code: string = 'VIREO_1000', details: Record<string, any> = {}) {
    super(message, code, details);
    this.name = 'ProtocolError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class StateError extends ProtocolError {
  constructor(
    message: string,
    public currentState?: string,
    public expectedState?: string,
  ) {
    super(message, 'VIREO_1010', { currentState, expectedState });
    this.name = 'StateError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class VersionError extends ProtocolError {
  constructor(
    message: string,
    public expected?: string,
    public actual?: string,
  ) {
    super(message, 'VIREO_1020', { expected, actual });
    this.name = 'VersionError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class NonceError extends ProtocolError {
  constructor(message: string, public nonce?: string) {
    super(message, 'VIREO_1030', { nonce });
    this.name = 'NonceError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class MessageError extends ProtocolError {
  constructor(
    message: string,
    public field?: string,
    public value?: any,
  ) {
    super(message, 'VIREO_1040', { field, value });
    this.name = 'MessageError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class CryptoError extends VireoError {
  constructor(message: string, code: string = 'VIREO_2000', details: Record<string, any> = {}) {
    super(message, code, details);
    this.name = 'CryptoError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class SignatureError extends CryptoError {
  constructor(message: string, public signer?: string) {
    super(message, 'VIREO_2010', { signer });
    this.name = 'SignatureError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class KeyError extends CryptoError {
  constructor(message: string, public keyId?: string) {
    super(message, 'VIREO_2020', { keyId });
    this.name = 'KeyError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class ValidationError extends VireoError {
  constructor(message: string, public path?: string, code: string = 'VIREO_3000') {
    super(message, code, { path });
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class SerializationError extends ValidationError {
  constructor(message: string, path?: string) {
    super(message, path, 'VIREO_3010');
    this.name = 'SerializationError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class IdentityError extends VireoError {
  constructor(message: string, public did?: string) {
    super(message, 'VIREO_4000', { did });
    this.name = 'IdentityError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class TrustError extends IdentityError {
  constructor(message: string, did?: string) {
    super(message, did);
    this.code = 'VIREO_4010';
    this.name = 'TrustError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class SandboxError extends VireoError {
  constructor(message: string, code: string = 'VIREO_5000', details: Record<string, any> = {}) {
    super(message, code, details);
    this.name = 'SandboxError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class ConfigError extends VireoError {
  constructor(message: string, public key?: string) {
    super(message, 'VIREO_6000', { key });
    this.name = 'ConfigError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class NotFoundError extends VireoError {
  constructor(message: string, public resourceType?: string) {
    super(message, 'VIREO_7000', { resourceType });
    this.name = 'NotFoundError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class PermissionError extends VireoError {
  constructor(message: string, public action?: string) {
    super(message, 'VIREO_8000', { action });
    this.name = 'PermissionError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class InternalError extends VireoError {
  constructor(message: string, code: string = 'VIREO_9000') {
    super(message, code);
    this.name = 'InternalError';
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

// Error factory
export function createError(code: string, message: string, details?: Record<string, any>): VireoError {
  const errorClasses: Record<string, new (message: string, code: string, details: Record<string, any>) => VireoError> = {
    'VIREO_0000': VireoError,
    'VIREO_1000': ProtocolError,
    'VIREO_1010': StateError,
    'VIREO_1020': VersionError,
    'VIREO_1030': NonceError,
    'VIREO_1040': MessageError,
    'VIREO_2000': CryptoError,
    'VIREO_2010': SignatureError,
    'VIREO_2020': KeyError,
    'VIREO_3000': ValidationError,
    'VIREO_3010': SerializationError,
    'VIREO_4000': IdentityError,
    'VIREO_4010': TrustError,
    'VIREO_5000': SandboxError,
    'VIREO_6000': ConfigError,
    'VIREO_7000': NotFoundError,
    'VIREO_8000': PermissionError,
    'VIREO_9000': InternalError,
  };

  const ErrorClass = errorClasses[code] || VireoError;
  return new ErrorClass(message, code, details || {});
}