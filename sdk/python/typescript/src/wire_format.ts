/**
 * Vireo TypeScript SDK - Wire Format Serialization
 * 
 * Binary canonical format for Vireo messages
 * 
 * @module wire_format
 */

import { VireoValue, VireoType, MessageEnvelope, MessageHeader, MessageBody } from './types';
import { SerializationError } from './errors';

// ============================================================
// Wire Format Constants
// ============================================================

export const WIRE_MAGIC = 0x56495245; // 'VIRE' in hex
export const WIRE_VERSION = 0x03000000; // v3.0.0
export const WIRE_HEADER_SIZE = 16; // bytes

// ============================================================
// Wire Format Types
// ============================================================

export interface WireHeader {
  magic: number;
  version: number;
  messageType: number;
  flags: number;
  bodyLength: number;
}

// ============================================================
// Wire Format Serializer
// ============================================================

export class WireFormat {
  /**
   * Serialize a message envelope to binary format
   */
  static serialize(envelope: MessageEnvelope): Uint8Array {
    const headerBytes = this.serializeHeader(envelope.header);
    const bodyBytes = envelope.body ? this.serializeBody(envelope.body) : new Uint8Array(0);

    const result = new Uint8Array(headerBytes.length + bodyBytes.length);
    result.set(headerBytes, 0);
    result.set(bodyBytes, headerBytes.length);

    return result;
  }

  /**
   * Deserialize binary data to message envelope
   */
  static deserialize(data: Uint8Array): MessageEnvelope {
    if (data.length < WIRE_HEADER_SIZE) {
      throw new SerializationError('Data too short for wire format');
    }

    const header = this.deserializeHeader(data);
    const bodyStart = WIRE_HEADER_SIZE;
    const bodyEnd = bodyStart + header.bodyLength;

    if (data.length < bodyEnd) {
      throw new SerializationError('Data too short for body');
    }

    const bodyData = data.slice(bodyStart, bodyEnd);
    const body = this.deserializeBody(bodyData, header.messageType);

    return { header, body };
  }

  /**
   * Serialize message header
   */
  static serializeHeader(header: MessageHeader): Uint8Array {
    const view = new DataView(new ArrayBuffer(WIRE_HEADER_SIZE));

    // Magic number (4 bytes)
    view.setUint32(0, WIRE_MAGIC, false);

    // Version (4 bytes)
    view.setUint32(4, WIRE_VERSION, false);

    // Message type (4 bytes)
    const typeMap: Record<string, number> = {
      'propose': 1,
      'commit': 2,
      'execute': 3,
      'verify': 4,
      'escalate': 5,
      'done': 6,
      'failed': 7,
      'timeout': 8,
      'ack': 9,
      'nack': 10,
      'query': 11,
      'response': 12,
      'error': 13,
    };
    view.setUint32(8, typeMap[header.type] || 0, false);

    // Flags (4 bytes)
    let flags = 0;
    if (header.signature) flags |= 0x01;
    if (header.nonce) flags |= 0x02;
    if (header.receiver) flags |= 0x04;
    if (header.correlationId) flags |= 0x08;
    if (header.replyTo) flags |= 0x10;
    view.setUint32(12, flags, false);

    return new Uint8Array(view.buffer);
  }

  /**
   * Deserialize message header
   */
  static deserializeHeader(data: Uint8Array): MessageHeader {
    const view = new DataView(data.buffer, data.byteOffset);

    const magic = view.getUint32(0, false);
    if (magic !== WIRE_MAGIC) {
      throw new SerializationError(`Invalid magic number: ${magic.toString(16)}`);
    }

    const version = view.getUint32(4, false);
    const typeCode = view.getUint32(8, false);
    const flags = view.getUint32(12, false);

    const typeMap: Record<number, string> = {
      1: 'propose',
      2: 'commit',
      3: 'execute',
      4: 'verify',
      5: 'escalate',
      6: 'done',
      7: 'failed',
      8: 'timeout',
      9: 'ack',
      10: 'nack',
      11: 'query',
      12: 'response',
      13: 'error',
    };

    return {
      type: (typeMap[typeCode] || 'error') as any,
      version: `${(version >> 24) & 0xFF}.${(version >> 16) & 0xFF}.${(version >> 8) & 0xFF}`,
      messageId: crypto.randomUUID(),
      timestamp: new Date(),
      sender: '',
      receiver: (flags & 0x04) ? 'placeholder' : undefined,
      correlationId: (flags & 0x08) ? 'placeholder' : undefined,
      replyTo: (flags & 0x10) ? 'placeholder' : undefined,
      nonce: (flags & 0x02) ? 'placeholder' : undefined,
      signature: (flags & 0x01) ? 'placeholder' : undefined,
      ttlSeconds: 300,
      priority: 0,
      flags: [],
    };
  }

