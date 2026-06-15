# AgentVault Demo Video Script

## Duration: 2-3 minutes

---

### Scene 1: Problem Statement (0:00 - 0:30)

**Visual**: Split screen showing traditional portfolio management (person stressed at computer with multiple monitors) vs. AgentVault dashboard (clean, automated interface)

**Narration**:
"Managing Real World Asset portfolios across DeFi protocols is complex and time-consuming. Traditional approaches require constant monitoring, slow reaction to market changes, and expensive compliance overhead."

**On-screen text**: 
- ❌ Manual monitoring
- ❌ Slow reactions  
- ❌ High operational costs

---

### Scene 2: Introducing AgentVault (0:30 - 0:45)

**Visual**: AgentVault logo animation transitioning to architecture diagram

**Narration**:
"Introducing AgentVault - the first autonomous RWA portfolio manager powered by Agentic AI on Casper Network. Our multi-agent system works 24/7 to optimize your yields, assess risks, and ensure compliance - all autonomously."

**On-screen text**:
- ✅ Autonomous AI Agents
- ✅ Real-time Optimization
- ✅ Built on Casper Network

---

### Scene 3: Live Demo - Yield Agent in Action (0:45 - 1:30)

**Visual**: Screen recording of AgentVault dashboard

**Demo Flow**:
1. Show dashboard with connected wallet displaying current portfolio value
2. Highlight "Yield Monitoring" section showing live APY data from multiple Casper DeFi protocols
3. **KEY MOMENT**: Show Yield Agent detecting a high-yield opportunity (22.3% APY)
4. Show autonomous decision-making: "Opportunity detected! Rebalancing portfolio..."
5. Display transaction being signed via CSPR.click Agent Skill
6. Show x402 micropayment processing for the transaction
7. Display successful transaction hash on Casper Testnet explorer

**Narration**:
"Watch as our Yield Agent continuously monitors DeFi protocols via MCP servers. When it detects an opportunity exceeding our threshold - like this 22.3% APY on YieldFarm - it automatically rebalances the portfolio. The entire process is autonomous: analysis, decision, signing via Agent Skills, and execution with x402 micropayments."

**On-screen highlights**:
- "MCP Server Query: 3 protocols analyzed"
- "Decision: Rebalance to YieldFarm @ 22.3% APY"
- "x402 Payment: ✓ Processed"
- "Transaction: 0xabc123... confirmed on Casper Testnet"

---

### Scene 4: Multi-Agent Coordination (1:30 - 2:00)

**Visual**: Animated diagram showing all four agents working together

**Narration**:
"AgentVault isn't just one agent - it's a coordinated swarm of specialized AI agents. The Risk Agent assesses RWA market conditions using ML models. The Compliance Agent handles KYC/AML verification. The Execution Agent manages secure transaction signing. Together, they make AgentVault smarter than any single agent could be."

**On-screen graphics**:
- 🎯 Yield Agent → "Optimizing Returns"
- 📊 Risk Agent → "Assessing Market Risks"  
- ✅ Compliance Agent → "Ensuring Regulatory Adherence"
- 🔐 Execution Agent → "Secure Transaction Management"

---

### Scene 5: Technical Deep Dive (2:00 - 2:30)

**Visual**: Code snippets and architecture diagrams

**Narration**:
"Built on the full Casper AI Toolkit, AgentVault leverages MCP Servers for blockchain queries, x402 for micropayments, Agent Skills for wallet management, and Odra framework for smart contracts. Our three smart contracts - Portfolio Manager, RWA Registry, and Agent Reputation - provide the trust layer for autonomous operations."

**On-screen code highlights**:
```rust
// Odra Smart Contract - Portfolio Manager
#[odra::module]
pub fn rebalance(&mut self, allocations: Vec<Allocation>)
```

```python
# Python Agent - Autonomous Decision Making
async def monitor_opportunities(self):
    protocols = await self.mcp.query_defi_protocols()
    if best_yield.apr > threshold:
        await self.execute_rebalance()
```

---

### Scene 6: Impact & Vision (2:30 - 3:00)

**Visual**: Roadmap timeline and future use cases

**Narration**:
"AgentVault transforms passive RWA ownership into active, intelligent portfolio management. Post-hackathon, we're targeting mainnet deployment in Q3 2026, partnerships with RWA tokenization platforms, and institutional pilots by Q1 2027. We're building the future of autonomous finance on Casper."

**On-screen roadmap**:
- 🚀 June 2026: Buildathon Prototype
- 📈 Q3 2026: Mainnet Launch
- 🤝 Q4 2026: RWA Partnerships
- 🏦 Q1 2027: Institutional Pilots
- 🌐 2027+: Multi-chain Expansion

**Final Call-to-Action**:
"Vote for AgentVault on CSPR.fans and join us in building the future of autonomous DeFi!"

**On-screen final slide**:
- 🏆 **AgentVault**
- 🔗 GitHub: github.com/agentvault
- 🐦 Twitter: @AgentVaultDeFi
- 💬 Discord: discord.gg/agentvault
- ✅ **Vote on CSPR.fans!**

---

## Production Notes

### Recording Setup
- Use OBS Studio or similar for screen recording
- Record at 1080p 60fps minimum
- Ensure clear audio with minimal background noise

### Visual Assets Needed
1. AgentVault logo (animated version preferred)
2. Dashboard screenshots/mockups
3. Architecture diagrams
4. Casper Testnet transaction links prepared
5. Code syntax highlighting theme

### Music & Sound
- Upbeat, tech-focused background music (royalty-free)
- Subtle sound effects for transitions
- Clear voiceover narration

### Editing Tips
- Keep transitions smooth and professional
- Add subtle zoom/pan effects on static images
- Include captions for accessibility
- End with clear call-to-action for voting

---

## Backup Scenes (if needed)

### Alternative Demo: Risk Assessment
Show Risk Agent analyzing market data and posting risk scores on-chain.

### Alternative Demo: Compliance Onboarding
Demonstrate user KYC flow with Compliance Agent issuing compliance token.

### Team Introduction
Brief intro of team members and their roles (if team-based submission).
