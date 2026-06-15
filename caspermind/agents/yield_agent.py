"""
CasperMind - Yield Router Agent
Monitors DeFi yields, requests oracle data (via x402), rebalances portfolio autonomously.
"""

import os
import time
import hashlib
import json
from typing import Optional, Dict, Any, List
import requests
from dotenv import load_dotenv

load_dotenv()

class YieldRouterAgent:
    """Autonomous Yield Optimization Agent."""
    
    def __init__(self):
        self.agent_name = "Yield-Router-Beta"
        self.private_key = os.getenv("YIELD_AGENT_PRIVATE_KEY")
        self.casper_rpc_url = os.getenv("CASPER_RPC_URL", "https://testnet.casper.network/rpc")
        
        # Oracle Agent endpoint (x402 gated)
        self.oracle_endpoint = os.getenv("ORACLE_AGENT_ENDPOINT", "http://localhost:8001/oracle")
        self.oracle_payment_address = os.getenv("ORACLE_PAYMENT_ADDRESS")
        self.price_per_oracle_request = 1000000  # 0.001 CSPR in motes
        
        # User configuration
        self.risk_tolerance = "moderate"  # conservative, moderate, aggressive
        self.min_yield_delta = 0.5  # Minimum APY improvement to trigger rebalance
        self.max_single_asset_exposure = 0.4  # 40% cap
        
        # Simulated DeFi protocols on Casper
        self.defi_protocols = [
            {"name": "CasperSwap", "apy": 8.5, "tvl": 5000000},
            {"name": "DefiLand", "apy": 12.3, "tvl": 2000000},
            {"name": "YieldWise", "apy": 6.8, "tvl": 8000000},
        ]
        
        # Current portfolio (simulated)
        self.portfolio = {
            "CasperSwap": 0.5,
            "DefiLand": 0.3,
            "YieldWise": 0.2
        }
    
    def query_mcp_defi_states(self) -> List[Dict[str, Any]]:
        """Query DeFi protocol states via Casper MCP Server."""
        print("[Yield] Querying MCP for DeFi states...")
        
        # In production: Use @modelcontextprotocol/sdk to query Casper MCP
        # For demo: Return simulated data with random APY fluctuations
        import random
        
        updated_protocols = []
        for protocol in self.defi_protocols:
            # Simulate APY change
            apy_change = random.uniform(-1.5, 1.5)
            new_apy = max(0, protocol["apy"] + apy_change)
            
            updated_protocols.append({
                "name": protocol["name"],
                "apy": round(new_apy, 2),
                "tvl": protocol["tvl"],
                "risk_score": random.randint(1, 10)
            })
        
        return updated_protocols
    
    def request_oracle_data(self, asset_id: str) -> Dict[str, Any]:
        """Request fresh RWA data from Oracle Agent (pays x402)."""
        print(f"[Yield] Requesting oracle data for {asset_id} (paying x402)...")
        
        # Generate payment proof (simplified)
        payment_proof = self.generate_x402_payment(
            amount=self.price_per_oracle_request,
            recipient=self.oracle_payment_address
        )
        
        # Make HTTP request with payment proof
        payload = {
            "asset_id": asset_id,
            "payment_proof": payment_proof
        }
        
        try:
            response = requests.post(self.oracle_endpoint, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"[Yield] Oracle data received, payment accepted")
                    return result.get("data", {})
                else:
                    print(f"[Yield] Oracle error: {result}")
            else:
                print(f"[Yield] HTTP error: {response.status_code}")
        except Exception as e:
            print(f"[Yield] Oracle request failed: {e}")
        
        return {}
    
    def generate_x402_payment(self, amount: int, recipient: str) -> str:
        """Generate x402 micropayment proof."""
        # In production: Use casper-x402 SDK to create cryptographic proof
        # For demo: Create signed payment hash
        payment_data = {
            "amount": amount,
            "recipient": recipient,
            "timestamp": int(time.time()),
            "nonce": hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        }
        payment_str = json.dumps(payment_data, sort_keys=True)
        signature = hashlib.sha256(payment_str.encode()).hexdigest()
        return f"x402-proof-{signature[:32]}"
    
    def llm_decision_engine(
        self,
        defi_states: List[Dict[str, Any]],
        oracle_data: Dict[str, Any],
        current_portfolio: Dict[str, float]
    ) -> Dict[str, Any]:
        """LLM-powered decision engine for portfolio rebalancing."""
        print("[Yield] Running LLM decision engine...")
        
        # In production: Call GPT-4o/Claude with structured prompt
        # Example prompt:
        # """
        # Given these DeFi yields: {defi_states}
        # And this RWA market context: {oracle_data}
        # With user risk tolerance: {risk_tolerance}
        # Current portfolio: {current_portfolio}
        # 
        # Recommend optimal allocation. Only rebalance if yield delta > {min_yield_delta}%
        # """
        
        # For demo: Use heuristic rules
        
        # Find best yield opportunity
        best_protocol = max(defi_states, key=lambda x: x["apy"])
        worst_protocol = min(current_portfolio.items(), key=lambda x: x[1])
        
        # Calculate potential improvement
        current_avg_apy = sum(
            p["apy"] * current_portfolio.get(p["name"], 0) 
            for p in defi_states
        )
        
        # Find current APY of the protocol we'd reduce
        worst_apy = next(
            (p["apy"] for p in defi_states if p["name"] == worst_protocol[0]),
            0
        )
        
        potential_improvement = best_protocol["apy"] - worst_apy
        
        # Decision logic
        should_rebalance = potential_improvement > self.min_yield_delta
        
        recommendation = {
            "action": "REBALANCE" if should_rebalance else "HOLD",
            "reasoning": f"Potential improvement: {potential_improvement:.2f}% vs threshold {self.min_yield_delta}%",
            "current_avg_apy": round(current_avg_apy, 2),
            "best_opportunity": {
                "protocol": best_protocol["name"],
                "apy": best_protocol["apy"]
            },
            "suggested_changes": []
        }
        
        if should_rebalance:
            # Suggest moving 15% from worst to best
            move_amount = min(0.15, current_portfolio.get(worst_protocol[0], 0))
            recommendation["suggested_changes"].append({
                "from": worst_protocol[0],
                "to": best_protocol["name"],
                "amount": move_amount,
                "expected_gain": round(potential_improvement * move_amount, 3)
            })
        
        return recommendation
    
    def execute_rebalance(self, changes: List[Dict[str, Any]]) -> Optional[str]:
        """Execute portfolio rebalance transactions on Casper."""
        print("[Yield] Executing rebalance transactions...")
        
        # In production: Use CSPR.click skill or Casper SDK to sign/execute
        # Example pseudo-code:
        """
        from casper.sdk import CasperSDK
        
        sdk = CasperSDK(self.casper_rpc_url)
        
        for change in changes:
            # Withdraw from source protocol
            withdraw_deploy = sdk.deploy(
                chain_name="casper-testnet",
                entry_point="withdraw",
                session_code_hash=change["from_contract"],
                args={"amount": change["amount"]},
                secret_key=self.private_key
            )
            sdk.put_deploy(withdraw_deploy)
            
            # Deposit to target protocol
            deposit_deploy = sdk.deploy(
                chain_name="casper-testnet",
                entry_point="deposit",
                session_code_hash=change["to_contract"],
                args={"amount": change["amount"]},
                secret_key=self.private_key
            )
            sdk.put_deploy(deposit_deploy)
        """
        
        # Demo: Simulate successful transaction
        tx_hash = "rebalance-tx-" + hashlib.sha256(
            json.dumps(changes).encode()
        ).hexdigest()[:16]
        
        print(f"[Yield] Rebalance executed: {tx_hash}")
        return tx_hash
    
    def log_action_to_identity(self, action_type: str, tx_hash: str, result: bool):
        """Log action to AgentIdentity contract."""
        print(f"[Yield] Logging action to AgentIdentity: {action_type}")
        # In production: Call AgentIdentity.record_action()
    
    def run_autonomous_cycle(self):
        """Run one complete autonomous cycle."""
        print("\n=== Yield Router Agent Cycle ===")
        
        # Step 1: Query DeFi states via MCP
        defi_states = self.query_mcp_defi_states()
        print(f"DeFi states: {[(p['name'], p['apy']) for p in defi_states]}")
        
        # Step 2: Request oracle data (pay x402)
        oracle_data = self.request_oracle_data("bitcoin")
        if oracle_data:
            print(f"Oracle data: price={oracle_data.get('price')}, confidence={oracle_data.get('confidence')}")
        
        # Step 3: Run LLM decision engine
        decision = self.llm_decision_engine(defi_states, oracle_data, self.portfolio)
        print(f"Decision: {decision['action']} - {decision['reasoning']}")
        
        # Step 4: Execute if rebalance recommended
        if decision["action"] == "REBALANCE" and decision["suggested_changes"]:
            tx_hash = self.execute_rebalance(decision["suggested_changes"])
            
            # Log action
            self.log_action_to_identity("REBALANCE_PORTFOLIO", tx_hash, True)
            
            # Update simulated portfolio
            for change in decision["suggested_changes"]:
                self.portfolio[change["from"]] = self.portfolio.get(change["from"], 0) - change["amount"]
                self.portfolio[change["to"]] = self.portfolio.get(change["to"], 0) + change["amount"]
            
            print(f"New portfolio: {self.portfolio}")
        else:
            print("No rebalance needed")
        
        return decision


if __name__ == "__main__":
    # Initialize agent
    yield_agent = YieldRouterAgent()
    
    # Run autonomous cycle
    result = yield_agent.run_autonomous_cycle()
    
    print("\n=== Final Decision ===")
    print(json.dumps(result, indent=2))
