# CasperMind: Autonomous Multi-Agent Intelligence Platform

## 🏆 Executive Summary

**CasperMind** is the ultimate submission for the Casper Agentic Buildathon 2026. It uniquely combines all four example directions (Yield Routing, RWA Oracles, DAO Governance, and Compliance) into a single, cohesive multi-agent ecosystem. Unlike other submissions that tackle individual problems, CasperMind creates a **machine-to-machine economy** where specialized AI agents collaborate, pay each other via x402 micropayments, and execute complex DeFi + RWA strategies autonomously on the Casper Network.

### Why CasperMind Wins
1. **Complete Toolkit Integration**: Uses EVERY component of the Casper AI Toolkit (Odra, MCP, x402, CSPR.click, CSPR.cloud).
2. **True Autonomy**: Agents make independent decisions, negotiate data prices, and execute transactions without human intervention.
3. **On-Chain Agent Identity**: Each agent has a verifiable on-chain reputation, making them first-class citizens of the blockchain.
4. **Machine-to-Machine Economy**: Implements the x402 protocol for agents to pay each other for services (e.g., Yield Agent pays Oracle Agent for fresh data).
5. **Real-World Applicability**: Addresses the $trillions RWA market and fragmented DeFi landscape with a unified solution.
6. **Community Vote Magnet**: Features a stunning real-time dashboard showing agent reasoning, decisions, and earnings live.

---

## 🎯 Problem Statement Alignment

The hackathon seeks applications at the intersection of **Agentic AI**, **DeFi**, and **RWA**. CasperMind directly addresses this by:
- **Agentic AI**: Deploying 4 distinct autonomous agents with specialized LLM-driven reasoning engines.
- **DeFi**: Automating yield optimization across Casper protocols via the Yield Router Agent.
- **RWA**: Providing verified, risk-assessed real-world asset data via the Oracle Agent.
- **Bonus Coverage**: Includes autonomous DAO governance (Governor Agent) and dynamic KYC/AML compliance (Compliance Agent), covering ALL example directions.

---

## 🏗️ System Architecture

### High-Level Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    CasperMind Dashboard (React)                  │
│  [Live Feed of Agent Reasoning] [Portfolio Stats] [Agent Earnings]│
└───────┬─────────────┬─────────────┬─────────────┬───────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Agent Orchestrator (Express API + SSE)              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Oracle  │ │  Yield   │ │Compliance│ │    Governor      │  │
│  │  Agent   │ │  Agent   │ │  Agent   │ │    Agent         │  │
│  │(LLM+MCP) │ │(LLM+MCP) │ │(LLM+ZK) │ │   (LLM+MCP)      │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
└───────┼─────────────┼─────────────┼─────────────────┼───────────┘
        │             │             │                 │
        ▼             ▼             ▼                 ▼
