/**
 * Vireo TypeScript SDK - Message Validator
 * 
 * @module validator
 */

import { MessageEnvelope, MessageHeader, MessageBody } from './types';
import { ValidationError, MessageError } from './errors';
import { WireFormat } from './wire_format';

// ============================================================
// Validation Result
// ============================================================

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export function createSuccessResult(): ValidationResult {
  return { valid: true, errors: [] };
}

export function createErrorResult(error: string): ValidationResult {
  return { valid: false, errors: [error] };
}

export function mergeResults(...results: ValidationResult[]): ValidationResult {
  const merged: ValidationResult = { valid: true, errors: [] };
  for (const result of results) {
    if (!result.valid) {
      merged.valid = false;
      merged.errors.push(...result.errors);
    }
  }
  return merged;
}

// ============================================================
// Validation Rules
// ============================================================

export interface ValidationRule {
  name: string;
  validate(message: MessageEnvelope): ValidationResult;
}

export class MessageTypeRule implements ValidationRule {
  public name = 'MessageTypeRule';
  private allowedTypes: string[];

  constructor(allowedTypes: string[]) {
    this.allowedTypes = allowedTypes;
  }

  validate(message: MessageEnvelope): ValidationResult {
    if (!this.allowedTypes.includes(message.header.type)) {
      return createErrorResult(
        `Invalid message type: ${message.header.type}. Allowed: ${this.allowedTypes.join(', ')}`
      );
    }
    return createSuccessResult();
  }
}

export class VersionRule implements ValidationRule {
  public name = 'VersionRule';
  private minVersion: string;
  private maxVersion?: string;

  constructor(minVersion: string, maxVersion?: string) {
    this.minVersion = minVersion;
    this.maxVersion = maxVersion;
  }

  validate(message: MessageEnvelope): ValidationResult {
    const version = message.header.version;
    if (!this.versionGte(version, this.minVersion)) {
      return createErrorResult(`Version ${version} is less than minimum ${this.minVersion}`);
    }
    if (this.maxVersion && !this.versionLte(version, this.maxVersion)) {
      return createErrorResult(`Version ${version} is greater than maximum ${this.maxVersion}`);
    }
    return createSuccessResult();
  }

  private versionParse(v: string): number[] {
    return v.replace(/[^0-9.]/g, '').split('.').map(Number);
  }

  private versionGte(v1: string, v2: string): boolean {
    const p1 = this.versionParse(v1);
    const p2 = this.versionParse(v2);
    for (let i = 0; i < Math.max(p1.length, p2.length); i++) {
      const n1 = i < p1.length ? p1[i] : 0;
      const n2 = i < p2.length ? p2[i] : 0;
      if (n1 < n2) return false;
      if (n1 > n2) return true;
    }
    return true;
  }

  private versionLte(v1: string, v2: string): boolean {
    return this.versionGte(v2, v1);
  }
}

export class TTLRule implements ValidationRule {
  public name = 'TTLRule';

  validate(message: MessageEnvelope): ValidationResult {
    const age = (Date.now() - message.header.timestamp.getTime()) / 1000;
    if (age > message.header.ttlSeconds) {
      return createErrorResult(
        `Message expired (TTL: ${message.header.ttlSeconds}s, age: ${age.toFixed(1)}s)`
      );
    }
    return createSuccessResult();
  }
}

// ============================================================
// Main Validator
// ============================================================

export class Validator {
  private rules: ValidationRule[] = [];

  constructor() {
    // Add default rules
    this.rules.push(
      new MessageTypeRule([
        'propose',
        'commit',
        'execute',
        'verify',
        'escalate',
        'done',
        'failed',
        'ack',
        'nack',
        'query',
        'response',
        'error',
      ]),
      new VersionRule('3.0.0', '3.0.9'),
      new TTLRule(),
    );
  }

  /**
   * Add a validation rule
   */
  addRule(rule: ValidationRule): void {
    this.rules.push(rule);
  }

  /**
   * Remove a validation rule by name
   */
  removeRule(name: string): void {
    this.rules = this.rules.filter((rule) => rule.name !== name);
  }

