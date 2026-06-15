//! Agent Reputation Contract
//! 
//! Tracks AI agent performance, decision history, and trust scores.
//! Enables transparent verification of autonomous agent reliability on-chain.

use odra::prelude::*;
use odra::casper_types::{U512, Address};

/// Agent statistics and reputation data
#[derive(Clone, Debug)]
pub struct AgentStats {
    pub total_decisions: u64,
    pub successful_decisions: u64,
    pub failed_decisions: u64,
    pub total_value_managed: U512,
    pub reputation_score: U256,
    pub last_activity: u64,
    pub created_at: u64,
}

/// Decision record for audit trail
#[derive(Clone, Debug)]
pub struct DecisionRecord {
    pub id: U512,
    pub agent: Address,
    pub decision_type: String,
    pub outcome: i32,  // -100 to 100 (negative = loss, positive = gain)
    pub timestamp: u64,
    pub transaction_hash: String,
}

/// Agent Reputation Contract
/// 
/// Maintains on-chain reputation scores for AI agents based on historical performance
#[odra::module]
pub struct AgentReputation {
    owner: Address,
    next_record_id: U512,
    agents: Mapping<Address, AgentStats>,
    decision_history: Mapping<U512, DecisionRecord>,
    agent_decision_count: Mapping<Address, Vec<U512>>,
}

#[odra::module]
impl AgentReputation {
    /// Initialize the agent reputation contract
    #[odra(init)]
    pub fn init(&mut self, owner: Address) {
        self.owner = owner;
        self.next_record_id = U512::one();
    }

    /// Record a decision made by an AI agent
    #[odra(execute)]
    pub fn record_decision(
        &mut self,
        agent: Address,
        decision_type: String,
        outcome: i32,
        transaction_hash: String,
    ) -> Result<U512, OdraError> {
        // Validate outcome range (-100 to 100)
        if outcome < -100 || outcome > 100 {
            return Err(OdraError::CustomError(
                "Outcome must be between -100 and 100".into()
            ));
        }

        let record_id = self.next_record_id;
        self.next_record_id = self.next_record_id + U512::one();

        let current_time = self.env().get_block_time();

        // Create decision record
        let record = DecisionRecord {
            id: record_id,
            agent,
            decision_type: decision_type.clone(),
            outcome,
            timestamp: current_time,
            transaction_hash,
        };

        self.decision_history.set(&record_id, &record);

        // Update agent stats
        let mut stats = self.agents.get(&agent).unwrap_or_else(|| AgentStats {
            total_decisions: 0,
            successful_decisions: 0,
            failed_decisions: 0,
            total_value_managed: U512::zero(),
            reputation_score: U256::from(50),  // Start with neutral score (0-100 scale)
            last_activity: 0,
            created_at: current_time,
        });

        stats.total_decisions += 1;
        stats.last_activity = current_time;

        // Update success/failure counts based on outcome
        if outcome >= 0 {
            stats.successful_decisions += 1;
        } else {
            stats.failed_decisions += 1;
        }

        // Calculate new reputation score using weighted average
        let success_rate = if stats.total_decisions > 0 {
            (stats.successful_decisions as f64 / stats.total_decisions as f64) * 100.0
        } else {
            50.0
        };

        // Weight recent decisions more heavily
        let avg_outcome = self.calculate_average_outcome(agent)?;
        let weighted_score = (success_rate * 0.7) + ((avg_outcome + 100.0) / 2.0 * 0.3);
        
        stats.reputation_score = U256::from(weighted_score as u64);

        self.agents.set(&agent, &stats);

        // Add to agent's decision list
        let mut decision_ids = self.agent_decision_count.get(&agent).unwrap_or_default();
        decision_ids.push(record_id);
        self.agent_decision_count.set(&agent, &decision_ids);

        // Emit event
        self.env().emit_event(DecisionRecordedEvent {
            record_id,
            agent,
            decision_type,
            outcome,
            new_reputation: stats.reputation_score,
            timestamp: current_time,
        });

        Ok(record_id)
    }

    /// Get current reputation score for an agent
    #[odra(view)]
    pub fn get_reputation(&self, agent: Address) -> U256 {
        self.agents
            .get(&agent)
            .map(|s| s.reputation_score)
            .unwrap_or(U256::from(50))  // Default neutral score for unknown agents
    }

