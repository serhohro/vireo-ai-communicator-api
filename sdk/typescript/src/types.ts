/**
 * Vireo TypeScript SDK - Type Definitions
 * 
 * Core types for Vireo communication protocol
 * 
 * @module types
 */

import { UUID } from 'crypto';

// ============================================================
// Vireo Value Types
// ============================================================

export type VireoType = 
  | 'null'
  | 'boolean'
  | 'integer'
  | 'float'
  | 'string'
  | 'binary'
  | 'array'
  | 'object'
  | 'timestamp'
  | 'duration'
  | 'uri'
  | 'uuid'
  | 'did'
  | 'signature'
  | 'public_key'
  | 'private_key'
  | 'hash'
  | 'nonce'
  | 'version';

export interface VireoValue<T = any> {
  type: VireoType;
  value: T;
}

export interface VireoObject {
  [key: string]: VireoValue;
}

export interface VireoArray extends Array<VireoValue> {}

// ============================================================
// DID (Decentralized Identifier)
// ============================================================

export interface DID {
  method: string;
  identifier: string;
  toString(): string;
}

export interface DIDDocument {
  '@context': string | string[];
  id: string;
  controller?: string | string[];
  alsoKnownAs?: string[];
  verificationMethod: VerificationMethod[];
  authentication: (string | VerificationMethod)[];
  assertionMethod: (string | VerificationMethod)[];
  keyAgreement: (string | VerificationMethod)[];
  capabilityInvocation: (string | VerificationMethod)[];
  capabilityDelegation: (string | VerificationMethod)[];
  service?: ServiceEndpoint[];
  created?: string;
  updated?: string;
  expires?: string;
}

export interface VerificationMethod {
  id: string;
  type: string;
  controller: string;
  publicKeyMultibase?: string;
  publicKeyHex?: string;
  publicKeyJwk?: JsonWebKey;
}

export interface ServiceEndpoint {
  id: string;
  type: string;
  serviceEndpoint: string | Record<string, any> | string[];
  description?: string;
}

// ============================================================
// Keys
// ============================================================

export interface KeyPair {
  publicKey: Uint8Array;
  privateKey: Uint8Array;
  algorithm: string;
}

export interface KeyMetadata {
  id: string;
  algorithm: string;
  usage: KeyUsage;
  state: KeyState;
  created: Date;
  expires?: Date;
  revokedAt?: Date;
  revokedReason?: string;
  issuer?: string;
  labels: string[];
}

export type KeyUsage = 'signing' | 'encryption' | 'auth' | 'agreement' | 'verification';
export type KeyState = 'active' | 'revoked' | 'expired' | 'suspended';

// ============================================================
// Messages
// ============================================================

export type MessageType = 
  | 'propose'
  | 'commit'
  | 'execute'
  | 'verify'
  | 'escalate'
  | 'done'
  | 'failed'
  | 'timeout'
  | 'ack'
  | 'nack'
  | 'query'
  | 'response'
  | 'error';

export interface MessageHeader {
  type: MessageType;
  version: string;
  messageId: string;
  timestamp: Date;
  sender: string;
  receiver?: string;
  correlationId?: string;
  replyTo?: string;
  nonce?: string;
  signature?: string;
  ttlSeconds: number;
  priority: number;
  flags: string[];
}

export interface MessageBody {
  contentType: string;
  data: VireoValue;
  metadata: Record<string, any>;
  schemaUri?: string;
  size: number;
}

export interface MessageEnvelope {
  header: MessageHeader;
  body?: MessageBody;
}

// ============================================================
// Protocol
// ============================================================

export type ProtocolState = 
  | 'init'
  | 'propose'
  | 'commit'
  | 'execute'
  | 'verify'
  | 'escalate'
  | 'done'
  | 'failed'
  | 'timeout'
  | 'paused';

export interface StateTransition {
  fromState: ProtocolState;
  toState: ProtocolState;
  condition?: (context: Record<string, any>) => boolean;
  action?: (context: Record<string, any>) => void;
  description?: string;
}

export interface ProtocolContext {
  sessionId: string;
  state: ProtocolState;
  metadata: Record<string, any>;
  startedAt: Date;
  updatedAt: Date;
}

// ============================================================
// Agent
// ============================================================

export interface AgentInfo {
  agentId: string;
  name: string;
  role: AgentRole;
  capabilities: string[];
  description: string;
  publicKey?: Uint8Array;
}

export type AgentRole = 
  | 'master'
  | 'worker'
  | 'executor'
  | 'guardian'
  | 'researcher'
  | 'analyst'
  | 'teacher'
  | 'custom';

export interface AgentCapability {
  name: string;
  description: string;
  handler: (...args: any[]) => Promise<any>;
}

// ============================================================
// Contract
// ============================================================

export interface Contract {
  contractId: string;
  parties: string[];
  terms: Terms;
  obligations: Record<string, Obligation>;
  condition?: string;
  onFailure: string;
  signatures: Record<string, string>;
  status: ContractStatus;
  createdAt: Date;
  updatedAt?: Date;
}

export interface Terms {
  maxTokens?: number;
  timeoutSec?: number;
  maxCostUsd?: number;
  maxRounds?: number;
  deadline?: string;
}

export interface Obligation {
  action: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  dependsOn: string[];
}

export type ContractStatus = 'draft' | 'proposed' | 'accepted' | 'committed' | 'executing' | 'executed' | 'verified' | 'failed';

// ============================================================
// Crypto
// ============================================================

export interface Signature {
  data: Uint8Array;
  signer: string;
  algorithm: string;
}

export interface Nonce {
  value: Uint8Array;
  timestamp: Date;
}

export interface Hash {
  value: Uint8Array;
  algorithm: string;
}

// ============================================================
// Reputation
// ============================================================

export interface ReputationScore {
  entityId: string;
  score: number;
  level: string;
  totalEvents: number;
  positiveEvents: number;
  negativeEvents: number;
  lastUpdate: Date;
  factors: Record<string, number>;
  confidence: number;
}

export interface ReputationEvent {
  id: string;
  entityId: string;
  eventType: string;
  factor: string;
  weight: number;
  timestamp: Date;
  description?: string;
  metadata: Record<string, any>;
}