/**
 * Vireo TypeScript SDK v3.0.0
 * 
 * The World's First AI-to-AI Communication Language
 * 
 * @packageDocumentation
 * @author Serhii (serhohro)
 * @license Apache 2.0
 * @version 3.0.0
 */

// Core exports
export * from './types';
export * from './errors';

// Agent
export * from './agent';

// Client
export * from './client';

// Wire Format
export * from './wire_format';

// Validator
export * from './validator';

// Crypto
export * from './crypto';

// Version
export const VERSION = '3.0.0';
export const AUTHOR = 'Serhii (serhohro)';
export const LICENSE = 'Apache 2.0';

// Re-export main components
export { VireoAgent } from './agent';
export { VireoClient } from './client';
export { WireFormat } from './wire_format';
export { Validator } from './validator';

// Default export for convenience
import { VireoAgent } from './agent';
import { VireoClient } from './client';
import { WireFormat } from './wire_format';

export default {
  VireoAgent,
  VireoClient,
  WireFormat,
  VERSION,
  AUTHOR,
  LICENSE,
};