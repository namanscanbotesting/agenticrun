"""
Execution Agent - Autonomous Transaction Signing and Execution

This agent handles wallet management, transaction signing via Casper Agent Skills,
and autonomous execution of DeFi operations on the Casper Network.

Features:
- Secure wallet connection via CSPR.click
- x402 micropayment handling for transactions
- Multi-signature support for high-value operations
- Transaction retry and gas optimization
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
class TransactionRequest:
    """Transaction request structure"""
    contract_address: str
    method: str
    args: Dict[str, Any]
    amount: int
    priority: str  # LOW, MEDIUM, HIGH


@dataclass
class TransactionResult:
    """Transaction execution result"""
    tx_hash: str
    status: str  # PENDING, SUCCESS, FAILED
    block_height: Optional[int]
    timestamp: datetime
    gas_used: int
    error_message: Optional[str]


class ExecutionAgent:
    """
    Autonomous AI agent for transaction execution on Casper Network.
    
    This agent manages wallet connections, signs transactions using
    CSPR.click Agent Skills, and executes DeFi operations autonomously.
    """
    
    def __init__(
        self,
        mcp_server_url: str,
        agent_skill_config: Dict[str, Any],
        x402_enabled: bool = True,
        max_gas_price: int = 100,
        retry_attempts: int = 3,
    ):
        """
        Initialize the Execution Agent.
        
        Args:
            mcp_server_url: URL of the Casper MCP server
            agent_skill_config: Configuration for CSPR.click Agent Skill
            x402_enabled: Enable x402 micropayments
            max_gas_price: Maximum acceptable gas price
            retry_attempts: Number of retry attempts for failed transactions
        """
        self.mcp_server_url = mcp_server_url
        self.agent_skill_config = agent_skill_config
        self.x402_enabled = x402_enabled
        self.max_gas_price = max_gas_price
        self.retry_attempts = retry_attempts
        
        self.is_running = False
        self.wallet_connected = False
        self.transaction_history: List[TransactionResult] = []
        self.pending_transactions: List[TransactionRequest] = []
        
        logger.info(f"ExecutionAgent initialized")
    
    async def connect_wallet(self) -> bool:
        """
        Connect wallet using CSPR.click Agent Skill.
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info("Connecting wallet via CSPR.click Agent Skill...")
            
            # In production, this would use the actual CSPR.click SDK
            # from casper_agent_skills import connect_wallet
            
            # Simulated connection for demo
            await asyncio.sleep(0.5)
            self.wallet_connected = True
            
            logger.info("Wallet connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect wallet: {e}")
            return False
    
    async def sign_transaction(self, tx_request: TransactionRequest) -> str:
        """
        Sign transaction using Agent Skill.
        
        Args:
            tx_request: TransactionRequest to sign
            
        Returns:
            Signed transaction hash
        """
        try:
            if not self.wallet_connected:
                raise RuntimeError("Wallet not connected")
            
            logger.info(f"Signing transaction for method: {tx_request.method}")
            
            # In production, this would:
            # 1. Prepare transaction payload
            # 2. Use CSPR.click to sign
            # 3. Return signed transaction
            
            # Simulated signing for demo
            await asyncio.sleep(0.3)
            signed_tx = "0x" + "signed" * 16
            
            logger.info(f"Transaction signed: {signed_tx[:10]}...")
            return signed_tx
            
        except Exception as e:
            logger.error(f"Failed to sign transaction: {e}")
            raise
    
    async def pay_with_x402(self, amount: int) -> bool:
        """
        Process x402 micropayment for transaction.
        
        Args:
            amount: Payment amount in mote
            
        Returns:
            True if payment successful
        """
        if not self.x402_enabled:
            logger.info("x402 payments disabled, skipping")
            return True
        
        try:
            logger.info(f"Processing x402 payment: {amount} mote")
            
            # In production, this would use x402 protocol
            # from casper_x402 import make_payment
            # await make_payment(amount)
            
            # Simulated payment for demo
            await asyncio.sleep(0.2)
            
            logger.info("x402 payment processed successfully")
            return True
            
        except Exception as e:
            logger.error(f"x402 payment failed: {e}")
            return False
    
    async def execute_transaction(
        self, 
        tx_request: TransactionRequest
    ) -> TransactionResult:
        """
        Execute a transaction with retry logic.
        
        Args:
            tx_request: TransactionRequest to execute
            
        Returns:
            TransactionResult with execution status
        """
        attempt = 0
        last_error = None
        
        while attempt < self.retry_attempts:
            try:
                logger.info(f"Executing transaction (attempt {attempt + 1})")
                
                # Step 1: Process x402 payment
                if not await self.pay_with_x402(tx_request.amount):
                    raise RuntimeError("x402 payment failed")
                
                # Step 2: Sign transaction
                signed_tx = await self.sign_transaction(tx_request)
                
                # Step 3: Submit to network
                # In production, submit via CSPR.cloud API
                await asyncio.sleep(0.5)
                
                # Create successful result
                result = TransactionResult(
                    tx_hash=signed_tx,
                    status="SUCCESS",
                    block_height=12345678,  # Simulated
                    timestamp=datetime.now(),
                    gas_used=25000,
                    error_message=None,
                )
                
                self.transaction_history.append(result)
                logger.info(f"Transaction executed successfully: {signed_tx[:10]}...")
                return result
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Transaction attempt {attempt + 1} failed: {e}")
                attempt += 1
                
                if attempt < self.retry_attempts:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # All retries failed
        result = TransactionResult(
            tx_hash="",
            status="FAILED",
            block_height=None,
            timestamp=datetime.now(),
            gas_used=0,
            error_message=last_error,
        )
        
        self.transaction_history.append(result)
        logger.error(f"Transaction failed after {self.retry_attempts} attempts")
        return result
    
    async def execute_rebalance(
        self,
        allocations: List[Dict[str, Any]]
    ) -> List[TransactionResult]:
        """
        Execute portfolio rebalancing across multiple protocols.
        
        Args:
            allocations: List of allocation decisions
            
        Returns:
            List of TransactionResults
        """
        logger.info(f"Executing rebalance with {len(allocations)} allocations")
        
        results = []
        for allocation in allocations:
            tx_request = TransactionRequest(
                contract_address=allocation.get("protocol_address"),
                method="rebalance",
                args={
                    "amount": allocation.get("amount"),
                    "target": allocation.get("target"),
                },
                amount=allocation.get("amount", 0),
                priority="HIGH",
            )
            
            result = await self.execute_transaction(tx_request)
            results.append(result)
        
        return results
    
    async def execute_compliance_update(
        self,
        user_address: str,
        compliance_status: Dict[str, Any]
    ) -> TransactionResult:
        """
        Execute compliance status update on-chain.
        
        Args:
            user_address: User's wallet address
            compliance_status: New compliance status
            
        Returns:
            TransactionResult
        """
        tx_request = TransactionRequest(
            contract_address=self.agent_skill_config.get("compliance_contract"),
            method="update_compliance",
            args={
                "user": user_address,
                "kyc_verified": compliance_status.get("kyc_verified"),
                "aml_cleared": compliance_status.get("aml_cleared"),
            },
            amount=10000,  # Gas estimate
            priority="MEDIUM",
        )
        
        return await self.execute_transaction(tx_request)
    
    def get_transaction_stats(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        total_txs = len(self.transaction_history)
        successful = sum(1 for t in self.transaction_history if t.status == "SUCCESS")
        failed = total_txs - successful
        
        return {
            "total_transactions": total_txs,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_txs if total_txs > 0 else 0,
            "wallet_connected": self.wallet_connected,
        }
    
    def stop(self) -> None:
        """Stop the agent"""
        self.is_running = False
        logger.info("ExecutionAgent stopped")


async def main():
    """Demo function to test ExecutionAgent"""
    agent = ExecutionAgent(
        mcp_server_url="http://localhost:8080/mcp",
        agent_skill_config={
            "wallet": "demo-wallet",
            "compliance_contract": "casper-contract-addr",
        },
        x402_enabled=True,
    )
    
    # Connect wallet
    connected = await agent.connect_wallet()
    print(f"Wallet connected: {connected}")
    
    # Execute sample transaction
    if connected:
        tx_request = TransactionRequest(
            contract_address="casper-contract-addr-1",
            method="deposit",
            args={"amount": 1000},
            amount=1000,
            priority="HIGH",
        )
        
        result = await agent.execute_transaction(tx_request)
        print(f"Transaction result: {result.status} - {result.tx_hash[:10] if result.tx_hash else 'N/A'}...")
        
        # Get stats
        stats = agent.get_transaction_stats()
        print(f"Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
