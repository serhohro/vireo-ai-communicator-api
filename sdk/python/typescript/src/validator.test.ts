/**
 * Vireo TypeScript SDK - Validator Tests
 * 
 * @module validator.test
 */

import { VireoAgent } from './agent';
import { Validator } from './validator';
import { MessageEnvelope } from './types';

describe('Validator', () => {
  let validator: Validator;

  beforeEach(() => {
    validator = Validator.default();
  });

  test('should validate valid message', () => {
    const agent = new VireoAgent('test-agent');
    const envelope: MessageEnvelope = {
      header: {
        type: 'propose',
        version: '3.0.0',
        messageId: 'test-123',
        timestamp: new Date(),
        sender: agent.info.agentId,
        ttlSeconds: 300,
        priority: 0,
        flags: [],
      },
      body: {
        contentType: 'application/json',
        data: { type: 'object', value: { task: 'test' } },
        metadata: {},
        size: 0,
      },
    };

    const result = validator.validate(envelope);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('should reject invalid message type', () => {
    const envelope: MessageEnvelope = {
      header: {
        type: 'invalid' as any,
        version: '3.0.0',
        messageId: 'test-123',
        timestamp: new Date(),
        sender: 'test-agent',
        ttlSeconds: 300,
        priority: 0,
        flags: [],
      },
    };

    const result = validator.validate(envelope);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.includes('Invalid message type'))).toBe(true);
  });

  test('should reject expired message', () => {
    const oldDate = new Date();
    oldDate.setMinutes(oldDate.getMinutes() - 10);

    const envelope: MessageEnvelope = {
      header: {
        type: 'propose',
        version: '3.0.0',
        messageId: 'test-123',
        timestamp: oldDate,
        sender: 'test-agent',
        ttlSeconds: 60,
        priority: 0,
        flags: [],
      },
    };

    const result = validator.validate(envelope);
    expect(result.valid).toBe(false);
    expect(result.errors.some(e => e.includes('expired'))).toBe(true);
  });
});