"""
Casper MCP Server - Model Context Protocol for Casper Blockchain

This MCP server provides AI agents with direct access to Casper blockchain data,
enabling autonomous querying of contract states, transaction history, and network status.

Features:
- Real-time blockchain state queries
- Contract state inspection
- Transaction history retrieval
- Network status monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BlockInfo:
    """Block information structure"""
    block_hash: str
    block_height: int
    timestamp: datetime
    transactions_count: int
    proposer: str


@dataclass
class ContractState:
    """Smart contract state information"""
    contract_address: str
    state_data: Dict[str, Any]
    last_modified: datetime
    version: int


class CasperMCPServer:
    """
    Model Context Protocol server for Casper Network interaction.
    
    This server enables AI agents to query blockchain data,
    inspect contract states, and monitor network activity.
    """
    
    def __init__(
        self,
        node_url: str = "https://testnet-api.casper.network",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Casper MCP Server.
        
        Args:
            node_url: Casper node API URL
            api_key: Optional API key for CSPR.cloud
        """
        self.node_url = node_url
        self.api_key = api_key
        self.is_connected = False
        self.cache: Dict[str, Any] = {}
        
        logger.info(f"CasperMCPServer initialized with node: {node_url}")
    
    async def connect(self) -> bool:
        """
        Establish connection to Casper node.
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Connecting to Casper node at {self.node_url}")
            
            # In production, this would establish actual connection
            # using CSPR.cloud SDK or direct HTTP client
            
            # Simulated connection for demo
            await asyncio.sleep(0.3)
            self.is_connected = True
            
            logger.info("Connected to Casper node successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    async def get_latest_block(self) -> Optional[BlockInfo]:
        """
        Get latest block information.
        
        Returns:
            BlockInfo or None if failed
        """
        try:
            if not self.is_connected:
                await self.connect()
            
            # In production: response = await self.http_client.get("/blocks/latest")
            
            # Simulated block info for demo
            block = BlockInfo(
                block_hash="0x" + "block" * 16,
                block_height=12345678,
                timestamp=datetime.now(),
                transactions_count=42,
                proposer="casper-validator-addr",
            )
            
            logger.info(f"Latest block: {block.block_height}")
            return block
            
        except Exception as e:
            logger.error(f"Failed to get latest block: {e}")
            return None
    
    async def query_contract_state(
        self, 
        contract_address: str,
        state_key: Optional[str] = None
    ) -> Optional[ContractState]:
        """
        Query smart contract state.
        
        Args:
            contract_address: Address of the contract
            state_key: Optional specific state key to query
            
        Returns:
            ContractState or None if failed
        """
        try:
            logger.info(f"Querying contract state: {contract_address[:10]}...")
            
            # In production, this would call Casper RPC endpoint
            # state = await self.rpc_client.get_contract_state(contract_address)
            
            # Simulated contract state for demo
            state_data = {
                "total_value_locked": 10000000,
                "user_count": 150,
                "last_rebalance": datetime.now().isoformat(),
                "active": True,
            }
            
            if state_key:
                state_data = {state_key: state_data.get(state_key)}
            
            contract_state = ContractState(
                contract_address=contract_address,
                state_data=state_data,
                last_modified=datetime.now(),
                version=1,
            )
            
            # Cache the result
            self.cache[f"contract:{contract_address}"] = contract_state
            
            logger.info(f"Contract state retrieved successfully")
            return contract_state
            
        except Exception as e:
            logger.error(f"Failed to query contract state: {e}")
            return None
    
    async def get_transaction_history(
        self,
        address: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history for an address.
        
        Args:
            address: Wallet or contract address
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction records
        """
        try:
            logger.info(f"Getting transaction history for {address[:10]}...")
            
            # In production: txs = await self.rpc_client.get_account_transactions(address, limit)
            
            # Simulated transactions for demo
            transactions = [
                {
                    "hash": f"0x{'tx' + str(i) * 14}",
                    "type": "transfer",
                    "amount": 1000 * (i + 1),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                }
                for i in range(limit)
            ]
            
            logger.info(f"Retrieved {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get transaction history: {e}")
            return []
    
    async def get_defi_protocols(self) -> List[Dict[str, Any]]:
        """
        Get list of DeFi protocols on Casper.
        
        Returns:
            List of protocol information
        """
        try:
            # Simulated DeFi protocols for demo
            protocols = [
                {
                    "name": "CasperSwap",
                    "address": "casper-contract-swap",
                    "tvl": 5000000,
                    "apy": 18.5,
                    "category": "DEX",
                },
                {
                    "name": "YieldFarm",
                    "address": "casper-contract-farm",
                    "tvl": 3000000,
                    "apy": 22.3,
                    "category": "Farming",
                },
                {
                    "name": "StakeVault",
                    "address": "casper-contract-stake",
                    "tvl": 8000000,
                    "apy": 12.1,
                    "category": "Staking",
                },
            ]
            
            logger.info(f"Retrieved {len(protocols)} DeFi protocols")
            return protocols
            
        except Exception as e:
            logger.error(f"Failed to get DeFi protocols: {e}")
            return []
    
    async def get_network_status(self) -> Dict[str, Any]:
        """
        Get current network status.
        
        Returns:
            Dictionary with network metrics
        """
        try:
            status = {
                "chain_name": "casper-testnet",
                "current_era": 1234,
                "block_height": 12345678,
                "tps": 150,
                "active_validators": 100,
                "gas_price": 10,
            }
            
            logger.info(f"Network status retrieved")
            return status
            
        except Exception as e:
            logger.error(f"Failed to get network status: {e}")
            return {}
    
    def clear_cache(self) -> None:
        """Clear the internal cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    async def disconnect(self) -> None:
        """Disconnect from the node"""
        self.is_connected = False
        self.clear_cache()
        logger.info("Disconnected from Casper node")


async def main():
    """Demo function to test CasperMCPServer"""
    server = CasperMCPServer(
        node_url="https://testnet-api.casper.network"
    )
    
    # Connect
    connected = await server.connect()
    print(f"Connected: {connected}")
    
    if connected:
        # Get latest block
        block = await server.get_latest_block()
        print(f"Latest block: {block.block_height if block else 'N/A'}")
        
        # Query contract state
        state = await server.query_contract_state("casper-contract-addr")
        print(f"Contract state: {state.state_data if state else 'N/A'}")
        
        # Get DeFi protocols
        protocols = await server.get_defi_protocols()
        print(f"DeFi protocols: {len(protocols)}")
        
        # Disconnect
        await server.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
