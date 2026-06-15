"""
CasperMind - Governor Agent
Analyzes DAO proposals, models impact, casts votes, executes treasury actions.
Pays Oracle Agent for RWA data before voting on relevant proposals.
"""

import os
import time
import hashlib
import json
from typing import Optional, Dict, Any, List
import requests
from dotenv import load_dotenv

load_dotenv()

class GovernorAgent:
    """Autonomous DAO Governance Agent."""
    
    def __init__(self):
        self.agent_name = "Governor-Agent-Delta"
        self.private_key = os.getenv("GOVERNOR_AGENT_PRIVATE_KEY")
        self.casper_rpc_url = os.getenv("CASPER_RPC_URL", "https://testnet.casper.network/rpc")
        
        # Oracle Agent endpoint (x402 gated)
        self.oracle_endpoint = os.getenv("ORACLE_AGENT_ENDPOINT", "http://localhost:8001/oracle")
        self.oracle_payment_address = os.getenv("ORACLE_PAYMENT_ADDRESS")
        self.price_per_oracle_request = 1000000  # 0.001 CSPR in motes
        
        # Governance configuration
        self.auto_vote_enabled = True
        self.min_confidence_threshold = 80  # Only auto-vote if confidence > 80%
        self.treasury_address = os.getenv("DAO_TREASURY_ADDRESS", "")
        
        # Simulated DAO proposals
        self.active_proposals = [
            {
                "id": 1,
                "title": "Increase staking rewards to 12%",
                "description": "Proposal to increase CSPR staking APY from 8% to 12%",
                "type": "parameter_change",
                "impact_area": "staking",
                "treasury_impact": -500000,  # CSPR per year
                "status": "active"
            },
            {
                "id": 2,
                "title": "Partner with RealEstate DAO for tokenized properties",
                "description": "Strategic partnership to bring RWA properties on-chain",
                "type": "partnership",
                "impact_area": "rwa",
                "treasury_impact": -100000,  # One-time cost
                "status": "active"
            }
        ]
        
        # Voting history
        self.voting_history = []
    
    def fetch_dao_proposals(self) -> List[Dict[str, Any]]:
        """Fetch active DAO proposals via MCP or direct query."""
        print("[Governor] Fetching active DAO proposals...")
        
        # In production: Query Casper DAO governance MCP server
        # For demo: Return simulated proposals
        return self.active_proposals
    
    def request_oracle_data_for_proposal(self, proposal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Request relevant RWA data from Oracle Agent if proposal affects RWA."""
        if proposal.get("impact_area") != "rwa":
            return None
        
        print(f"[Governor] Requesting RWA data for proposal {proposal['id']} (paying x402)...")
        
        # Generate payment proof
        payment_proof = self.generate_x402_payment(
            amount=self.price_per_oracle_request,
            recipient=self.oracle_payment_address
        )
        
        # Make request
        payload = {
            "asset_id": "real-estate-index",  # Relevant asset for this proposal
            "payment_proof": payment_proof
        }
        
        try:
            response = requests.post(self.oracle_endpoint, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"[Governor] RWA context received")
                    return result.get("data", {})
        except Exception as e:
            print(f"[Governor] Oracle request failed: {e}")
        
        return {}
    
    def generate_x402_payment(self, amount: int, recipient: str) -> str:
        """Generate x402 micropayment proof."""
        payment_data = {
            "amount": amount,
            "recipient": recipient,
            "timestamp": int(time.time()),
            "nonce": hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        }
        payment_str = json.dumps(payment_data, sort_keys=True)
        signature = hashlib.sha256(payment_str.encode()).hexdigest()
        return f"x402-proof-{signature[:32]}"
    
    def llm_proposal_analysis(
        self,
        proposal: Dict[str, Any],
        oracle_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        LLM-powered proposal analysis.
        In production: Call GPT-4o/Claude with structured prompt.
        """
        print(f"[Governor] Analyzing proposal {proposal['id']}: {proposal['title']}")
        
        # Simulated LLM reasoning
        # In production, prompt would be:
        # """
        # Analyze this DAO proposal:
        # Title: {title}
        # Description: {description}
        # Type: {type}
        # Treasury Impact: {treasury_impact} CSPR
        # 
        # RWA Market Context (if applicable): {oracle_context}
        # 
        # Provide:
        # 1. Risk assessment (LOW/MEDIUM/HIGH)
        # 2. Benefit score (0-100)
        # 3. Recommendation (FOR/AGAINST/ABSTAIN)
        # 4. Confidence level (0-100)
        # 5. Rationale
        # """
        
        # Heuristic analysis for demo
        risk_level = "MEDIUM"
        benefit_score = 65
        recommendation = "FOR"
        confidence = 75
        rationale = []
        
        # Analyze treasury impact
        if proposal["treasury_impact"] < -400000:
            risk_level = "HIGH"
            rationale.append("Large treasury impact requires caution")
            benefit_score -= 20
        elif proposal["treasury_impact"] > 0:
            rationale.append("Positive treasury impact")
            benefit_score += 15
        
        # Analyze RWA context if available
        if oracle_context:
            if oracle_context.get("risk_level") == "HIGH":
                risk_level = "HIGH"
                rationale.append("RWA market conditions unfavorable")
                benefit_score -= 25
            else:
                rationale.append("RWA market conditions supportive")
                benefit_score += 10
        
        # Adjust recommendation based on analysis
        if benefit_score < 50:
            recommendation = "AGAINST"
            confidence = 85
        elif benefit_score > 75:
            recommendation = "FOR"
            confidence = 90
        else:
            recommendation = "ABSTAIN"
            confidence = 70
        
        if not rationale:
            rationale.append("Balanced risk-reward profile")
        
        return {
            "proposal_id": proposal["id"],
            "risk_assessment": risk_level,
            "benefit_score": benefit_score,
            "recommendation": recommendation,
            "confidence": confidence,
            "rationale": "; ".join(rationale),
            "should_auto_vote": self.auto_vote_enabled and confidence >= self.min_confidence_threshold
        }
    
    def cast_vote(self, proposal_id: int, vote: str, rationale: str) -> Optional[str]:
        """Cast vote on DAO proposal via Casper blockchain."""
        print(f"[Governor] Casting {vote} vote on proposal {proposal_id}...")
        
        # In production: Use Casper SDK to call DAO governance contract
        # Example pseudo-code:
        """
        from casper.sdk import CasperSDK
        
        sdk = CasperSDK(self.casper_rpc_url)
        
        deploy = sdk.deploy(
            chain_name="casper-testnet",
            payment_amount=10000000000,
            ttl="1h",
            session_code_hash=DAO_GOVERNANCE_CONTRACT,
            entry_point="cast_vote",
            args={
                "proposal_id": proposal_id,
                "vote": vote,  # "FOR", "AGAINST", "ABSTAIN"
                "rationale": rationale
            },
            secret_key=self.private_key
        )
        
        result = sdk.put_deploy(deploy)
        return result.deploy_hash
        """
        
        # Demo: Simulate transaction
        tx_hash = "governance-vote-" + hashlib.sha256(
            f"{proposal_id}{vote}".encode()
        ).hexdigest()[:16]
        
        print(f"[Governor] Vote cast: {tx_hash}")
        
        # Record in history
        self.voting_history.append({
            "proposal_id": proposal_id,
            "vote": vote,
            "tx_hash": tx_hash,
            "timestamp": int(time.time())
        })
        
        return tx_hash
    
    def execute_treasury_action(self, proposal_id: int, action_details: Dict[str, Any]) -> Optional[str]:
        """Execute approved treasury action (multi-step transaction)."""
        print(f"[Governor] Executing treasury action for proposal {proposal_id}...")
        
        # In production: Execute multi-sig treasury transaction
        # This might involve multiple contract calls
        
        tx_hash = "treasury-exec-" + hashlib.sha256(
            f"{proposal_id}{action_details}".encode()
        ).hexdigest()[:16]
        
        print(f"[Governor] Treasury action executed: {tx_hash}")
        return tx_hash
    
    def log_action_to_identity(self, action_type: str, tx_hash: str, result: bool):
        """Log action to AgentIdentity contract."""
        print(f"[Governor] Logging action: {action_type}")
        # In production: Call AgentIdentity.record_action()
    
    def run_autonomous_cycle(self):
        """Run one complete autonomous governance cycle."""
        print("\n=== Governor Agent Cycle ===")
        
        # Step 1: Fetch active proposals
        proposals = self.fetch_dao_proposals()
        print(f"Found {len(proposals)} active proposals")
        
        decisions = []
        
        for proposal in proposals:
            # Step 2: Request Oracle data if RWA-related (pay x402)
            oracle_context = self.request_oracle_data_for_proposal(proposal)
            
            # Step 3: Run LLM analysis
            analysis = self.llm_proposal_analysis(proposal, oracle_context)
            print(f"Analysis: {analysis['recommendation']} (confidence: {analysis['confidence']}%)")
            
            # Step 4: Auto-vote if confidence threshold met
            if analysis["should_auto_vote"]:
                tx_hash = self.cast_vote(
                    proposal["id"],
                    analysis["recommendation"],
                    analysis["rationale"]
                )
                
                # Log action
                self.log_action_to_identity("CAST_GOVERNANCE_VOTE", tx_hash, True)
                
                decisions.append({
                    "proposal_id": proposal["id"],
                    "decision": analysis["recommendation"],
                    "executed": True,
                    "tx_hash": tx_hash
                })
            else:
                decisions.append({
                    "proposal_id": proposal["id"],
                    "decision": analysis["recommendation"],
                    "executed": False,
                    "reason": f"Confidence {analysis['confidence']}% < threshold {self.min_confidence_threshold}%"
                })
        
        return decisions


if __name__ == "__main__":
    # Initialize agent
    governor = GovernorAgent()
    
    # Demo: Run autonomous governance cycle
    print("=== CasperMind Governor Agent Demo ===")
    
    decisions = governor.run_autonomous_cycle()
    
    print("\n=== Voting Decisions ===")
    for decision in decisions:
        status = "✅ Executed" if decision.get("executed") else f"⏸️ Skipped ({decision.get('reason')})"
        print(f"Proposal {decision['proposal_id']}: {decision['decision']} - {status}")
    
    print(f"\nTotal votes cast: {len([d for d in decisions if d.get('executed')])}")
    print(f"Voting history: {len(governor.voting_history)} records")