┌───────────────────────────────────────────────────────────────┐
│                    Casper AI Toolkit Layer                      │
│  [MCP Servers] ←→ [x402 Micropayments] ←→ [CSPR.cloud APIs]   │
│                         ↓                                      │
│                   [Odra Smart Contracts]                       │
└───────────────────────────────────────────────────────────────┘
        │                                         │
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────────┐
│  External Data       │              │   Casper Testnet          │
│  - Yahoo Finance     │              │   - OracleRegistry.wasm   │
│  - CoinGecko         │              │   - ComplianceToken.wasm  │
│  - Real Estate APIs  │              │   - AgentIdentity.wasm    │
└──────────────────────┘              └──────────────────────────┘
```

### The 4 Autonomous Agents

#### 1. Oracle Agent (RWA Intelligence)
- **Role**: Scrapes off-chain RWA data, runs risk models, posts verified data on-chain.
- **Key Feature**: Exposes an **x402-gated HTTP endpoint**. Other agents MUST pay this agent in CSPR to get fresh data.
- **On-Chain Action**: Posts `OracleEntry` to `OracleRegistry.wasm` with price, confidence score, and timestamp.
- **Revenue Model**: Earns CSPR micropayments from Yield and Governor agents for every data request.

#### 2. Yield Router Agent (DeFi Optimizer)
- **Role**: Monitors DeFi yields via MCP, calculates risk-adjusted returns, rebalances portfolios.
- **Key Feature**: Autonomously decides when to rebalance based on LLM analysis of Oracle data + DeFi states.
- **On-Chain Action**: Executes swaps/deposits via `CSPR.click` skill; logs performance to `AgentIdentity.wasm`.
- **Cost Model**: Pays Oracle Agent for data; keeps a % of generated yield as profit.

#### 3. Compliance Agent (Identity & KYC)
- **Role**: Verifies user identity, issues on-chain compliance tokens, monitors for changes.
- **Key Feature**: Issues upgradable `ComplianceToken.wasm` NFTs representing KYC levels (Basic, Enhanced, Institutional).
- **On-Chain Action**: Mints, upgrades, or revokes compliance tokens based on continuous off-chain monitoring.
- **Privacy**: Processes data in-memory; only hashes and token levels stored on-chain.

#### 4. Governor Agent (DAO Intelligence)
- **Role**: Analyzes DAO proposals, models impact, casts votes, executes treasury actions.
- **Key Feature**: Deliberates with other agents (pays Oracle for data) before voting.
- **On-Chain Action**: Casts votes and executes multi-sig treasury transactions autonomously.
- **Reputation**: Builds a track record of "successful" votes on `AgentIdentity.wasm`.

---

## 💻 Smart Contract Specifications (Odra/Rust)

### 1. OracleRegistry.wasm
**Purpose**: Store verified RWA data and track Oracle Agent reputation.
**Key Entry Points**:
- `post_oracle_data(asset_id, price, confidence, timestamp)`: Called by Oracle Agent.
- `get_oracle_data(asset_id)`: Public read access.
- `update_reputation(oracle_address, accuracy_score)`: Auto-updates based on data accuracy.
- `slash_reputation(oracle_address)`: Challenge mechanism for bad data.

### 2. ComplianceToken.wasm
**Purpose**: Issue and manage on-chain compliance status.
**Key Entry Points**:
- `issue_token(user, level, expires_at)`: Mints a compliance NFT.
- `revoke_token(user, reason)`: Revokes access if risk detected.
- `check_compliance(user)`: Returns status for DeFi protocols to query.

### 3. AgentIdentity.wasm
**Purpose**: Verifiable on-chain identity and reputation for AI agents.
**Key Entry Points**:
- `register_agent(name, agent_type, capabilities)`: Registers a new agent.
- `record_action(action_type, tx_hash, result)`: Logs every action for transparency.
- `get_agent_reputation(agent_address)`: Returns full history and success rate.
- `challenge_action(action_id, evidence)`: Allows community to dispute bad actions.

---

## 🔑 Casper AI Toolkit Integration Matrix

| Tool | Usage in CasperMind | Criticality |
| :--- | :--- | :--- |
| **Odra Framework** | Writing all 3 smart contracts in Rust. | **Required** |
| **MCP Servers** | Yield/Governor agents querying DeFi/Gov states directly. | **High** |
| **x402 Protocol** | Agent-to-Agent micropayments (Oracle selling data). | **Unique Selling Point** |
| **CSPR.click** | Wallet connection, transaction signing for all agents. | **High** |
| **CSPR.cloud** | Real-time event streaming, historical data for dashboard. | **Medium** |

---

## 📅 15-Day Execution Plan (June 15 - June 30)

### Phase 1: Foundation (Days 1-3)
- **Day 1**: Setup Casper Testnet, Odra CLI, and GitHub repo. Scaffold `OracleRegistry.wasm`.
- **Day 2**: Deploy `OracleRegistry.wasm`. Build Oracle Agent skeleton (fetch → LLM → sign → post).
- **Day 3**: Implement x402 gated endpoint for Oracle Agent. Scaffold remaining 2 contracts.

### Phase 2: Core Agents (Days 4-7)
- **Day 4**: Build Yield Agent (MCP integration + x402 payment logic).
- **Day 5**: Build Compliance Agent (KYC flow + token minting).
- **Day 6**: Build Governor Agent (Proposal analysis + voting).
- **Day 7**: **Integration Day**: Run all 4 agents together. Verify inter-agent payments.

### Phase 3: Polish & UI (Days 8-11)
- **Day 8**: Build React Dashboard with Server-Sent Events (SSE) for live agent reasoning feed.
- **Day 9**: Add challenge mechanisms to contracts. Optimize gas usage.
- **Day 10**: Create "Agent Performance" metrics UI. Draft Whitepaper.
- **Day 11**: Bug bash. Fix critical issues. Setup social media channels.

### Phase 4: Submission & Campaign (Days 12-15)
- **Day 12**: Record high-quality demo video showing LIVE autonomous trades and x402 payments.
- **Day 13**: Launch community voting campaign on CSPR.fans (Discord, Telegram, Twitter).
- **Day 14**: Final code audit. Ensure all README docs are perfect.
- **Day 15**: Submit to DoraHacks. Push for Top 3 community votes.

---

## 🎬 Demo Video Script Outline

1.  **Hook (0:00-1:00)**: "Watch an AI agent detect a yield opportunity, pay another agent for data via x402, and execute a trade—autonomously." (Show live tx).
2.  **Problem (1:00-3:00)**: Explain fragmented DeFi/RWA landscape and lack of trust infrastructure for AI.
3.  **Architecture (3:00-6:00)**: Animated diagram of the 4 agents and money flow.
4.  **Live Demo (6:00-10:00)**:
    *   Show Oracle Agent posting data.
    *   Show Yield Agent paying for it (x402 receipt).
    *   Show LLM reasoning in dashboard.
    *   Show transaction execution on Testnet explorer.
    *   Show Compliance Token issuance.
5.  **Vision (10:00-12:00)**: Roadmap to mainnet and open platform for third-party agents.

---

## 🚀 Winning Strategy Checklist

- [ ] **Working Prototype**: All 3 contracts deployed on Testnet with successful transactions.
- [ ] **Autonomy**: Agents run on a cron/scheduler without manual triggers during demo.
- [ ] **x402 Integration**: Visible proof of agent-to-agent payments in logs/UI.
- [ ] **On-Chain Identity**: `AgentIdentity.wasm` showing reputation scores for each agent.
- [ ] **Community Votes**: Aggressive campaigning on CSPR.fans to secure Top 3 spot.
- [ ] **Documentation**: Comprehensive README, Architecture.md, and Whitepaper.
- [ ] **Video**: Professional demo highlighting the "Magic" of autonomous coordination.

By executing this plan, CasperMind positions itself not just as another hackathon project, but as a foundational layer for the future Agentic Economy on Casper.