  /**
   * Serialize message body
   */
  static serializeBody(body: MessageBody): Uint8Array {
    const json = JSON.stringify({
      contentType: body.contentType,
      data: this.serializeValue(body.data),
      metadata: body.metadata,
      schemaUri: body.schemaUri,
    });
    return new TextEncoder().encode(json);
  }

  /**
   * Deserialize message body
   */
  static deserializeBody(data: Uint8Array, messageType: number): MessageBody | undefined {
    if (data.length === 0) return undefined;

    const json = new TextDecoder().decode(data);
    const parsed = JSON.parse(json);

    return {
      contentType: parsed.contentType || 'application/json',
      data: this.deserializeValue(parsed.data),
      metadata: parsed.metadata || {},
      schemaUri: parsed.schemaUri,
      size: data.length,
    };
  }

  /**
   * Serialize Vireo value
   */
  static serializeValue(value: VireoValue): any {
    if (value === null || value === undefined) {
      return { __type: 'null', value: null };
    }

    switch (value.type) {
      case 'null':
        return null;
      case 'boolean':
        return value.value;
      case 'integer':
        return value.value;
      case 'float':
        return value.value;
      case 'string':
        return value.value;
      case 'binary':
        return { __type: 'binary', value: Buffer.from(value.value).toString('hex') };
      case 'array':
        return value.value.map((v: any) => this.serializeValue(v));
      case 'object':
        const obj: Record<string, any> = {};
        for (const [k, v] of Object.entries(value.value)) {
          obj[k] = this.serializeValue(v);
        }
        return obj;
      case 'timestamp':
        return { __type: 'timestamp', value: value.value.toISOString() };
      case 'did':
        return { __type: 'did', value: value.value };
      case 'signature':
        return { __type: 'signature', value: Buffer.from(value.value).toString('hex') };
      case 'nonce':
        return { __type: 'nonce', value: Buffer.from(value.value).toString('hex') };
      default:
        return value.value;
    }
  }

  /**
   * Deserialize Vireo value
   */
  static deserializeValue(data: any): VireoValue {
    if (data === null || data === undefined) {
      return { type: 'null', value: null };
    }

    if (typeof data === 'boolean') {
      return { type: 'boolean', value: data };
    }

    if (typeof data === 'number') {
      if (Number.isInteger(data)) {
        return { type: 'integer', value: data };
      }
      return { type: 'float', value: data };
    }

    if (typeof data === 'string') {
      return { type: 'string', value: data };
    }

    if (Array.isArray(data)) {
      return { type: 'array', value: data.map((v) => this.deserializeValue(v)) };
    }

    if (typeof data === 'object' && data !== null) {
      if (data.__type) {
        switch (data.__type) {
          case 'binary':
            return { type: 'binary', value: Buffer.from(data.value, 'hex') };
          case 'timestamp':
            return { type: 'timestamp', value: new Date(data.value) };
          case 'did':
            return { type: 'did', value: data.value };
          case 'signature':
            return { type: 'signature', value: Buffer.from(data.value, 'hex') };
          case 'nonce':
            return { type: 'nonce', value: Buffer.from(data.value, 'hex') };
        }
      }

      const obj: Record<string, VireoValue> = {};
      for (const [k, v] of Object.entries(data)) {
        obj[k] = this.deserializeValue(v);
      }
      return { type: 'object', value: obj };
    }

    return { type: 'null', value: null };
  }

  /**
   * Check if data is valid wire format
   */
  static isValid(data: Uint8Array): boolean {
    try {
      if (data.length < WIRE_HEADER_SIZE) return false;
      const view = new DataView(data.buffer, data.byteOffset);
      const magic = view.getUint32(0, false);
      return magic === WIRE_MAGIC;
    } catch {
      return false;
    }
  }
}