  /**
   * Validate a message envelope
   */
  validate(message: MessageEnvelope): ValidationResult {
    let result = createSuccessResult();
    for (const rule of this.rules) {
      try {
        const ruleResult = rule.validate(message);
        if (!ruleResult.valid) {
          result = mergeResults(result, ruleResult);
        }
      } catch (error) {
        result = mergeResults(result, createErrorResult(`Rule "${rule.name}" error: ${error}`));
      }
    }
    return result;
  }

  /**
   * Validate raw wire data
   */
  validateWire(data: Uint8Array): ValidationResult {
    try {
      if (!WireFormat.isValid(data)) {
        return createErrorResult('Invalid wire format (magic number mismatch)');
      }
      const envelope = WireFormat.deserialize(data);
      return this.validate(envelope);
    } catch (error) {
      return createErrorResult(`Wire format error: ${error}`);
    }
  }

  /**
   * Validate a message header
   */
  validateHeader(header: MessageHeader): ValidationResult {
    const envelope: MessageEnvelope = {
      header,
      body: {
        contentType: 'application/json',
        data: { type: 'null', value: null },
        metadata: {},
        size: 0,
      },
    };
    return this.validate(envelope);
  }

  /**
   * Validate a message body against schema
   */
  validateBody(body: MessageBody, schema: Record<string, any>): ValidationResult {
    try {
      return this.validateSchema(body.data, schema);
    } catch (error) {
      return createErrorResult(`Schema validation error: ${error}`);
    }
  }

  /**
   * Validate a value against JSON schema
   */
  private validateSchema(value: any, schema: Record<string, any>): ValidationResult {
    // Simple schema validation
    const schemaType = schema.type;

    if (schemaType === 'object') {
      if (typeof value !== 'object' || value === null || Array.isArray(value)) {
        return createErrorResult('Expected object');
      }
      const required = schema.required || [];
      for (const prop of required) {
        if (!(prop in value)) {
          return createErrorResult(`Missing required property: ${prop}`);
        }
      }
      const properties = schema.properties || {};
      for (const [prop, propSchema] of Object.entries(properties)) {
        if (prop in value) {
          const result = this.validateSchema(value[prop], propSchema);
          if (!result.valid) return result;
        }
      }
      return createSuccessResult();
    }

    if (schemaType === 'array') {
      if (!Array.isArray(value)) {
        return createErrorResult('Expected array');
      }
      const itemsSchema = schema.items;
      if (itemsSchema) {
        for (const item of value) {
          const result = this.validateSchema(item, itemsSchema);
          if (!result.valid) return result;
        }
      }
      return createSuccessResult();
    }

    if (schemaType === 'string') {
      if (typeof value !== 'string') {
        return createErrorResult('Expected string');
      }
      const minLength = schema.minLength;
      const maxLength = schema.maxLength;
      if (minLength !== undefined && value.length < minLength) {
        return createErrorResult(`String too short: ${value.length} < ${minLength}`);
      }
      if (maxLength !== undefined && value.length > maxLength) {
        return createErrorResult(`String too long: ${value.length} > ${maxLength}`);
      }
      if (schema.pattern) {
        const regex = new RegExp(schema.pattern);
        if (!regex.test(value)) {
          return createErrorResult(`String doesn't match pattern: ${schema.pattern}`);
        }
      }
      return createSuccessResult();
    }

    if (schemaType === 'integer') {
      if (typeof value !== 'number' || !Number.isInteger(value)) {
        return createErrorResult('Expected integer');
      }
      if (schema.minimum !== undefined && value < schema.minimum) {
        return createErrorResult(`Value ${value} < ${schema.minimum}`);
      }
      if (schema.maximum !== undefined && value > schema.maximum) {
        return createErrorResult(`Value ${value} > ${schema.maximum}`);
      }
      return createSuccessResult();
    }

    if (schemaType === 'number') {
      if (typeof value !== 'number') {
        return createErrorResult('Expected number');
      }
      return createSuccessResult();
    }

    if (schemaType === 'boolean') {
      if (typeof value !== 'boolean') {
        return createErrorResult('Expected boolean');
      }
      return createSuccessResult();
    }

    return createSuccessResult();
  }

  /**
   * Static validator instance with default rules
   */
  static default(): Validator {
    return new Validator();
  }
}