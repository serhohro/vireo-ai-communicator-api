import * as ed from '@noble/ed25519';
import { blake2b } from '@noble/hashes/blake2b';
import { sha512 } from '@noble/hashes/sha512';

// @noble/ed25519@1.7.3: sha512Sync is on ed.utils, not ed.etc
ed.utils.sha512Sync = (...m: Uint8Array[]) => sha512(ed.utils.concatBytes(...m));

export const DIGEST_SIZE = 32;
export const SIGNATURE_SIZE = 64;
export const PUBLIC_KEY_SIZE = 32;
export const PRIVATE_KEY_SIZE = 32;
export const NONCE_SIZE = 16;

export function blake2b256(data: Uint8Array): Uint8Array {
  return blake2b(data, { dkLen: DIGEST_SIZE });
}

export function didHash(didString: string): Uint8Array {
  return blake2b256(new TextEncoder().encode(didString));
}

export function wireHash(canonicalBytes: Uint8Array): Uint8Array {
  return blake2b256(canonicalBytes);
}

export function payloadHash(payloadBytes: Uint8Array): Uint8Array {
  return blake2b256(payloadBytes);
}

export function sign(privateKey: Uint8Array, message: Uint8Array): Uint8Array {
  return ed.sign(message, privateKey);
}

export function verify(
  publicKey: Uint8Array,
  message: Uint8Array,
  signature: Uint8Array
): boolean {
  try {
    return ed.verify(signature, message, publicKey);
  } catch {
    return false;
  }
}

export function generateKeypair(): {
  privateKey: Uint8Array;
  publicKey: Uint8Array;
} {
  const privateKey = ed.utils.randomPrivateKey();
  const publicKey = ed.getPublicKey(privateKey);
  return { privateKey, publicKey };
}

export function getPublicKey(privateKey: Uint8Array): Uint8Array {
  return ed.getPublicKey(privateKey);
}

export function generateNonce(): Uint8Array {
  return ed.utils.randomPrivateKey().slice(0, NONCE_SIZE);
}

export function didFromName(name: string): string {
  const hash = blake2b256(new TextEncoder().encode(`agent:${name}`));
  return `did:vireo:${Buffer.from(hash).toString('base64url')}`;
}

export function toHex(bytes: Uint8Array): string {
  return Buffer.from(bytes).toString('hex');
}

export function fromHex(hex: string): Uint8Array {
  return new Uint8Array(Buffer.from(hex, 'hex'));
}
