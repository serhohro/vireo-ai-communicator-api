/**
 * Vireo TypeScript SDK - Agent
 * 
 * @module agent
 */

import { randomUUID } from 'crypto';
import { AgentInfo, AgentRole, AgentCapability, MessageEnvelope, MessageType } from './types';
import { Validator } from './validator';
import { ProtocolError, StateError } from './errors';
import { WireFormat } from './wire_format';

// ============================================================
// Agent State Machine
// ============================================================

export type AgentState = 'idle' | 'discovering' | 'proposing' | 'negotiating' | 'committing' | 'executing' | 'verifying' | 'done' | 'error';

export interface AgentStateMachine {
  state: AgentState;
  history: AgentState[];
  context: Record<string, any>;
  startedAt: Date;
  updatedAt: Date;
}

// ============================================================
// Vireo Agent
// ============================================================

export class VireoAgent {
  private agentId: string;
  private name: string;
  private role: AgentRole;
  private capabilities: Map<string, AgentCapability> = new Map();
  private stateMachine: AgentStateMachine;
  private validator: Validator;
  private listeners: Map<string, ((...args: any[]) => void)[]> = new Map();
  private messageHandlers: Map<MessageType, (message: MessageEnvelope) => Promise<void>> = new Map();

  constructor(name: string, role: AgentRole = 'worker') {
    this.agentId = `agent-${randomUUID().slice(0, 8)}`;
    this.name = name;
    this.role = role;
    this.validator = Validator.default();
    this.stateMachine = {
      state: 'idle',
      history: [],
      context: {},
      startedAt: new Date(),
      updatedAt: new Date(),
    };
  }

  /**
   * Get agent information
   */
  get info(): AgentInfo {
    return {
      agentId: this.agentId,
      name: this.name,
      role: this.role,
      capabilities: Array.from(this.capabilities.keys()),
      description: `Vireo agent: ${this.name}`,
    };
  }

  /**
   * Get current state
   */
  get state(): AgentState {
    return this.stateMachine.state;
  }

  /**
   * Register a capability
   */
  registerCapability(name: string, description: string, handler: (...args: any[]) => Promise<any>): void {
    if (this.capabilities.has(name)) {
      throw new Error(`Capability "${name}" already registered`);
    }
    this.capabilities.set(name, { name, description, handler });
  }

  /**
   * Check if agent has a capability
   */
  hasCapability(name: string): boolean {
    return this.capabilities.has(name);
  }

  /**
   * Execute a capability
   */
  async executeCapability(name: string, ...args: any[]): Promise<any> {
    const capability = this.capabilities.get(name);
    if (!capability) {
      throw new Error(`Capability "${name}" not found`);
    }
    try {
      return await capability.handler(...args);
    } catch (error) {
      throw new Error(`Capability execution failed: ${error}`);
    }
  }

  /**
   * Get all capabilities
   */
  getCapabilities(): string[] {
    return Array.from(this.capabilities.keys());
  }

  /**
   * Register a message handler
   */
  on(type: MessageType, handler: (message: MessageEnvelope) => Promise<void>): void {
    this.messageHandlers.set(type, handler);
  }

  /**
   * Register an event listener
   */
  addListener(event: string, listener: (...args: any[]) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(listener);
  }

  /**
   * Emit an event
   */
  private emit(event: string, ...args: any[]): void {
    const listeners = this.listeners.get(event) || [];
    for (const listener of listeners) {
      try {
        listener(...args);
      } catch (error) {
        console.error(`Event listener error: ${error}`);
      }
    }
  }

  /**
   * Handle an incoming message
   */
  async handleMessage(envelope: MessageEnvelope): Promise<MessageEnvelope | undefined> {
    // Validate message
    const validation = this.validator.validate(envelope);
    if (!validation.valid) {
      throw new Error(`Invalid message: ${validation.errors.join(', ')}`);
    }

    // Emit event
    this.emit('message', envelope);

    // Handle by type
    const handler = this.messageHandlers.get(envelope.header.type);
    if (handler) {
      await handler(envelope);
    }

    // Update state
    this.updateState(`handled_${envelope.header.type}`);

    return undefined;
  }

  /**
   * Propose a task
   */
  async propose(recipient: string, task: string, contract?: any): Promise<MessageEnvelope> {
    this.updateState('proposing');

    const envelope: MessageEnvelope = {
      header: {
        type: 'propose',
        version: '3.0.0',
        messageId: randomUUID(),
        timestamp: new Date(),
        sender: this.agentId,
        receiver: recipient,
        ttlSeconds: 300,
        priority: 0,
        flags: [],
      },
      body: {
        contentType: 'application/json',
        data: { type: 'object', value: { task, contract } },
        metadata: { timestamp: new Date().toISOString() },
        size: 0,
      },
    };

    this.emit('proposed', envelope);
    return envelope;
  }

