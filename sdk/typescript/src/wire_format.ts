import canonicalize from 'canonicalize';
import { didHash } from './crypto';
import { SerializationError } from './errors';
import type { MessageEnvelope } from './types';

export const WIRE_MAGIC = 0x56495245;
export const WIRE_VERSION = 0x0301;
export const HEADER_SIZE = 96;
export const LENGTH_SIZE = 4;

export const INTENT_CODES: Record<string, number> = {
  DISCOVER: 1,
  PROPOSE: 2,
  NEGOTIATE: 3,
  COMMIT: 4,
  REJECT: 5,
  EXECUTE: 6,
  VERIFY: 7,
  DONE: 8,
  ESCALATED: 9,
  CANCELLED: 10,
  FAILED: 11,
  TIMEOUT: 12,
};

export const INTENT_NAMES: Record<number, string> = Object.fromEntries(
  Object.entries(INTENT_CODES).map(([k, v]) => [v, k])
);

export class WireFormat {
  static serialize(envelope: MessageEnvelope): Uint8Array {
    const header = envelope.header;
    const body = envelope.body;

    if (!body) {
      throw new SerializationError('Envelope body is required');
    }

    const intentName = (header.intent || header.type || '').toUpperCase();
    const intentCode = INTENT_CODES[intentName];
    if (intentCode === undefined) {
      throw new SerializationError(`Unknown intent: ${intentName}`);
    }

    const senderDid = header.sender;
    const recipientDid = header.receiver;
    if (!senderDid || !recipientDid) {
      throw new SerializationError('sender and receiver DIDs are required');
    }

    const senderHash = didHash(senderDid);
    const recipientHash = didHash(recipientDid);

    const nonce = normalizeNonce(header.nonce);
    const timestampMs = header.timestampMs ?? Date.now();

    const payloadValue = body.data?.value ?? body.data;
    const payloadJson = canonicalize(payloadValue);
    if (payloadJson === undefined) {
      throw new SerializationError('Payload is not canonicalizable');
    }
    const payloadBytes = new TextEncoder().encode(payloadJson);

    const total = HEADER_SIZE + LENGTH_SIZE + payloadBytes.length;
    const buf = new Uint8Array(total);
    const view = new DataView(buf.buffer);

    view.setUint32(0, WIRE_MAGIC, false);
    view.setUint16(4, WIRE_VERSION, false);
    view.setUint16(6, intentCode, false);
    view.setBigUint64(8, BigInt(timestampMs), false);
    buf.set(nonce, 16);
    buf.set(senderHash, 32);
    buf.set(recipientHash, 64);
    view.setUint32(96, payloadBytes.length, false);
    buf.set(payloadBytes, 100);

    return buf;
  }

  static deserialize(data: Uint8Array): MessageEnvelope {
    if (data.length < HEADER_SIZE + LENGTH_SIZE) {
      throw new SerializationError('Data too short for wire format');
    }

    const view = new DataView(data.buffer, data.byteOffset, data.byteLength);

    const magic = view.getUint32(0, false);
    if (magic !== WIRE_MAGIC) {
      throw new SerializationError(`Invalid magic: 0x${magic.toString(16)}`);
    }

    const version = view.getUint16(4, false);
    const intentCode = view.getUint16(6, false);
    const timestampMs = Number(view.getBigUint64(8, false));
    const nonce = data.slice(16, 32);
    const payloadLength = view.getUint32(96, false);

    if (data.length < HEADER_SIZE + LENGTH_SIZE + payloadLength) {
      throw new SerializationError('Data too short for payload');
    }

    const payloadBytes = data.slice(100, 100 + payloadLength);
    const payloadJson = new TextDecoder().decode(payloadBytes);
    const payload = JSON.parse(payloadJson);

    const intentName = INTENT_NAMES[intentCode] || 'UNKNOWN';

    return {
      header: {
        type: intentName.toLowerCase() as any,
        intent: intentName,
        intentCode,
        version: `${(version >> 8) & 0xff}.${version & 0xff}.0`,
        messageId: '',
        timestamp: new Date(timestampMs),
        timestampMs,
        sender: '',
        receiver: '',
        senderDidHash: data.slice(32, 64),
        recipientDidHash: data.slice(64, 96),
        nonce,
        ttlSeconds: 0,
        priority: 0,
        flags: [],
      },
      body: {
        contentType: 'application/json',
        data: { type: 'object', value: payload },
        metadata: {},
        size: payloadLength,
      },
    };
  }

  static isValid(data: Uint8Array): boolean {
    if (data.length < 4) return false;
    try {
      const view = new DataView(data.buffer, data.byteOffset, data.byteLength);
      return view.getUint32(0, false) === WIRE_MAGIC;
    } catch {
      return false;
    }
  }
}

function normalizeNonce(nonce: Uint8Array | string | undefined): Uint8Array {
  if (!nonce) return new Uint8Array(16);
  if (typeof nonce === 'string') {
    const buf = Buffer.from(nonce, 'hex');
    if (buf.length !== 16) {
      throw new SerializationError(`Nonce must be 16 bytes, got ${buf.length}`);
    }
    return new Uint8Array(buf);
  }
  if (nonce.length !== 16) {
    throw new SerializationError(`Nonce must be 16 bytes, got ${nonce.length}`);
  }
  return nonce;
}
