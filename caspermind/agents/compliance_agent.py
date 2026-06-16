"""
CasperMind - Compliance Agent
Verifies user identity, issues compliance tokens, monitors for changes.
"""

import os
import time
import hashlib
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class ComplianceLevel:
    LEVEL1 = 1  # Basic KYC (name + email)
    LEVEL2 = 2  # Enhanced KYC (government ID)
    LEVEL3 = 3  # Institutional (full AML + accreditation)

class ComplianceAgent:
    """Autonomous Compliance & KYC Agent."""
    
    def __init__(self):
        self.agent_name = "Compliance-Agent-Gamma"
        self.private_key = os.getenv("COMPLIANCE_AGENT_PRIVATE_KEY")
        self.casper_rpc_url = os.getenv("CASPER_RPC_URL", "https://testnet.casper.network/rpc")
        self.contract_hash = os.getenv("COMPLIANCE_TOKEN_CONTRACT_HASH")
        
        # Compliance configuration
        self.recheck_interval_hours = 24
        self.auto_revoke_on_risk = True
        
        # Simulated user database (in production: encrypted DB)
        self.pending_verifications = []
        self.active_tokens = {}
    
    def process_verification_request(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user KYC verification request.
        In production: Use LLM to analyze documents, run risk scoring.
        """
        print(f"[Compliance] Processing verification for user...")
        
        # Simulated LLM analysis
        # In production: Call GPT-4o/Claude with document analysis prompt
        risk_score = self.calculate_risk_score(user_data)
        
        # Determine compliance level
        if risk_score < 30:
            level = ComplianceLevel.LEVEL3  # Low risk = institutional
            rationale = "Low risk profile, all documents verified"
        elif risk_score < 60:
            level = ComplianceLevel.LEVEL2  # Medium risk = enhanced
            rationale = "Moderate risk, additional verification recommended"
        else:
            level = ComplianceLevel.LEVEL1  # High risk = basic only
            rationale = "Higher risk profile, basic KYC only"
        
        # Calculate expiry (higher risk = shorter expiry)
        if level == ComplianceLevel.LEVEL3:
            expires_in_days = 365
        elif level == ComplianceLevel.LEVEL2:
            expires_in_days = 180
        else:
            expires_in_days = 90
        
        return {
            "user_address": user_data.get("address"),
            "level": level,
            "risk_score": risk_score,
            "rationale": rationale,
            "expires_at": int(time.time()) + (expires_in_days * 24 * 60 * 60),
            "recommended_action": "ISSUE_TOKEN"
        }
    
    def calculate_risk_score(self, user_data: Dict[str, Any]) -> int:
        """
        Calculate risk score (0-100) based on user data.
        In production: Use ML model + LLM reasoning.
        """
        # Simplified heuristic for demo
        score = 50  # Base score
        
        # Factors that reduce risk
        if user_data.get("government_id_verified"):
            score -= 20
        if user_data.get("proof_of_address"):
            score -= 15
        if user_data.get("source_of_funds_verified"):
            score -= 25
        
        # Factors that increase risk
        if user_data.get("high_risk_jurisdiction"):
            score += 30
        if user_data.get("pep_status"):  # Politically Exposed Person
            score += 40
        
        return max(0, min(100, score))
    
    def issue_token_on_chain(self, user_address: str, level: int, expires_at: int) -> Optional[str]:
        """Issue compliance token on Casper blockchain."""
        print(f"[Compliance] Issuing token for user {user_address[:8]}... at level {level}")
        
        # In production: Use Casper SDK to call ComplianceToken.issue_token()
        # Example pseudo-code:
        """
        from casper.sdk import CasperSDK
        
        sdk = CasperSDK(self.casper_rpc_url)
        
        deploy = sdk.deploy(
            chain_name="casper-testnet",
            payment_amount=5000000000,
            ttl="1h",
            session_code_hash=self.contract_hash,
            entry_point="issue_token",
            args={
                "user": Key.from_account_str(user_address),
                "level": {"Level" + str(level)},
                "expires_at": expires_at
            },
            secret_key=self.private_key
        )
        
        result = sdk.put_deploy(deploy)
        return result.deploy_hash
        """
        
        # Demo: Simulate successful transaction
        tx_hash = "compliance-tx-" + hashlib.sha256(
            f"{user_address}{level}{expires_at}".encode()
        ).hexdigest()[:16]
        
        print(f"[Compliance] Token issued: {tx_hash}")
        
        # Track active token
        self.active_tokens[user_address] = {
            "level": level,
            "expires_at": expires_at,
            "tx_hash": tx_hash,
            "issued_at": int(time.time())
        }
        
        return tx_hash
    
    def revoke_token(self, user_address: str, reason: str) -> Optional[str]:
        """Revoke compliance token if risk detected."""
        print(f"[Compliance] Revoking token for {user_address[:8]}... Reason: {reason}")
        
        # In production: Call ComplianceToken.revoke_token()
        
        tx_hash = "revoke-tx-" + hashlib.sha256(
            f"{user_address}{reason}".encode()
        ).hexdigest()[:16]
        
        if user_address in self.active_tokens:
            del self.active_tokens[user_address]
        
        print(f"[Compliance] Token revoked: {tx_hash}")
        return tx_hash
    
    def continuous_monitoring(self) -> List[Dict[str, Any]]:
        """
        Continuously monitor active tokens for compliance changes.
        Run every 24 hours or on trigger events.
        """
        print("[Compliance] Running continuous monitoring...")
        
        actions_taken = []
        current_time = int(time.time())
        
        for user_address, token_info in list(self.active_tokens.items()):
            # Check if expired
            if current_time >= token_info["expires_at"]:
                actions_taken.append({
                    "user": user_address,
                    "action": "EXPIRED",
                    "tx_hash": self.revoke_token(user_address, "Token expired")
                })
                continue
            
            # Simulate re-check (in production: query external risk databases)
            new_risk_score = self.simulate_risk_recheck(user_address)
            
            if new_risk_score > 80 and self.auto_revoke_on_risk:
                actions_taken.append({
                    "user": user_address,
                    "action": "REVOKED_HIGH_RISK",
                    "tx_hash": self.revoke_token(user_address, "High risk detected")
                })
            elif new_risk_score > 60 and token_info["level"] == ComplianceLevel.LEVEL3:
                # Downgrade from Level 3 to Level 2
                actions_taken.append({
                    "user": user_address,
                    "action": "DOWNGRADED",
                    "new_level": ComplianceLevel.LEVEL2
                })
        
        return actions_taken
    
    def simulate_risk_recheck(self, user_address: str) -> int:
        """Simulate risk re-check (in production: query real databases)."""
        # For demo: Return random score with slight variation
        import random
        base_score = random.randint(20, 70)
        return base_score
    
    def log_action_to_identity(self, action_type: str, tx_hash: str, result: bool):
        """Log action to AgentIdentity contract."""
        print(f"[Compliance] Logging action: {action_type}")
        # In production: Call AgentIdentity.record_action()
    
    def run_autonomous_cycle(self):
        """Run one complete autonomous monitoring cycle."""
        print("\n=== Compliance Agent Cycle ===")
        
        # Check pending verifications
        if self.pending_verifications:
            for user_data in self.pending_verifications:
                result = self.process_verification_request(user_data)
                
                if result["recommended_action"] == "ISSUE_TOKEN":
                    tx_hash = self.issue_token_on_chain(
                        result["user_address"],
                        result["level"],
                        result["expires_at"]
                    )
                    
                    self.log_action_to_identity("ISSUE_COMPLIANCE_TOKEN", tx_hash, True)
        
        # Run continuous monitoring
        actions = self.continuous_monitoring()
        
        for action in actions:
            print(f"Action taken: {action['action']} for user {action['user'][:8]}")
        
        return actions


if __name__ == "__main__":
    # Initialize agent
    compliance = ComplianceAgent()
    
    # Demo: Process sample verification requests
    print("=== CasperMind Compliance Agent Demo ===")
    
    sample_users = [
        {
            "address": "0123456789abcdef" * 2,
            "government_id_verified": True,
            "proof_of_address": True,
            "source_of_funds_verified": True,
            "high_risk_jurisdiction": False,
            "pep_status": False
        },
        {
            "address": "fedcba9876543210" * 2,
            "government_id_verified": True,
            "proof_of_address": False,
            "source_of_funds_verified": False,
            "high_risk_jurisdiction": True,
            "pep_status": False
        }
    ]
    
    # Add to pending queue
    compliance.pending_verifications = sample_users
    
    # Run cycle
    actions = compliance.run_autonomous_cycle()
    
    print(f"\nActive tokens: {len(compliance.active_tokens)}")
    print(f"Actions taken: {len(actions)}")