  /**
   * Commit to a proposal
   */
  async commit(proposalId: string): Promise<MessageEnvelope> {
    this.updateState('committing');

    const envelope: MessageEnvelope = {
      header: {
        type: 'commit',
        version: '3.0.0',
        messageId: randomUUID(),
        timestamp: new Date(),
        sender: this.agentId,
        correlationId: proposalId,
        ttlSeconds: 300,
        priority: 0,
        flags: [],
      },
      body: {
        contentType: 'application/json',
        data: { type: 'object', value: { proposalId, status: 'committed' } },
        metadata: {},
        size: 0,
      },
    };

    this.emit('committed', envelope);
    return envelope;
  }

  /**
   * Execute a task
   */
  async execute(proposalId: string, input?: any): Promise<MessageEnvelope> {
    this.updateState('executing');

    // Find and execute capability
    const result = await this.executeCapability('execute', input);

    const envelope: MessageEnvelope = {
      header: {
        type: 'execute',
        version: '3.0.0',
        messageId: randomUUID(),
        timestamp: new Date(),
        sender: this.agentId,
        correlationId: proposalId,
        ttlSeconds: 300,
        priority: 0,
        flags: [],
      },
      body: {
        contentType: 'application/json',
        data: { type: 'object', value: { proposalId, result } },
        metadata: {},
        size: 0,
      },
    };

    this.emit('executed', envelope);
    return envelope;
  }

  /**
   * Verify execution result
   */
  async verify(executionId: string, result: any): Promise<MessageEnvelope> {
    this.updateState('verifying');

    const isValid = result && result.status === 'success';

    const envelope: MessageEnvelope = {
      header: {
        type: 'verify',
        version: '3.0.0',
        messageId: randomUUID(),
        timestamp: new Date(),
        sender: this.agentId,
        correlationId: executionId,
        ttlSeconds: 300,
        priority: 0,
        flags: [],
      },
      body: {
        contentType: 'application/json',
        data: { type: 'object', value: { executionId, verified: isValid, result } },
        metadata: {},
        size: 0,
      },
    };

    this.emit('verified', envelope);
    return envelope;
  }

  /**
   * Escalate an issue
   */
  async escalate(issueId: string, reason: string): Promise<MessageEnvelope> {
    this.updateState('error');

    const envelope: MessageEnvelope = {
      header: {
        type: 'escalate',
        version: '3.0.0',
        messageId: randomUUID(),
        timestamp: new Date(),
        sender: this.agentId,
        ttlSeconds: 300,
        priority: 1,
        flags: [],
      },
      body: {
        contentType: 'application/json',
        data: { type: 'object', value: { issueId, reason } },
        metadata: {},
        size: 0,
      },
    };

    this.emit('escalated', envelope);
    return envelope;
  }

  /**
   * Mark as done
   */
  async done(result: any): Promise<MessageEnvelope> {
    this.updateState('done');

    const envelope: MessageEnvelope = {
      header: {
        type: 'done',
        version: '3.0.0',
        messageId: randomUUID(),
        timestamp: new Date(),
        sender: this.agentId,
        ttlSeconds: 300,
        priority: 0,
        flags: [],
      },
      body: {
        contentType: 'application/json',
        data: { type: 'object', value: { result, completedAt: new Date().toISOString() } },
        metadata: {},
        size: 0,
      },
    };

    this.emit('done', envelope);
    return envelope;
  }

  /**
   * Serialize message to wire format
   */
  serialize(envelope: MessageEnvelope): Uint8Array {
    return WireFormat.serialize(envelope);
  }

  /**
   * Deserialize message from wire format
   */
  deserialize(data: Uint8Array): MessageEnvelope {
    return WireFormat.deserialize(data);
  }

  /**
   * Update agent state
   */
  private updateState(newState: AgentState): void {
    this.stateMachine.history.push(this.stateMachine.state);
    this.stateMachine.state = newState;
    this.stateMachine.updatedAt = new Date();
    this.emit('stateChange', newState);
  }

  /**
   * Reset agent state
   */
  reset(): void {
    this.stateMachine.state = 'idle';
    this.stateMachine.history = [];
    this.stateMachine.context = {};
    this.stateMachine.startedAt = new Date();
    this.stateMachine.updatedAt = new Date();
    this.emit('reset');
  }

  /**
   * Get state machine summary
   */
  getStateSummary(): any {
    return {
      state: this.stateMachine.state,
      history: this.stateMachine.history.slice(-10),
      context: this.stateMachine.context,
      startedAt: this.stateMachine.startedAt,
      updatedAt: this.stateMachine.updatedAt,
    };
  }

  /**
   * Start the agent
   */
  async start(): Promise<void> {
    this.updateState('idle');
    this.emit('started');
  }

  /**
   * Stop the agent
   */
  async stop(): Promise<void> {
    this.updateState('idle');
    this.emit('stopped');
  }

  /**
   * Get agent info as JSON
   */
  toJSON(): Record<string, any> {
    return {
      agentId: this.agentId,
      name: this.name,
      role: this.role,
      capabilities: this.getCapabilities(),
      state: this.state,
      info: this.info,
    };
  }

  /**
   * String representation
   */
  toString(): string {
    return `VireoAgent(${this.agentId}, ${this.name}, role=${this.role}, state=${this.state})`;
  }
}