    /// Get full agent statistics
    #[odra(view)]
    pub fn get_agent_stats(&self, agent: Address) -> Option<AgentStats> {
        self.agents.get(&agent)
    }

    /// Get decision record by ID
    #[odra(view)]
    pub fn get_decision_record(&self, record_id: U512) -> Option<DecisionRecord> {
        self.decision_history.get(&record_id)
    }

    /// Get all decision records for an agent
    #[odra(view)]
    pub fn get_agent_decisions(&self, agent: Address) -> Vec<U512> {
        self.agent_decision_count.get(&agent).unwrap_or_default()
    }

    /// Get total number of recorded decisions
    #[odra(view)]
    pub fn get_total_decisions(&self) -> U512 {
        self.next_record_id - U512::one()
    }

    /// Verify if agent meets minimum reputation threshold
    #[odra(view)]
    pub fn verify_agent_threshold(&self, agent: Address, min_score: U256) -> bool {
        self.get_reputation(agent) >= min_score
    }

    /// Helper function to calculate average outcome for an agent
    fn calculate_average_outcome(&self, agent: Address) -> Result<f64, OdraError> {
        let decision_ids = self.agent_decision_count.get(&agent).unwrap_or_default();
        
        if decision_ids.is_empty() {
            return Ok(0.0);
        }

        let mut total_outcome: f64 = 0.0;
        let mut count: u64 = 0;

        for record_id in decision_ids {
            if let Some(record) = self.decision_history.get(&record_id) {
                total_outcome += record.outcome as f64;
                count += 1;
            }
        }

        if count == 0 {
            return Ok(0.0);
        }

        Ok(total_outcome / count as f64)
    }
}

// Events
#[odra(event)]
pub struct DecisionRecordedEvent {
    pub record_id: U512,
    pub agent: Address,
    pub decision_type: String,
    pub outcome: i32,
    pub new_reputation: U256,
    pub timestamp: u64,
}

#[odra(event)]
pub struct AgentRegisteredEvent {
    pub agent: Address,
    pub initial_reputation: U256,
    pub timestamp: u64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use odra_test::env;

    #[test]
    fn test_record_decision() {
        let env = env::test_env();
        let owner = env.get_account(0);
        let agent = env.get_account(1);

        let mut contract = AgentReputation::deploy(&env, owner);
        
        contract.record_decision(
            agent,
            "Portfolio Rebalance".into(),
            85,  // Positive outcome
            "0xabc123...".into(),
        ).unwrap();
        
        let stats = contract.get_agent_stats(agent).unwrap();
        assert_eq!(stats.total_decisions, 1);
        assert_eq!(stats.successful_decisions, 1);
        assert_eq!(stats.failed_decisions, 0);
    }

    #[test]
    fn test_reputation_calculation() {
        let env = env::test_env();
        let owner = env.get_account(0);
        let agent = env.get_account(1);

        let mut contract = AgentReputation::deploy(&env, owner);
        
        // Record multiple decisions with varying outcomes
        contract.record_decision(agent, "Trade 1".into(), 90, "0x1".into()).unwrap();
        contract.record_decision(agent, "Trade 2".into(), 75, "0x2".into()).unwrap();
        contract.record_decision(agent, "Trade 3".into(), -30, "0x3".into()).unwrap();
        
        let stats = contract.get_agent_stats(agent).unwrap();
        assert_eq!(stats.total_decisions, 3);
        assert_eq!(stats.successful_decisions, 2);
        assert_eq!(stats.failed_decisions, 1);
        
        // Reputation should reflect mixed performance
        let reputation = contract.get_reputation(agent);
        assert!(reputation > U256::zero());
    }

    #[test]
    fn test_threshold_verification() {
        let env = env::test_env();
        let owner = env.get_account(0);
        let good_agent = env.get_account(1);
        let unknown_agent = env.get_account(2);

        let mut contract = AgentReputation::deploy(&env, owner);
        
        // Good agent with positive decisions
        contract.record_decision(good_agent, "Good Trade".into(), 95, "0xgood".into()).unwrap();
        
        // Should pass threshold
        assert!(contract.verify_agent_threshold(good_agent, U256::from(50)));
        
        // Unknown agent should have default score of 50
        assert!(contract.verify_agent_threshold(unknown_agent, U256::from(50)));
        assert!(!contract.verify_agent_threshold(unknown_agent, U256::from(60)));
    }
}
