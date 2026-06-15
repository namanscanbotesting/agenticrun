//! AgentIdentity Smart Contract
//! Verifiable on-chain identity and reputation for AI agents.

use odra::prelude::*;
use odra::collections::{Mapping, Vec};

/// Agent Types
#[odra::type]
pub enum AgentType {
    Oracle,
    YieldRouter,
    Compliance,
    Governor,
}

/// Structure representing an action logged by an agent
#[odra::type]
pub struct ActionLog {
    pub action_id: u64,
    pub action_type: String,
    pub tx_hash: String,
    pub result: bool, // true = success, false = failure
    pub timestamp: u64,
    pub challenged: bool,
}

/// Structure representing an agent's full profile
#[odra::type]
pub struct AgentProfile {
    pub name: String,
    pub agent_type: AgentType,
    pub capabilities: Vec<String>,
    pub registered_at: u64,
    pub total_actions: u64,
    pub successful_actions: u64,
    pub reputation_score: u8, // 0-100
}

/// Structure for challenging an action
#[odra::type]
pub struct Challenge {
    pub action_id: u64,
    pub challenger: Key,
    pub evidence: String,
    pub timestamp: u64,
    pub resolved: bool,
}

/// AgentIdentity Contract
#[odra::module]
pub struct AgentIdentityContract {
    /// Map of agent address to AgentProfile
    agents: Mapping<Key, AgentProfile>,
    /// Map of agent address to their action logs (Vec of ActionLog)
    action_logs: Mapping<Key, Vec<ActionLog>>,
    /// Map of action challenges (action_id -> Challenge)
    challenges: Mapping<u64, Challenge>,
    /// Counter for action IDs
    action_counter: Mapping<Key, u64>,
    /// Admin address
    admin: Key,
}

#[odra::module]
impl AgentIdentityContract {
    /// Constructor
    #[odra(init)]
    pub fn init(&mut self) {
        self.admin.set(caller());
    }

    /// Register a new AI agent
    pub fn register_agent(
        &mut self,
        agent_address: Key,
        name: String,
        agent_type: AgentType,
        capabilities: Vec<String>,
    ) {
        let now = block_time();
        let profile = AgentProfile {
            name,
            agent_type,
            capabilities,
            registered_at: now,
            total_actions: 0,
            successful_actions: 0,
            reputation_score: 50, // Start neutral
        };

        self.agents.insert(agent_address, profile);
        self.action_counter.insert(agent_address, 0);
        self.action_logs.insert(agent_address, Vec::new());

        self.emit_event(AgentRegistered {
            agent: agent_address,
            name,
            agent_type,
        });
    }

    /// Record an action performed by an agent
    pub fn record_action(
        &mut self,
        action_type: String,
        tx_hash: String,
        result: bool,
    ) {
        let agent = caller();
        
        // Get current counter
        let mut counter = self.action_counter.get(&agent).unwrap_or(0);
        counter += 1;
        self.action_counter.insert(agent, counter);

        let action = ActionLog {
            action_id: counter,
            action_type,
            tx_hash,
            result,
            timestamp: block_time(),
            challenged: false,
        };

        // Add to logs
        if let Some(mut logs) = self.action_logs.get(&agent) {
            logs.push(action.clone());
            self.action_logs.insert(agent, logs);
        }

        // Update profile stats
        if let Some(mut profile) = self.agents.get(&agent) {
            profile.total_actions += 1;
            if result {
                profile.successful_actions += 1;
            }
            // Recalculate reputation score
            if profile.total_actions > 0 {
                profile.reputation_score = 
                    ((profile.successful_actions * 100) / profile.total_actions) as u8;
            }
            self.agents.insert(agent, profile);
        }

        self.emit_event(ActionRecorded {
            agent,
            action_id: counter,
            action_type,
            result,
        });
    }

    /// Get full agent profile
    pub fn get_agent_reputation(&self, agent: Key) -> Option<AgentProfile> {
        self.agents.get(&agent)
    }

    /// Get action logs for an agent (paginated in real impl)
    pub fn get_agent_actions(&self, agent: Key, limit: u32) -> Vec<ActionLog> {
        if let Some(logs) = self.action_logs.get(&agent) {
            let len = logs.len().min(limit as usize);
            let mut result = Vec::new();
            for i in 0..len {
                if let Some(log) = logs.get(i) {
                    result.push(log);
                }
            }
            result
        } else {
            Vec::new()
        }
    }

    /// Challenge a specific action (Anyone can challenge)
    pub fn challenge_action(&mut self, agent: Key, action_id: u64, evidence: String) {
        let challenger = caller();
        
        // Verify action exists
        let mut found = false;
        if let Some(logs) = self.action_logs.get(&agent) {
            for i in 0..logs.len() {
                if let Some(log) = logs.get(i) {
                    if log.action_id == action_id {
                        found = true;
                        break;
                    }
                }
            }
        }
        assert!(found, "Action not found");

        let challenge = Challenge {
            action_id,
            challenger,
            evidence,
            timestamp: block_time(),
            resolved: false,
        };

        self.challenges.insert(action_id, challenge);

        self.emit_event(ActionChallenged {
            agent,
            action_id,
            challenger,
        });
    }

    /// Resolve a challenge (Admin only)
    pub fn resolve_challenge(&mut self, action_id: u64, is_valid: bool) {
        self.require_admin();

        if let Some(mut challenge) = self.challenges.get(&action_id) {
            challenge.resolved = true;
            self.challenges.insert(action_id, challenge);

            // If challenge valid, slash reputation (simplified)
            if !is_valid {
                // Find the agent who performed this action (would need reverse lookup in prod)
                // For now, just emit event
                self.emit_event(ChallengeResolved {
                    action_id,
                    is_valid,
                });
            }
        }
    }

    /// Helper: Ensure caller is admin
    fn require_admin(&self) {
        assert_eq!(caller(), self.admin.get(), "Only admin can call this");
    }
}

// Events
#[odra::type]
pub struct AgentRegistered {
    pub agent: Key,
    pub name: String,
    pub agent_type: AgentType,
}

#[odra::type]
pub struct ActionRecorded {
    pub agent: Key,
    pub action_id: u64,
    pub action_type: String,
    pub result: bool,
}

#[odra::type]
pub struct ActionChallenged {
    pub agent: Key,
    pub action_id: u64,
    pub challenger: Key,
}

#[odra::type]
pub struct ChallengeResolved {
    pub action_id: u64,
    pub is_valid: bool,
}
