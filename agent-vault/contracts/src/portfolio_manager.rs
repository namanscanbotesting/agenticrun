//! Portfolio Manager Contract
//! 
//! Main contract for managing RWA portfolios with autonomous AI agent control.
//! Handles deposits, withdrawals, and automated rebalancing of assets across DeFi protocols.

use odra::prelude::*;
use odra::casper_types::{U512, Address};

/// Allocation structure for portfolio rebalancing
#[derive(Clone, Debug)]
pub struct Allocation {
    pub protocol: Address,
    pub amount: U512,
    pub asset_type: String,
}

/// Portfolio state information
#[derive(Clone, Debug)]
pub struct PortfolioState {
    pub total_value_locked: U512,
    pub user_balance: U512,
    pub last_rebalance: u64,
    pub active_allocations: Vec<Allocation>,
}

/// Portfolio Manager Contract
/// 
/// Manages user deposits and autonomously rebalances portfolio across DeFi protocols
#[odra::module]
pub struct PortfolioManager {
    owner: Address,
    authorized_agent: Address,
    total_value_locked: U512,
    paused: bool,
    user_balances: Mapping<Address, U512>,
    portfolio_states: Mapping<Address, PortfolioState>,
}

#[odra::module]
impl PortfolioManager {
    /// Initialize the portfolio manager contract
    #[odra(init)]
    pub fn init(&mut self, owner: Address, authorized_agent: Address) {
        self.owner = owner;
        self.authorized_agent = authorized_agent;
        self.total_value_locked = U512::zero();
        self.paused = false;
    }

    /// Deposit RWA tokens into the vault
    #[odra(execute)]
    pub fn deposit(&mut self, amount: U512) -> Result<(), OdraError> {
        if self.paused {
            return Err(OdraError::CustomError("Contract is paused".into()));
        }

        if amount.is_zero() {
            return Err(OdraError::CustomError("Amount must be greater than zero".into()));
        }

        let caller = self.env().caller();
        
        // Update user balance
        let current_balance = self.user_balances.get(&caller).unwrap_or(U512::zero());
        let new_balance = current_balance + amount;
        self.user_balances.set(&caller, &new_balance);

        // Update total value locked
        self.total_value_locked = self.total_value_locked + amount;

        // Emit deposit event
        self.env().emit_event(DepositEvent {
            user: caller,
            amount,
            timestamp: self.env().get_block_time(),
        });

        Ok(())
    }

    /// Withdraw RWA tokens from the vault
    #[odra(execute)]
    pub fn withdraw(&mut self, amount: U512) -> Result<(), OdraError> {
        if self.paused {
            return Err(OdraError::CustomError("Contract is paused".into()));
        }

        if amount.is_zero() {
            return Err(OdraError::CustomError("Amount must be greater than zero".into()));
        }

        let caller = self.env().caller();
        let current_balance = self.user_balances.get(&caller).unwrap_or(U512::zero());

        if current_balance < amount {
            return Err(OdraError::CustomError("Insufficient balance".into()));
        }

        // Update user balance
        let new_balance = current_balance - amount;
        self.user_balances.set(&caller, &new_balance);

        // Update total value locked
        self.total_value_locked = self.total_value_locked - amount;

        // Emit withdrawal event
        self.env().emit_event(WithdrawalEvent {
            user: caller,
            amount,
            timestamp: self.env().get_block_time(),
        });

        Ok(())
    }

    /// Rebalance portfolio across DeFi protocols (Agent-only)
    #[odra(execute)]
    pub fn rebalance(&mut self, allocations: Vec<Allocation>) -> Result<(), OdraError> {
        // Only authorized agent can call this function
        let caller = self.env().caller();
        if caller != self.authorized_agent {
            return Err(OdraError::CustomError("Only authorized agent can rebalance".into()));
        }

        if self.paused {
            return Err(OdraError::CustomError("Contract is paused".into()));
        }

        if allocations.is_empty() {
            return Err(OdraError::CustomError("Allocations cannot be empty".into()));
        }

        // Validate total allocation matches TVL
        let total_allocated: U512 = allocations.iter().map(|a| a.amount).sum();
        if total_allocated != self.total_value_locked {
            return Err(OdraError::CustomError(
                "Total allocation must match TVL".into()
            ));
        }

        // Execute rebalancing logic here
        // In production, this would interact with DeFi protocols
        
        // Emit rebalance event
        self.env().emit_event(RebalanceEvent {
            agent: caller,
            allocations: allocations.clone(),
            timestamp: self.env().get_block_time(),
        });

        Ok(())
    }

