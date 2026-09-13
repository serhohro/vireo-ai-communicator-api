import * as fs from 'fs';
import * as path from 'path';
import { WireFormat, INTENT_CODES } from '../src/wire_format';
import { blake2b256, didHash, toHex } from '../src/crypto';
import type { MessageEnvelope } from '../src/types';

const VECTOR_PATH = path.resolve(
  __dirname,
  '../../../tests/conformance/vectors/001_propose_commit.json'
);

const vector = JSON.parse(fs.readFileSync(VECTOR_PATH, 'utf8'));

function buildEnvelope(v: any): MessageEnvelope {
  return {
    header: {
      type: v.input_fields.intent.toLowerCase(),
      intent: v.input_fields.intent,
      version: '3.1.0',
      messageId: 'conformance-001',
      timestamp: new Date(v.input_fields.timestamp_ms),
      timestampMs: v.input_fields.timestamp_ms,
      sender: v.input_fields.sender_did,
      receiver: v.input_fields.recipient_did,
      nonce: v.input_fields.nonce_hex,
      ttlSeconds: 300,
      priority: 0,
      flags: [],
    },
    body: {
      contentType: 'application/json',
      data: {
        type: 'object',
        value: v.input_fields.payload,
      },
      metadata: {},
      size: 0,
    },
  };
}

describe('Cross-language conformance — 001_propose_commit', () => {
  test('intent code is PROPOSE=2', () => {
    expect(INTENT_CODES.PROPOSE).toBe(2);
  });

  test('sender DID hash matches vector', () => {
    const hash = didHash(vector.input_fields.sender_did);
    const expected = vector.expected_outputs.canonical_bytes_hex.slice(64, 128);
    expect(toHex(hash)).toBe(expected);
  });

  test('recipient DID hash matches vector', () => {
    const hash = didHash(vector.input_fields.recipient_did);
    const expected = vector.expected_outputs.canonical_bytes_hex.slice(128, 192);
    expect(toHex(hash)).toBe(expected);
  });

  test('canonical bytes length is 226', () => {
    const bytes = WireFormat.serialize(buildEnvelope(vector));
    expect(bytes.length).toBe(226);
    expect(bytes.length).toBe(vector.expected_outputs.canonical_bytes_len);
  });

  test('canonical bytes match vector', () => {
    const bytes = WireFormat.serialize(buildEnvelope(vector));
    expect(toHex(bytes)).toBe(vector.expected_outputs.canonical_bytes_hex);
  });

  test('wire hash matches vector', () => {
    const bytes = WireFormat.serialize(buildEnvelope(vector));
    expect(toHex(blake2b256(bytes))).toBe(vector.expected_outputs.wire_hash_hex);
  });

  test('wire hash is 011c2182...', () => {
    const bytes = WireFormat.serialize(buildEnvelope(vector));
    expect(toHex(blake2b256(bytes))).toBe(
      '011c2182af8206779ae3bc4ff145467a49ae0a2389ee54f940da9de24e7255db'
    );
  });
});
