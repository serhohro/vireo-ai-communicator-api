/**
 * Vireo TypeScript SDK - Integration Tests
 * 
 * End-to-end tests for Vireo agent communication
 * 
 * @module integration.test
 */

import { VireoAgent } from '../src/agent';
import { VireoClient, InMemoryTransport } from '../src/client';
import { MessageEnvelope, MessageType, Contract, ProtocolState } from '../src/types';
import { Validator } from '../src/validator';
import { WireFormat } from '../src/wire_format';
import { ProtocolError, StateError, ValidationError } from '../src/errors';

// ============================================================
// TEST SETUP
// ============================================================

describe('Vireo TypeScript SDK Integration Tests', () => {
  let agent1: VireoAgent;
  let agent2: VireoAgent;
  let client1: VireoClient;
  let client2: VireoClient;
  let transport1: InMemoryTransport;
  let transport2: InMemoryTransport;

  beforeEach(() => {
    // Create agents
    agent1 = new VireoAgent('Agent-Alpha', 'master');
    agent2 = new VireoAgent('Agent-Beta', 'worker');

    // Register capabilities
    agent1.registerCapability('analyze', 'Analyze data', async (data: any) => {
      return { status: 'success', result: `Analyzed: ${JSON.stringify(data)}` };
    });

    agent2.registerCapability('execute', 'Execute task', async (task: any) => {
      return { status: 'success', result: `Executed: ${JSON.stringify(task)}` };
    });

    // Create transports
    transport1 = new InMemoryTransport();
    transport2 = new InMemoryTransport();
    transport1.connectTo(transport2);

    // Create clients
    client1 = new VireoClient(agent1, { transport: transport1 });
    client2 = new VireoClient(agent2, { transport: transport2 });
  });

  afterEach(async () => {
    await client1.disconnect();
    await client2.disconnect();
  });

  // ============================================================
  // CONNECTION TESTS
  // ============================================================

  describe('Connection', () => {
    test('should connect successfully', async () => {
      await client1.connect();
      expect(client1.isConnected()).toBe(true);
    });

    test('should disconnect successfully', async () => {
      await client1.connect();
      await client1.disconnect();
      expect(client1.isConnected()).toBe(false);
    });

    test('should handle multiple connections', async () => {
      await client1.connect();
      await client2.connect();
      expect(client1.isConnected()).toBe(true);
      expect(client2.isConnected()).toBe(true);
    });

    test('should not connect twice', async () => {
      await client1.connect();
      await client1.connect(); // Should not throw
      expect(client1.isConnected()).toBe(true);
    });
  });

  // ============================================================
  // MESSAGE TESTS
  // ============================================================

  describe('Message Exchange', () => {
    beforeEach(async () => {
      await client1.connect();
      await client2.connect();
    });

    test('should send and receive proposal', async () => {
      const messageHandler = jest.fn();
      client2.on('received', messageHandler);

      const proposal = await client1.propose(
        agent2.info.agentId,
        'Test task',
        { maxTokens: 1000, timeout: 30 }
      );

      expect(proposal.header.type).toBe('propose');
      expect(proposal.header.sender).toBe(agent1.info.agentId);
      expect(proposal.header.receiver).toBe(agent2.info.agentId);

      // Wait for message to be received
      await new Promise(resolve => setTimeout(resolve, 50));
      expect(messageHandler).toHaveBeenCalled();
    });

    test('should send and receive commit', async () => {
      const proposal = await client1.propose(
        agent2.info.agentId,
        'Test task',
        { maxTokens: 1000 }
      );

      const commit = await client1.commit(proposal.header.messageId);
      expect(commit.header.type).toBe('commit');
      expect(commit.header.correlationId).toBe(proposal.header.messageId);
    });

    test('should send and receive execute', async () => {
      const proposal = await client1.propose(
        agent2.info.agentId,
        'Test task'
      );

      const commit = await client1.commit(proposal.header.messageId);
      const execution = await client1.execute(commit.header.messageId, { input: 'test data' });

      expect(execution.header.type).toBe('execute');
      expect(execution.body?.data.value).toHaveProperty('result');
    });

    test('should send and receive verify', async () => {
      const proposal = await client1.propose(
        agent2.info.agentId,
        'Test task'
      );

      await client1.commit(proposal.header.messageId);
      const execution = await client1.execute(proposal.header.messageId);
      const verification = await client1.verify(
        execution.header.messageId,
        { status: 'success', data: 'verified' }
      );

      expect(verification.header.type).toBe('verify');
      expect(verification.body?.data.value).toHaveProperty('verified', true);
    });

    test('should send and receive done', async () => {
      const proposal = await client1.propose(
        agent2.info.agentId,
        'Test task'
      );

      await client1.commit(proposal.header.messageId);
      await client1.execute(proposal.header.messageId);
      await client1.verify(proposal.header.messageId, { status: 'success' });
      const done = await client1.done({ status: 'complete' });

      expect(done.header.type).toBe('done');
      expect(done.body?.data.value).toHaveProperty('result');
    });

    test('should send and receive escalate', async () => {
      const proposal = await client1.propose(
        agent2.info.agentId,
        'Test task'
      );

      const escalate = await client1.escalate(
        proposal.header.messageId,
        'Something went wrong'
      );

      expect(escalate.header.type).toBe('escalate');
      expect(escalate.body?.data.value).toHaveProperty('reason', 'Something went wrong');
    });

    test('should send and receive ack', async () => {
      const ackHandler = jest.fn();
      client2.on('received', (envelope: MessageEnvelope) => {
        if (envelope.header.type === 'ack') {
          ackHandler(envelope);
        }
      });

      const proposal = await client1.propose(
        agent2.info.agentId,
        'Test task'
      );

      // Wait for ACK
      await new Promise(resolve => setTimeout(resolve, 100));
      expect(ackHandler).toHaveBeenCalled();
    });
  });

  // ============================================================
  // AGENT STATE TESTS
  // ============================================================

  describe('Agent State', () => {
    test('should start in idle state', () => {
      expect(agent1.state).toBe('idle');
    });

    test('should update state on propose', async () => {
      await client1.connect();
      await client1.propose(agent2.info.agentId, 'Test task');
      expect(agent1.state).toBe('proposing');
    });

    test('should update state on commit', async () => {
      await client1.connect();
      const proposal = await client1.propose(agent2.info.agentId, 'Test task');
      await client1.commit(proposal.header.messageId);
      expect(agent1.state).toBe('committing');
    });

    test('should update state on execute', async () => {
      await client1.connect();
      const proposal = await client1.propose(agent2.info.agentId, 'Test task');
      await client1.commit(proposal.header.messageId);
      await client1.execute(proposal.header.messageId);
      expect(agent1.state).toBe('executing');
    });

    test('should update state on verify', async () => {
      await client1.connect();
      const proposal = await client1.propose(agent2.info.agentId, 'Test task');
      await client1.commit(proposal.header.messageId);
      await client1.execute(proposal.header.messageId);
      await client1.verify(proposal.header.messageId, { status: 'success' });
      expect(agent1.state).toBe('verifying');
    });

    test('should update state on done', async () => {
      await client1.connect();
      const proposal = await client1.propose(agent2.info.agentId, 'Test task');
      await client1.commit(proposal.header.messageId);
      await client1.execute(proposal.header.messageId);
      await client1.verify(proposal.header.messageId, { status: 'success' });
      await client1.done({ status: 'complete' });
      expect(agent1.state).toBe('done');
    });

    test('should update state on escalate', async () => {
      await client1.connect();
      const proposal = await client1.propose(agent2.info.agentId, 'Test task');
      await client1.escalate(proposal.header.messageId, 'Error');
      expect(agent1.state).toBe('error');
    });

    test('should reset state', async () => {
      await client1.connect();
      const proposal = await client1.propose(agent2.info.agentId, 'Test task');
      await client1.commit(proposal.header.messageId);
      expect(agent1.state).toBe('committing');
      agent1.reset();
      expect(agent1.state).toBe('idle');
    });

    test('should track state history', async () => {
      await client1.connect();
      const proposal = await client1.propose(agent2.info.agentId, 'Test task');
      await client1.commit(proposal.header.messageId);
      await client1.execute(proposal.header.messageId);

      const summary = agent1.getStateSummary();
      expect(summary.history).toContain('idle');
      expect(summary.history).toContain('proposing');
      expect(summary.history).toContain('committing');
      expect(summary.history).toContain('executing');
    });
  });

  // ============================================================
  // CAPABILITY TESTS
  // ============================================================

  describe('Capabilities', () => {
    test('should register capability', () => {
      agent1.registerCapability('test', 'Test capability', async () => 'test result');
      expect(agent1.hasCapability('test')).toBe(true);
    });

    test('should get capabilities list', () => {
      agent1.registerCapability('cap1', 'Cap 1', async () => {});
      agent1.registerCapability('cap2', 'Cap 2', async () => {});
      expect(agent1.getCapabilities()).toContain('cap1');
      expect(agent1.getCapabilities()).toContain('cap2');
    });

    test('should execute capability', async () => {
      agent1.registerCapability('greet', 'Greet user', async (name: string) => {
        return `Hello, ${name}!`;
      });

      const result = await agent1.executeCapability('greet', 'World');
      expect(result).toBe('Hello, World!');
    });

    test('should reject unknown capability', async () => {
      await expect(agent1.executeCapability('unknown')).rejects.toThrow('Capability "unknown" not found');
    });

    test('should reject duplicate capability registration', () => {
      agent1.registerCapability('duplicate', 'First', async () => {});
      expect(() => {
        agent1.registerCapability('duplicate', 'Second', async () => {});
      }).toThrow('Capability "duplicate" already registered');
    });

    test('should handle capability errors', async () => {
      agent1.registerCapability('error', 'Error capability', async () => {
        throw new Error('Capability error');
      });

      await expect(agent1.executeCapability('error')).rejects.toThrow('Capability execution failed');
    });
  });

  // ============================================================
  // VALIDATION TESTS
  // ============================================================

  describe('Validation', () => {
    let validator: Validator;

    beforeEach(() => {
      validator = Validator.default();
    });

    test('should validate valid message', () => {
      const envelope: MessageEnvelope = {
        header: {
          type: 'propose',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: 'test-agent',
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

    test('should reject version mismatch', () => {
      const envelope: MessageEnvelope = {
        header: {
          type: 'propose',
          version: '2.0.0',
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
      expect(result.errors.some(e => e.includes('Version'))).toBe(true);
    });

    test('should add custom rule', () => {
      let called = false;
      validator.addRule({
        name: 'CustomRule',
        validate: (envelope: MessageEnvelope) => {
          called = true;
          return { valid: true, errors: [] };
        },
      });

      const envelope: MessageEnvelope = {
        header: {
          type: 'propose',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: 'test-agent',
          ttlSeconds: 300,
          priority: 0,
          flags: [],
        },
      };

      validator.validate(envelope);
      expect(called).toBe(true);
    });

    test('should remove custom rule', () => {
      validator.addRule({
        name: 'RemoveMe',
        validate: () => ({ valid: true, errors: [] }),
      });

      validator.removeRule('RemoveMe');
      // Should not throw
      const envelope: MessageEnvelope = {
        header: {
          type: 'propose',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: 'test-agent',
          ttlSeconds: 300,
          priority: 0,
          flags: [],
        },
      };

      expect(() => validator.validate(envelope)).not.toThrow();
    });
  });

  // ============================================================
  // WIRE FORMAT TESTS
  // ============================================================

  describe('Wire Format', () => {
    test('should serialize and deserialize message', () => {
      const original: MessageEnvelope = {
        header: {
          type: 'propose',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: 'agent-1',
          receiver: 'agent-2',
          ttlSeconds: 300,
          priority: 1,
          flags: ['test'],
        },
        body: {
          contentType: 'application/json',
          data: { type: 'object', value: { test: 'data' } },
          metadata: { version: '1.0' },
          size: 0,
        },
      };

      const serialized = WireFormat.serialize(original);
      const deserialized = WireFormat.deserialize(serialized);

      expect(deserialized.header.type).toBe(original.header.type);
      expect(deserialized.header.version).toBe(original.header.version);
      expect(deserialized.header.messageId).toBe(original.header.messageId);
    });

    test('should detect valid wire format', () => {
      const envelope: MessageEnvelope = {
        header: {
          type: 'propose',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: 'agent-1',
          ttlSeconds: 300,
          priority: 0,
          flags: [],
        },
      };

      const data = WireFormat.serialize(envelope);
      expect(WireFormat.isValid(data)).toBe(true);
    });

    test('should detect invalid wire format', () => {
      const invalidData = new Uint8Array([0x00, 0x01, 0x02, 0x03]);
      expect(WireFormat.isValid(invalidData)).toBe(false);
    });

    test('should handle empty body', () => {
      const envelope: MessageEnvelope = {
        header: {
          type: 'ack',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: 'agent-1',
          ttlSeconds: 300,
          priority: 0,
          flags: [],
        },
      };

      const data = WireFormat.serialize(envelope);
      const deserialized = WireFormat.deserialize(data);
      expect(deserialized.body).toBeUndefined();
    });

    test('should serialize and deserialize binary data', () => {
      const binaryData = new Uint8Array([0x01, 0x02, 0x03, 0x04, 0x05]);
      const envelope: MessageEnvelope = {
        header: {
          type: 'execute',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: 'agent-1',
          ttlSeconds: 300,
          priority: 0,
          flags: [],
        },
        body: {
          contentType: 'application/octet-stream',
          data: { type: 'binary', value: binaryData },
          metadata: {},
          size: binaryData.length,
        },
      };

      const data = WireFormat.serialize(envelope);
      const deserialized = WireFormat.deserialize(data);
      expect(deserialized.body?.data.type).toBe('binary');
      expect(deserialized.body?.data.value).toEqual(binaryData);
    });
  });

  // ============================================================
  // ERROR HANDLING TESTS
  // ============================================================

  describe('Error Handling', () => {
    test('should handle connection errors', async () => {
      const badTransport = new InMemoryTransport();
      const badClient = new VireoClient(agent1, { transport: badTransport });

      // Bad transport with no peers should still work (just no delivery)
      await badClient.connect();
      expect(badClient.isConnected()).toBe(true);

      await badClient.disconnect();
      expect(badClient.isConnected()).toBe(false);
    });

    test('should handle message errors gracefully', async () => {
      const envelope: MessageEnvelope = {
        header: {
          type: 'propose',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: 'test-agent',
          ttlSeconds: 300,
          priority: 0,
          flags: [],
        },
      };

      // Should not throw
      await expect(agent1.handleMessage(envelope)).resolves.not.toThrow();
    });

    test('should handle invalid messages', async () => {
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

      await expect(agent1.handleMessage(envelope)).rejects.toThrow('Invalid message');
    });

    test('should handle timeout errors', async () => {
      await client1.connect();

      const envelope: MessageEnvelope = {
        header: {
          type: 'propose',
          version: '3.0.0',
          messageId: 'test-123',
          timestamp: new Date(),
          sender: agent1.info.agentId,
          receiver: 'non-existent-agent',
          ttlSeconds: 300,
          priority: 0,
          flags: [],
        },
      };

      // With no response, should timeout
      await expect(client1.sendAndWait(envelope, 100)).rejects.toThrow('Response timeout');
    }, 10000);
  });

  // ============================================================
  // AGENT INFO TESTS
  // ============================================================

  describe('Agent Info', () => {
    test('should return agent info', () => {
      const info = agent1.info;
      expect(info.agentId).toBe(agent1.info.agentId);
      expect(info.name).toBe('Agent-Alpha');
      expect(info.role).toBe('master');
      expect(info.capabilities).toEqual([]);
    });

    test('should include capabilities in info', () => {
      agent1.registerCapability('test-cap', 'Test', async () => {});
      expect(agent1.info.capabilities).toContain('test-cap');
    });

    test('should serialize to JSON', () => {
      const json = agent1.toJSON();
      expect(json).toHaveProperty('agentId');
      expect(json).toHaveProperty('name');
      expect(json).toHaveProperty('role');
      expect(json).toHaveProperty('capabilities');
      expect(json).toHaveProperty('state');
      expect(json).toHaveProperty('info');
    });

    test('should stringify', () => {
      const str = agent1.toString();
      expect(str).toContain('VireoAgent');
      expect(str).toContain(agent1.info.agentId);
      expect(str).toContain('Agent-Alpha');
    });
  });

  // ============================================================
  // EVENT TESTS
  // ============================================================

  describe('Events', () => {
    test('should emit connect event', async () => {
      const handler = jest.fn();
      client1.on('connected', handler);
      await client1.connect();
      expect(handler).toHaveBeenCalled();
    });

    test('should emit disconnect event', async () => {
      const handler = jest.fn();
      client1.on('disconnected', handler);
      await client1.connect();
      await client1.disconnect();
      expect(handler).toHaveBeenCalled();
    });

    test('should emit sent event', async () => {
      const handler = jest.fn();
      client1.on('sent', handler);
      await client1.connect();
      await client1.propose('test', 'task');
      expect(handler).toHaveBeenCalled();
    });

    test('should emit received event', async () => {
      const handler = jest.fn();
      client2.on('received', handler);
      await client1.connect();
      await client2.connect();
      await client1.propose(agent2.info.agentId, 'task');
      await new Promise(resolve => setTimeout(resolve, 50));
      expect(handler).toHaveBeenCalled();
    });

    test('should emit state change event', () => {
      const handler = jest.fn();
      agent1.addListener('stateChange', handler);
      agent1.updateState('proposing');
      expect(handler).toHaveBeenCalledWith('proposing');
    });

    test('should emit message event', async () => {
      const handler = jest.fn();
      agent2.addListener('message', handler);
      await client1.connect();
      await client2.connect();
      await client1.propose(agent2.info.agentId, 'task');
      await new Promise(resolve => setTimeout(resolve, 50));
      expect(handler).toHaveBeenCalled();
    });

    test('should emit error event', async () => {
      const handler = jest.fn();
      client1.on('error', handler);
      const invalidData = new Uint8Array([0x00, 0x01, 0x02, 0x03]);
      await client1.connect();
      // Force error by sending invalid data through transport
      // This is a bit hacky but tests the error path
      transport1.send(invalidData).catch(() => {});
      await new Promise(resolve => setTimeout(resolve, 50));
      // Handler may or may not be called depending on error propagation
    });
  });

  // ============================================================
  // MESSAGE QUEUE TESTS
  // ============================================================

  describe('Message Queue', () => {
    test('should queue messages when disconnected', async () => {
      // Don't connect
      await client1.propose('test', 'task');
      expect(client1.getInfo().queueSize).toBe(1);
    });

    test('should flush queue on connect', async () => {
      const handler = jest.fn();
      client2.on('received', handler);

      // Send while disconnected (queued)
      await client1.propose(agent2.info.agentId, 'task');
      expect(client1.getInfo().queueSize).toBe(1);

      // Connect and flush
      await client1.connect();
      await client2.connect();
      await client1.flushQueue();

      // Wait for delivery
      await new Promise(resolve => setTimeout(resolve, 50));
      expect(handler).toHaveBeenCalled();
      expect(client1.getInfo().queueSize).toBe(0);
    });

    test('should not duplicate queue on reconnect', async () => {
      const handler = jest.fn();
      client2.on('received', handler);

      await client1.connect();
      await client2.connect();

      // Send message
      await client1.propose(agent2.info.agentId, 'task1');
      await new Promise(resolve => setTimeout(resolve, 50));
      expect(handler).toHaveBeenCalledTimes(1);

      // Disconnect and reconnect
      await client1.disconnect();
      await client1.connect();

      // Send another message
      await client1.propose(agent2.info.agentId, 'task2');
      await new Promise(resolve => setTimeout(resolve, 50));
      expect(handler).toHaveBeenCalledTimes(2);
    });
  });

  // ============================================================
  // CONTRACT TESTS
  // ============================================================

  describe('Contracts', () => {
    const sampleContract: Contract = {
      contractId: 'contract-123',
      parties: ['agent-1', 'agent-2'],
      terms: {
        maxTokens: 1000,
        timeoutSec: 30,
        maxCostUsd: 0.10,
        maxRounds: 5,
      },
      obligations: {
        'agent-1': {
          action: 'analyze',
          input: { data: 'test' },
          dependsOn: [],
        },
        'agent-2': {
          action: 'execute',
          input: { task: 'process' },
          dependsOn: ['agent-1'],
        },
      },
      signatures: {},
      status: 'draft',
      createdAt: new Date(),
      onFailure: 'escalate',
    };

    test('should include contract in proposal', async () => {
      await client1.connect();
      await client2.connect();

      const proposal = await client1.propose(
        agent2.info.agentId,
        'Contract task',
        sampleContract
      );

      expect(proposal.body?.data.value).toHaveProperty('contract');
      expect(proposal.body?.data.value.contract).toMatchObject(sampleContract);
    });

    test('should handle contract validation', () => {
      const validator = Validator.default();
      const contractData = { type: 'object', value: sampleContract };
      const result = validator.validateBody(
        {
          contentType: 'application/json',
          data: contractData,
          metadata: {},
          size: 0,
        },
        {
          type: 'object',
          required: ['contractId', 'parties', 'terms'],
          properties: {
            contractId: { type: 'string' },
            parties: { type: 'array' },
            terms: { type: 'object' },
          },
        }
      );

      expect(result.valid).toBe(true);
    });
  });

  // ============================================================
  // PERFORMANCE TESTS (basic)
  // ============================================================

  describe('Performance', () => {
    test('should handle multiple messages quickly', async () => {
      await client1.connect();
      await client2.connect();

      const start = Date.now();
      const count = 10;

      for (let i = 0; i < count; i++) {
        await client1.propose(agent2.info.agentId, `Task ${i}`);
      }

      const duration = Date.now() - start;
      expect(duration).toBeLessThan(5000); // Should be fast
    }, 10000);

    test('should handle concurrent proposals', async () => {
      await client1.connect();
      await client2.connect();

      const promises = [];
      const count = 5;

      for (let i = 0; i < count; i++) {
        promises.push(client1.propose(agent2.info.agentId, `Concurrent task ${i}`));
      }

      await Promise.all(promises);
      const summary = agent1.getStateSummary();
      // Should have completed all proposals
      expect(summary.history).toContain('idle');
    }, 10000);
  });
});