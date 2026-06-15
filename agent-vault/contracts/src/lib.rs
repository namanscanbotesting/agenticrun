//! AgentVault Smart Contracts for Casper Network
//! 
//! This library contains all smart contracts for the AgentVault system:
//! - PortfolioManager: Main vault operations and yield optimization
//! - RWARegistry: Real World Asset token registry and metadata
//! - AgentReputation: Track AI agent performance and trust scores

#![no_std]
#![no_main]

mod portfolio_manager;
mod rwa_registry;
mod agent_reputation;

pub use portfolio_manager::PortfolioManager;
pub use rwa_registry::RWARegistry;
pub use agent_reputation::AgentReputation;
