"""
CasperMind - Oracle Agent
Scrapes RWA data, runs risk models, posts to Casper blockchain.
Exposes x402-gated endpoint for other agents to purchase data.
"""

import os
import time
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OracleAgent:
    """Autonomous Oracle Agent for RWA data."""
    
    def __init__(self):
        self.agent_name = "Oracle-Agent-Alpha"
        self.private_key = os.getenv("ORACLE_AGENT_PRIVATE_KEY")
        self.casper_rpc_url = os.getenv("CASPER_RPC_URL", "https://testnet.casper.network/rpc")
        self.contract_hash = os.getenv("ORACLE_REGISTRY_CONTRACT_HASH")
        self.api_key = os.getenv("COINGECKO_API_KEY", "")  # Free tier
        
        # x402 configuration
        self.price_per_request = 1000000  # 0.001 CSPR in motes
        self.payment_address = os.getenv("ORACLE_AGENT_PAYMENT_ADDRESS")
        
        # Data sources
        self.data_sources = [
            "coingecko",
            "yahoo_finance",  # Would need yfinance package
        ]
        
    def fetch_rwa_data(self, asset_id: str) -> Dict[str, Any]:
        """Fetch real-world asset data from multiple sources."""
        print(f"[Oracle] Fetching data for {asset_id}...")
        
        data_points = []
        
        # CoinGecko API (crypto-assets as proxy for RWAs)
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if asset_id in data and "usd" in data[asset_id]:
                    price = data[asset_id]["usd"]
                    data_points.append({
                        "source": "coingecko",
                        "price": price,
                        "timestamp": time.time()
                    })
        except Exception as e:
            print(f"[Oracle] CoinGecko error: {e}")
        
        # Calculate consensus price and confidence
        if not data_points:
            return {"error": "No data available"}
        
        prices = [dp["price"] for dp in data_points]
        avg_price = sum(prices) / len(prices)
        
        # Confidence based on source agreement
        if len(prices) > 1:
            variance = sum((p - avg_price) ** 2 for p in prices) / len(prices)
            confidence = max(0, 100 - int(variance * 100))
        else:
            confidence = 75  # Single source = moderate confidence
        
        return {
            "asset_id": asset_id,
            "price": int(avg_price * 1e6),  # Store as integer with precision
            "confidence": min(confidence, 100),
            "timestamp": int(time.time()),
            "sources_used": len(data_points)
        }
    
    def run_risk_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run simple risk assessment model (simulated LLM reasoning)."""
        print("[Oracle] Running risk model...")
        
        # In production, this would call GPT-4o/Claude with structured prompt
        # For demo, use heuristic rules
        
        confidence = data.get("confidence", 0)
        price = data.get("price", 0)
        
        risk_level = "LOW"
        rationale = []
        
        if confidence < 50:
            risk_level = "HIGH"
            rationale.append("Low data confidence")
        elif confidence < 75:
            risk_level = "MEDIUM"
            rationale.append("Moderate data confidence")
        
        if price == 0:
            risk_level = "CRITICAL"
            rationale.append("Invalid price data")
        
        if not rationale:
            rationale.append("All indicators normal")
        
        return {
            **data,
            "risk_level": risk_level,
            "rationale": "; ".join(rationale),
            "recommended_action": "POST" if risk_level != "CRITICAL" else "HOLD"
        }
    
    def sign_data(self, data: Dict[str, Any]) -> str:
        """Sign data payload with agent's private key."""
        # In production: Use casper-sdk to sign with private key
        # For demo: Create SHA256 hash as signature placeholder
        data_str = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(data_str.encode()).hexdigest()
        return signature
    
    def post_to_blockchain(self, data: Dict[str, Any], signature: str) -> Optional[str]:
        """Post verified data to OracleRegistry smart contract."""
        print(f"[Oracle] Posting to Casper Testnet...")
        
        # In production: Use casper-python-sdk to deploy wasm
        # Example pseudo-code:
        """
        from casper.types import Key, U256
        from casper.sdk import CasperSDK
        
        sdk = CasperSDK(self.casper_rpc_url)
        
        deploy = sdk.deploy(
            chain_name="casper-testnet",
            payment_amount=100000000,
            ttl="1h",
            entry_point="post_oracle_data",
            session_code_hash=self.contract_hash,
            args={
                "asset_id": data["asset_id"],
                "price": U256(data["price"]),
                "confidence": data["confidence"]
            },
            secret_key=self.private_key
        )
        
        result = sdk.put_deploy(deploy)
        return result.deploy_hash
        """
        
        # Demo: Simulate successful transaction
        tx_hash = "simulated-tx-" + hashlib.sha256(signature.encode()).hexdigest()[:16]
        print(f"[Oracle] Transaction posted: {tx_hash}")
        return tx_hash
    
    def x402_gated_endpoint(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        x402-gated HTTP endpoint for other agents.
        Requires payment proof before returning data.
        """
        asset_id = request.get("asset_id")
        payment_proof = request.get("payment_proof")
        
        if not payment_proof:
            return {
                "error": "Payment required",
                "x402_required": True,
                "price": self.price_per_request,
                "payment_address": self.payment_address
            }
        
        # Verify payment proof (simplified)
        # In production: Verify cryptographic proof on-chain
        if not self.verify_payment(payment_proof):
            return {"error": "Invalid payment proof"}
        
        # Fetch and return data
        data = self.fetch_rwa_data(asset_id)
        assessed_data = self.run_risk_model(data)
        signature = self.sign_data(assessed_data)
        
        return {
            "status": "success",
            "data": assessed_data,
            "signature": signature,
            "agent": self.agent_name
        }
    
    def verify_payment(self, payment_proof: str) -> bool:
        """Verify x402 payment proof."""
        # In production: Verify against Casper blockchain
        # For demo: Accept any non-empty proof
        return bool(payment_proof)
    
    def run_autonomous_loop(self, assets: list, interval_minutes: int = 15):
        """Run autonomous data posting loop."""
        print(f"[Oracle] Starting autonomous loop (interval: {interval_minutes}m)")
        
        while True:
            for asset_id in assets:
                try:
                    # Fetch data
                    data = self.fetch_rwa_data(asset_id)
                    
                    # Run risk model
                    assessed_data = self.run_risk_model(data)
                    
                    # Sign data
                    signature = self.sign_data(assessed_data)
                    
                    # Post to blockchain
                    if assessed_data.get("recommended_action") == "POST":
                        tx_hash = self.post_to_blockchain(assessed_data, signature)
                        
                        # Log action to AgentIdentity contract (pseudo-code)
                        # self.log_action_to_identity("POST_ORACLE_DATA", tx_hash, True)
                        
                except Exception as e:
                    print(f"[Oracle] Error processing {asset_id}: {e}")
            
            print(f"[Oracle] Sleeping for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    # Initialize agent
    oracle = OracleAgent()
    
    # Demo: Fetch and post data for Bitcoin (as RWA proxy)
    print("=== CasperMind Oracle Agent Demo ===")
    data = oracle.fetch_rwa_data("bitcoin")
    print(f"Fetched data: {data}")
    
    assessed = oracle.run_risk_model(data)
    print(f"Risk assessment: {assessed}")
    
    signature = oracle.sign_data(assessed)
    print(f"Signature: {signature[:32]}...")
    
    tx_hash = oracle.post_to_blockchain(assessed, signature)
    print(f"Transaction hash: {tx_hash}")
    
    print("\n=== x402 Endpoint Demo ===")
    # Simulate request without payment
    req_no_pay = {"asset_id": "bitcoin"}
    resp = oracle.x402_gated_endpoint(req_no_pay)
    print(f"Without payment: {resp}")
    
    # Simulate request with payment
    req_with_pay = {"asset_id": "bitcoin", "payment_proof": "valid-proof-123"}
    resp = oracle.x402_gated_endpoint(req_with_pay)
    print(f"With payment: Status={resp.get('status')}")
