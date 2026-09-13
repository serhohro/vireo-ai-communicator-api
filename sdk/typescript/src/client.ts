/**
 * Vireo TypeScript SDK - Client
 * 
 * @module client
 */

import { EventEmitter } from 'events';
import { VireoAgent } from './agent';
import { MessageEnvelope, MessageType } from './types';
import { ProtocolError } from './errors';
import { WireFormat } from './wire_format';

// ============================================================
// Transport Interface
// ============================================================

export interface Transport {
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  send(data: Uint8Array): Promise<void>;
  subscribe(callback: (data: Uint8Array) => void): void;
  unsubscribe(): void;
  isConnected(): boolean;
}

// ============================================================
// In-Memory Transport
// ============================================================

export class InMemoryTransport implements Transport {
  private connected: boolean = false;
  private subscribers: ((data: Uint8Array) => void)[] = [];
  private peers: InMemoryTransport[] = [];

  async connect(): Promise<void> {
    this.connected = true;
  }

  async disconnect(): Promise<void> {
    this.connected = false;
    this.subscribers = [];
  }

  async send(data: Uint8Array): Promise<void> {
    if (!this.connected) {
      throw new Error('Transport not connected');
    }
    // Broadcast to all peers
    for (const peer of this.peers) {
      peer.receive(data);
    }
  }

  subscribe(callback: (data: Uint8Array) => void): void {
    this.subscribers.push(callback);
  }

  unsubscribe(): void {
    this.subscribers = [];
  }

  isConnected(): boolean {
    return this.connected;
  }

  receive(data: Uint8Array): void {
    for (const subscriber of this.subscribers) {
      try {
        subscriber(data);
      } catch (error) {
        console.error('Subscriber error:', error);
      }
    }
  }

  connectTo(peer: InMemoryTransport): void {
    if (!this.peers.includes(peer)) {
      this.peers.push(peer);
    }
    if (!peer.peers.includes(this)) {
      peer.peers.push(this);
    }
  }
}

// ============================================================
// Vireo Client
// ============================================================

export interface VireoClientOptions {
  agentId?: string;
  transport?: Transport;
  autoConnect?: boolean;
}

export class VireoClient extends EventEmitter {
  private agent: VireoAgent;
  private transport: Transport;
  private connected: boolean = false;
  private messageQueue: MessageEnvelope[] = [];
  private pendingResponses: Map<string, (envelope: MessageEnvelope) => void> = new Map();

  constructor(agent: VireoAgent, options: VireoClientOptions = {}) {
    super();
    this.agent = agent;
    this.transport = options.transport || new InMemoryTransport();
  }

  /**
   * Connect to the network
   */
  async connect(): Promise<void> {
    if (this.connected) {
      return;
    }

    try {
      await this.transport.connect();
      this.connected = true;
      this.transport.subscribe(this.handleIncoming.bind(this));
      this.emit('connected');
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Disconnect from the network
   */
  async disconnect(): Promise<void> {
    if (!this.connected) {
      return;
    }

    try {
      this.transport.unsubscribe();
      await this.transport.disconnect();
      this.connected = false;
      this.emit('disconnected');
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Send a message
   */
  async send(envelope: MessageEnvelope): Promise<void> {
    if (!this.connected) {
      // Queue message for later
      this.messageQueue.push(envelope);
      return;
    }

    try {
      const data = this.agent.serialize(envelope);
      await this.transport.send(data);
      this.emit('sent', envelope);
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Send and wait for response
   */
  async sendAndWait(envelope: MessageEnvelope, timeout: number = 30000): Promise<MessageEnvelope> {
    return new Promise((resolve, reject) => {
      const messageId = envelope.header.messageId;
      const timeoutId = setTimeout(() => {
        this.pendingResponses.delete(messageId);
        reject(new Error(`Response timeout after ${timeout}ms`));
      }, timeout);

      this.pendingResponses.set(messageId, (response: MessageEnvelope) => {
        clearTimeout(timeoutId);
        this.pendingResponses.delete(messageId);
        resolve(response);
      });

      this.send(envelope).catch((error) => {
        clearTimeout(timeoutId);
        this.pendingResponses.delete(messageId);
        reject(error);
      });
    });
  }

  /**
   * Handle incoming messages
   */
  private async handleIncoming(data: Uint8Array): Promise<void> {
    try {
      const envelope = this.agent.deserialize(data);
      this.emit('received', envelope);

      // Handle pending response
      if (envelope.header.correlationId) {
        const resolver = this.pendingResponses.get(envelope.header.correlationId);
        if (resolver) {
          resolver(envelope);
          return;
        }
      }

      // Pass to agent
      await this.agent.handleMessage(envelope);

      // Auto-respond to ACK if needed
      if (envelope.header.type === 'propose' || envelope.header.type === 'commit') {
        const ack: MessageEnvelope = {
          header: {
            type: 'ack',
            version: '3.0.0',
            messageId: `ack-${Date.now()}`,
            timestamp: new Date(),
            sender: this.agent.info.agentId,
            receiver: envelope.header.sender,
            correlationId: envelope.header.messageId,
            ttlSeconds: 60,
            priority: 0,
            flags: [],
          },
        };
        await this.send(ack);
      }
    } catch (error) {
      this.emit('error', error);
    }
  }

  /**
   * Flush message queue
   */
  async flushQueue(): Promise<void> {
    const queue = this.messageQueue;
    this.messageQueue = [];
    for (const envelope of queue) {
      await this.send(envelope);
    }
  }

  /**
   * Propose a task
   */
  async propose(recipient: string, task: string, contract?: any): Promise<MessageEnvelope> {
    const envelope = await this.agent.propose(recipient, task, contract);
    await this.send(envelope);
    return envelope;
  }

  /**
   * Propose and wait for response
   */
  async proposeAndWait(recipient: string, task: string, contract?: any, timeout?: number): Promise<MessageEnvelope> {
    const envelope = await this.agent.propose(recipient, task, contract);
    return await this.sendAndWait(envelope, timeout);
  }

  /**
   * Commit to a proposal
   */
  async commit(proposalId: string): Promise<MessageEnvelope> {
    const envelope = await this.agent.commit(proposalId);
    await this.send(envelope);
    return envelope;
  }

  /**
   * Execute a task
   */
  async execute(proposalId: string, input?: any): Promise<MessageEnvelope> {
    const envelope = await this.agent.execute(proposalId, input);
    await this.send(envelope);
    return envelope;
  }

  /**
   * Verify execution
   */
  async verify(executionId: string, result: any): Promise<MessageEnvelope> {
    const envelope = await this.agent.verify(executionId, result);
    await this.send(envelope);
    return envelope;
  }

  /**
   * Escalate an issue
   */
  async escalate(issueId: string, reason: string): Promise<MessageEnvelope> {
    const envelope = await this.agent.escalate(issueId, reason);
    await this.send(envelope);
    return envelope;
  }

  /**
   * Mark as done
   */
  async done(result: any): Promise<MessageEnvelope> {
    const envelope = await this.agent.done(result);
    await this.send(envelope);
    return envelope;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.connected && this.transport.isConnected();
  }

  /**
   * Get the underlying agent
   */
  getAgent(): VireoAgent {
    return this.agent;
  }

  /**
   * Get client info
   */
  getInfo(): Record<string, any> {
    return {
      connected: this.isConnected(),
      agent: this.agent.toJSON(),
      queueSize: this.messageQueue.length,
      pendingResponses: this.pendingResponses.size,
    };
  }
}