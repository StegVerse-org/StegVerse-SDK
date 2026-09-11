#!/usr/bin/env node

import fs from 'node:fs';
import crypto from 'node:crypto';

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest();
}

function leafHash(salt, core) {
  return sha256(Buffer.concat([Buffer.from([0x00]), salt, core]));
}

function nodeHash(left, right) {
  return sha256(Buffer.concat([Buffer.from([0x01]), left, right]));
}

function largestPowerOfTwoLessThan(n) {
  if (n < 2) throw new Error('tree split requires at least two leaves');
  let k = 1;
  while ((k << 1) < n) k <<= 1;
  return k;
}

function merkleTreeHash(leaves) {
  if (leaves.length === 0) return sha256(Buffer.alloc(0));
  if (leaves.length === 1) return leaves[0];
  const split = largestPowerOfTwoLessThan(leaves.length);
  return nodeHash(
    merkleTreeHash(leaves.slice(0, split)),
    merkleTreeHash(leaves.slice(split)),
  );
}

function reproduce(fixture) {
  if (fixture.leaf_scheme !== 'mir.leaf.v3') throw new Error('unsupported leaf scheme');
  if (fixture.tree_profile !== 'rfc6962-mth-v1') throw new Error('unsupported tree profile');
  if (fixture.checkpoint_profile !== 'mir.checkpoint-tip.v0.3') throw new Error('unsupported checkpoint profile');

  const leaves = fixture.events.map((event, i) => {
    if (event.event_index !== i) throw new Error('event indexes must be contiguous and ordered');
    const digest = leafHash(
      Buffer.from(event.salt_base64, 'base64'),
      Buffer.from(event.canonical_event_core_base64, 'base64'),
    );
    const text = `sha256:${digest.toString('hex')}`;
    if (text !== event.expected_leaf_hash) throw new Error(`leaf mismatch at event ${i}`);
    return digest;
  });

  if (fixture.checkpoint.eventCount !== leaves.length) throw new Error('checkpoint eventCount mismatch');
  const merkleRoot = `sha256:${merkleTreeHash(leaves).toString('hex')}`;
  if (merkleRoot !== fixture.checkpoint.expected_merkle_root) throw new Error('merkle root mismatch');

  const prevTip = fixture.checkpoint.prevTip === null ? 'null' : String(fixture.checkpoint.prevTip);
  const preimage = [
    fixture.checkpoint.seq,
    fixture.checkpoint.rangeStart,
    fixture.checkpoint.rangeEnd,
    fixture.checkpoint.eventCount,
    merkleRoot,
    prevTip,
  ].join(':');
  const tip = `sha256:${sha256(Buffer.from(preimage, 'utf8')).toString('hex')}`;
  if (tip !== fixture.checkpoint.expected_tip) throw new Error('checkpoint tip mismatch');
  if (!Array.isArray(fixture.witnesses) || fixture.witnesses.length !== 0) throw new Error('witnesses must remain empty');
  if (!['NOT_REQUESTED', 'UNAVAILABLE'].includes(fixture.proof_status)) throw new Error('proof_status invalid');

  return {
    schema: 'neutral.mir-leaf-v3-conformance-result/v1',
    fixture_id: fixture.fixture_id,
    leaf_scheme: fixture.leaf_scheme,
    tree_profile: fixture.tree_profile,
    leaf_hashes: leaves.map((x) => `sha256:${x.toString('hex')}`),
    merkle_root: merkleRoot,
    checkpoint_tip: tip,
    proof_status: fixture.proof_status,
    witnesses: [],
    authority_effect: 'NONE_CONFORMANCE_EVIDENCE_ONLY',
  };
}

const fixturePath = process.argv[2];
if (!fixturePath) {
  console.error('usage: node tools/mir_leaf_v3_neutral_reproducer.mjs <fixture.json>');
  process.exit(2);
}

try {
  const fixture = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
  process.stdout.write(`${JSON.stringify(reproduce(fixture), null, 2)}\n`);
} catch (err) {
  console.error(`MIR_LEAF_V3_CONFORMANCE_FAILED: ${err.message}`);
  process.exit(1);
}
