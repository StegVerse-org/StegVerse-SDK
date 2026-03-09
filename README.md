# StegVerse SDK

SDK for interacting with the **StegVerse Trust Kernel**.

StegVerse introduces runtime governance for autonomous systems by verifying
whether actions are legitimately allowed to execute before they occur.

Instead of assuming autonomy is always permitted, StegVerse enforces decision
validation at the **execution boundary**.

system proposes action
        ↓
   Trust Kernel
        ↓
allow | deny | defer
        ↓
execution
        ↓
receipt

---

## Why StegVerse Exists

Autonomous systems can now:

• deploy infrastructure  
• control financial flows  
• manage cloud resources  
• coordinate other agents  

Most systems still operate like this:

model decides → system executes → humans audit afterward

This assumes every action should execute unless blocked.

StegVerse reverses this assumption.

Execution becomes a **privilege granted by governance**, not a default capability.

---

## Core Concepts

### Intent

An intent is a structured request describing an action a system wants to perform.

Example:

intent = {
    "action": "deploy.compute",
    "target": "render.cluster",
    "parameters": {
        "gpu": "A100",
        "count": 4
    }
}

### Decision

The Trust Kernel evaluates the intent and returns:

allow | deny | defer

### Execution Receipt

If execution occurs, a receipt proves:

• the action was authorized  
• the decision was verified  
• execution occurred within policy constraints  

Receipts create a verifiable history of system state transitions.

---

## Minimal SDK Interface

submit_intent(intent)

get_decision(intent_id)

verify_receipt(receipt)

---

## Architecture

Agent / Automation System
        ↓
StegVerse SDK
        ↓
Trust Kernel
        ↓
GCAT Evaluation
        ↓
Decision
        ↓
Execution
        ↓
Receipt Ledger

---

## Governance Model

StegVerse runtime governance follows the GCAT framework:

G — Governance  
C — Constraints  
A — Artifact execution pressure  
T — Trust continuity

The Trust Kernel enforces admissibility conditions ensuring system actions
never exceed governance capacity.

---

## Status

This repository contains the reference SDK for interacting with
StegVerse governance infrastructure.

Current focus:

• intent submission  
• Trust Kernel decision queries  
• receipt verification  
• integration examples
