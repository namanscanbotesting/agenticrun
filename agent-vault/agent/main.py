"""
AgentVault Main Entry Point

This is the main orchestration script that coordinates all AI agents
in the AgentVault system for autonomous RWA portfolio management.
"""

import asyncio
import logging
import signal
from typing import Dict, Any

from agent.agents.yield_agent import YieldAgent
from agent.agents.risk_agent import RiskAgent
from agent.agents.compliance_agent import ComplianceAgent
from agent.agents.execution_agent import ExecutionAgent
from agent.mcp_servers.casper_mcp import CasperMCPServer
from agent.mcp_servers.data_oracle_mcp import DataOracleMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentVaultOrchestrator:
    """
    Main orchestrator for the AgentVault multi-agent system.
    
    Coordinates all AI agents to work together autonomously
    for RWA portfolio management on Casper Network.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config: Configuration dictionary with all settings
        """
        self.config = config
        self.is_running = False
        
        # Initialize MCP servers
        self.casper_mcp = CasperMCPServer(
            node_url=config.get("casper_node_url", "https://testnet-api.casper.network")
        )
        self.data_oracle = DataOracleMCP(
            api_keys=config.get("oracle_api_keys", {})
        )
        
        # Initialize AI agents
        self.yield_agent = YieldAgent(
            mcp_server_url=config.get("mcp_server_url"),
            agent_skill_config=config.get("agent_skill_config", {}),
            threshold_apr=config.get("yield_threshold_apr", 15.0),
        )
        
        self.risk_agent = RiskAgent(
            mcp_server_url=config.get("mcp_server_url"),
            risk_threshold=config.get("risk_threshold", 70.0),
        )
        
        self.compliance_agent = ComplianceAgent(
            mcp_server_url=config.get("mcp_server_url"),
            compliance_contract=config.get("compliance_contract_address"),
        )
        
        self.execution_agent = ExecutionAgent(
            mcp_server_url=config.get("mcp_server_url"),
            agent_skill_config=config.get("agent_skill_config", {}),
            x402_enabled=config.get("x402_enabled", True),
        )
        
        logger.info("AgentVault Orchestrator initialized")
    
    async def start(self):
        """Start all agents and begin autonomous operation"""
        logger.info("Starting AgentVault system...")
        self.is_running = True
        
        try:
            # Connect to MCP servers
            await self.casper_mcp.connect()
            await self.data_oracle.connect()
            
            # Connect execution agent wallet
            await self.execution_agent.connect_wallet()
            
            logger.info("All systems connected, starting autonomous operation...")
            
            # Start monitoring loops concurrently
            await asyncio.gather(
                self._run_yield_monitoring(),
                self._run_risk_monitoring(),
                self._run_compliance_monitoring(),
                return_exceptions=True,
            )
            
        except Exception as e:
            logger.error(f"System error: {e}")
            raise
        finally:
            await self.stop()
    
    async def _run_yield_monitoring(self):
        """Run yield monitoring loop"""
        logger.info("Yield monitoring started")
        while self.is_running:
            try:
                # Query DeFi protocols via MCP
                protocols = await self.casper_mcp.get_defi_protocols()
                logger.info(f"Monitored {len(protocols)} DeFi protocols")
                
                # Yield agent would analyze and potentially rebalance
                # This is simplified for demo
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Yield monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _run_risk_monitoring(self):
        """Run risk monitoring loop"""
        logger.info("Risk monitoring started")
        asset_ids = ["RWA-001", "RWA-002", "RWA-003"]
        
        while self.is_running:
            try:
                for asset_id in asset_ids:
                    # Get price data from oracle
                    price = await self.data_oracle.get_price(asset_id)
                    
                    # Get sentiment
                    sentiment = await self.data_oracle.get_sentiment(asset_id)
                    
                    # Risk agent would assess and post on-chain
                    logger.info(f"Risk check completed for {asset_id}")
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _run_compliance_monitoring(self):
        """Run compliance monitoring loop"""
        logger.info("Compliance monitoring started")
        
        while self.is_running:
            try:
                # Compliance agent would monitor transactions
                # This is simplified for demo
                stats = self.compliance_agent.get_compliance_stats()
                logger.info(f"Compliance stats: {stats}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Compliance monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop all agents and cleanup"""
        logger.info("Stopping AgentVault system...")
        self.is_running = False
        
        # Stop all agents
        self.yield_agent.stop()
        self.risk_agent.stop()
        self.compliance_agent.stop()
        self.execution_agent.stop()
        
        # Disconnect from MCP servers
        await self.casper_mcp.disconnect()
        await self.data_oracle.disconnect()
        
        logger.info("AgentVault system stopped")


def load_config() -> Dict[str, Any]:
    """Load configuration from environment or config file"""
    # In production, load from .env or config file
    return {
        "casper_node_url": "https://testnet-api.casper.network",
        "mcp_server_url": "http://localhost:8080/mcp",
        "yield_threshold_apr": 15.0,
        "risk_threshold": 70.0,
        "x402_enabled": True,
        "compliance_contract_address": "casper-contract-compliance",
        "agent_skill_config": {
            "wallet": "demo-wallet",
            "network": "testnet",
        },
        "oracle_api_keys": {},
    }


async def main():
    """Main entry point"""
    config = load_config()
    orchestrator = AgentVaultOrchestrator(config)
    
    # Setup graceful shutdown
    loop = asyncio.get_event_loop()
    
    def handle_signal():
        logger.info("Shutdown signal received")
        asyncio.create_task(orchestrator.stop())
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)
    
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())
