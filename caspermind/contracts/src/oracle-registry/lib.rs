//! OracleRegistry Smart Contract
//! Stores verified RWA data posted by the Oracle Agent and tracks reputation.

use odra::prelude::*;
use odra::collections::Mapping;
use odra::ContractRef;

/// Structure representing an Oracle data entry
#[odra::type]
pub struct OracleEntry {
    pub price: U256,
    pub confidence: u8,
    pub timestamp: u64,
    pub agent_address: Key,
}

/// Structure representing an Agent's reputation profile
#[odra::type]
pub struct AgentProfile {
    pub total_posts: u32,
    pub accurate_posts: u32,
    pub reputation_score: u8, // 0-100
}

/// OracleRegistry Contract
#[odra::module]
pub struct OracleRegistry {
    /// Map of asset_id to latest OracleEntry
    oracle_data: Mapping<String, OracleEntry>,
    /// Map of agent address to AgentProfile
    reputation: Mapping<Key, AgentProfile>,
    /// Challenge window in blocks (e.g., 100 blocks)
    challenge_window: u64,
    /// Owner (admin) address
    owner: Key,
}

#[odra::module]
impl OracleRegistry {
    /// Constructor: Initialize the contract
    #[odra(init)]
    pub fn init(&mut self, challenge_window: u64) {
        self.challenge_window.set(challenge_window);
        self.owner.set(caller());
    }

    /// Post new oracle data (Called by Oracle Agent)
    #[odra(no_mutable_state)]
    pub fn post_oracle_data(
        &mut self,
        asset_id: String,
        price: U256,
        confidence: u8,
    ) {
        let caller_addr = caller();
        let timestamp = block_time();

        // Create new entry
        let entry = OracleEntry {
            price,
            confidence,
            timestamp,
            agent_address: caller_addr,
        };

        // Store entry
        self.oracle_data.insert(asset_id.clone(), entry);

        // Update reputation (increment total posts)
        self.update_reputation_total(&caller_addr);
        
        // Emit event
        self.emit_event(OracleDataPosted {
            asset_id,
            price,
            confidence,
            timestamp,
            agent: caller_addr,
        });
    }

    /// Get oracle data for an asset
    pub fn get_oracle_data(&self, asset_id: String) -> Option<OracleEntry> {
        self.oracle_data.get(&asset_id)
    }

    /// Update reputation: increment total posts
    fn update_reputation_total(&mut self, agent: &Key) {
        let mut profile = self.reputation.get(agent).unwrap_or(AgentProfile {
            total_posts: 0,
            accurate_posts: 0,
            reputation_score: 50, // Start with neutral score
        });
        profile.total_posts += 1;
        self.reputation.insert(*agent, profile);
    }

    /// Update accuracy score (Called by admin or automated system)
    pub fn update_accuracy(&mut self, agent: Key, is_accurate: bool) {
        if let Some(mut profile) = self.reputation.get(&agent) {
            if is_accurate {
                profile.accurate_posts += 1;
            }
            // Recalculate score
            if profile.total_posts > 0 {
                profile.reputation_score = 
                    ((profile.accurate_posts as u32 * 100) / profile.total_posts) as u8;
            }
            self.reputation.insert(agent, profile);
        }
    }

    /// Slash reputation (Called if data proven wrong)
    pub fn slash_reputation(&mut self, agent: Key, penalty: u8) {
        if let Some(mut profile) = self.reputation.get(&agent) {
            profile.reputation_score = profile.reputation_score.saturating_sub(penalty);
            self.reputation.insert(agent, profile);
            
            self.emit_event(ReputationSlashed {
                agent,
                penalty,
                new_score: profile.reputation_score,
            });
        }
    }

    /// Get agent reputation
    pub fn get_agent_reputation(&self, agent: Key) -> Option<AgentProfile> {
        self.reputation.get(&agent)
    }

    /// Set challenge window (Admin only)
    pub fn set_challenge_window(&mut self, window: u64) {
        self.require_owner();
        self.challenge_window.set(window);
    }

    /// Helper: Ensure caller is owner
    fn require_owner(&self) {
        assert_eq!(caller(), self.owner.get(), "Only owner can call this");
    }
}

// Events
#[odra::type]
pub struct OracleDataPosted {
    pub asset_id: String,
    pub price: U256,
    pub confidence: u8,
    pub timestamp: u64,
    pub agent: Key,
}

#[odra::type]
pub struct ReputationSlashed {
    pub agent: Key,
    pub penalty: u8,
    pub new_score: u8,
}