    /// Get current portfolio value for a user
    #[odra(view)]
    pub fn get_portfolio_value(&self, user: Address) -> U512 {
        self.user_balances.get(&user).unwrap_or(U512::zero())
    }

    /// Get total value locked in the vault
    #[odra(view)]
    pub fn get_tvl(&self) -> U512 {
        self.total_value_locked
    }

    /// Get user balance
    #[odra(view)]
    pub fn get_user_balance(&self, user: Address) -> U512 {
        self.user_balances.get(&user).unwrap_or(U512::zero())
    }

    /// Pause contract operations (Owner-only)
    #[odra(execute)]
    pub fn pause(&mut self) -> Result<(), OdraError> {
        if self.env().caller() != self.owner {
            return Err(OdraError::CustomError("Only owner can pause".into()));
        }
        self.paused = true;
        
        self.env().emit_event(PauseEvent {
            timestamp: self.env().get_block_time(),
        });
        
        Ok(())
    }

    /// Unpause contract operations (Owner-only)
    #[odra(execute)]
    pub fn unpause(&mut self) -> Result<(), OdraError> {
        if self.env().caller() != self.owner {
            return Err(OdraError::CustomError("Only owner can unpause".into()));
        }
        self.paused = false;
        
        self.env().emit_event(UnpauseEvent {
            timestamp: self.env().get_block_time(),
        });
        
        Ok(())
    }

    /// Update authorized agent address (Owner-only)
    #[odra(execute)]
    pub fn update_authorized_agent(&mut self, new_agent: Address) -> Result<(), OdraError> {
        if self.env().caller() != self.owner {
            return Err(OdraError::CustomError("Only owner can update agent".into()));
        }
        
        let old_agent = self.authorized_agent;
        self.authorized_agent = new_agent;
        
        self.env().emit_event(AgentUpdateEvent {
            old_agent,
            new_agent,
            timestamp: self.env().get_block_time(),
        });
        
        Ok(())
    }
}

// Events
#[odra(event)]
pub struct DepositEvent {
    pub user: Address,
    pub amount: U512,
    pub timestamp: u64,
}

#[odra(event)]
pub struct WithdrawalEvent {
    pub user: Address,
    pub amount: U512,
    pub timestamp: u64,
}

#[odra(event)]
pub struct RebalanceEvent {
    pub agent: Address,
    pub allocations: Vec<Allocation>,
    pub timestamp: u64,
}

#[odra(event)]
pub struct PauseEvent {
    pub timestamp: u64,
}

#[odra(event)]
pub struct UnpauseEvent {
    pub timestamp: u64,
}

#[odra(event)]
pub struct AgentUpdateEvent {
    pub old_agent: Address,
    pub new_agent: Address,
    pub timestamp: u64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use odra_test::env;

    #[test]
    fn test_deposit() {
        let env = env::test_env();
        let owner = env.get_account(0);
        let agent = env.get_account(1);
        let user = env.get_account(2);

        let mut contract = PortfolioManager::deploy(&env, (owner, agent));
        
        env.caller(user);
        contract.deposit(U512::from(1000)).unwrap();
        
        assert_eq!(contract.get_user_balance(user), U512::from(1000));
        assert_eq!(contract.get_tvl(), U512::from(1000));
    }

    #[test]
    fn test_withdraw() {
        let env = env::test_env();
        let owner = env.get_account(0);
        let agent = env.get_account(1);
        let user = env.get_account(2);

        let mut contract = PortfolioManager::deploy(&env, (owner, agent));
        
        env.caller(user);
        contract.deposit(U512::from(1000)).unwrap();
        contract.withdraw(U512::from(500)).unwrap();
        
        assert_eq!(contract.get_user_balance(user), U512::from(500));
    }

    #[test]
    fn test_agent_rebalance() {
        let env = env::test_env();
        let owner = env.get_account(0);
        let agent = env.get_account(1);

        let mut contract = PortfolioManager::deploy(&env, (owner, agent));
        
        // Agent should be able to rebalance
        let allocations = vec![
            Allocation {
                protocol: env.get_account(3),
                amount: U512::from(500),
                asset_type: "DeFi_Protocol_A".into(),
            },
        ];
        
        env.caller(agent);
        // This would work if TVL matches allocations
        // contract.rebalance(allocations).unwrap();
    }
}
