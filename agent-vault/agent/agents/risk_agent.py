"""
Risk Agent - RWA Risk Assessment using ML

This agent evaluates Real World Asset risks using machine learning models,
scrapes off-chain data sources, and posts verified risk scores on-chain.

Features:
- ML-powered risk scoring for RWAs (real estate, commodities, bonds)
- Off-chain data scraping and validation
- On-chain reputation tracking based on prediction accuracy
- Continuous monitoring of asset risk factors
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RiskAssessment:
    """Risk assessment result for an RWA"""
    asset_id: str
    risk_score: float  # 0-100 (higher = riskier)
    credit_rating: str
    volatility: float
    liquidity_score: float
    market_sentiment: float
    timestamp: datetime
    confidence: float


@dataclass
class AssetData:
    """Raw asset data from various sources"""
    asset_id: str
    price: float
    volume_24h: float
    market_cap: float
    historical_volatility: float
    news_sentiment: float
    macro_factors: Dict[str, float]


class RiskAgent:
    """
    Autonomous AI agent for RWA risk assessment on Casper Network.
    
    This agent uses ML models to evaluate asset risks, monitors market conditions,
    and maintains an on-chain reputation based on prediction accuracy.
    """
    
    def __init__(
        self,
        mcp_server_url: str,
        model_path: Optional[str] = None,
        update_interval: int = 600,  # 10 minutes
        risk_threshold: float = 70.0,  # Alert threshold
    ):
        """
        Initialize the Risk Agent.
        
        Args:
            mcp_server_url: URL of the Casper MCP server
            model_path: Path to pre-trained ML model
            update_interval: Seconds between risk assessments
            risk_threshold: Risk score threshold for alerts
        """
        self.mcp_server_url = mcp_server_url
        self.model_path = model_path
        self.update_interval = update_interval
        self.risk_threshold = risk_threshold
        
        self.is_running = False
        self.assessments: Dict[str, RiskAssessment] = {}
        self.prediction_history: List[Dict] = []
        self.accuracy_rate: float = 0.0
        
        # Load ML model (would be actual model in production)
        self.ml_model = self._load_model()
        
        logger.info(f"RiskAgent initialized with threshold: {risk_threshold}")
    
    def _load_model(self) -> Any:
        """
        Load pre-trained ML model for risk assessment.
        
        In production, this would load a scikit-learn or PyTorch model
        trained on historical RWA performance data.
        """
        logger.info("Loading ML risk assessment model...")
        
        # Simulated model for demo
        # In production: import joblib; model = joblib.load(self.model_path)
        model = {"loaded": True, "type": "RandomForestClassifier"}
        
        logger.info(f"Model loaded: {model}")
        return model
    
    async def scrape_asset_data(self, asset_id: str) -> Optional[AssetData]:
        """
        Scrape off-chain data for asset analysis.
        
        Args:
            asset_id: Identifier for the RWA
            
        Returns:
            AssetData object with scraped information
        """
        try:
            logger.info(f"Scraping data for asset: {asset_id}")
            
            # In production, this would:
            # - Query price oracles
            # - Scrape news sources for sentiment
            # - Pull macroeconomic indicators
            # - Access traditional finance APIs
            
            # Simulated data for demo
            simulated_data = AssetData(
                asset_id=asset_id,
                price=150.25,
                volume_24h=1000000,
                market_cap=50000000,
                historical_volatility=0.15,
                news_sentiment=0.65,
                macro_factors={
                    "interest_rate": 0.05,
                    "inflation": 0.03,
                    "gdp_growth": 0.025,
                }
            )
            
            logger.info(f"Successfully scraped data for {asset_id}")
            return simulated_data
            
        except Exception as e:
            logger.error(f"Error scraping data for {asset_id}: {e}")
            return None
    
    def assess_risk(self, asset_data: AssetData) -> RiskAssessment:
        """
        Evaluate asset risk using ML model.
        
        Args:
            asset_data: Raw asset data for analysis
            
        Returns:
            RiskAssessment with scored risk metrics
        """
        try:
            # Extract features for ML model
            features = self._extract_features(asset_data)
            
            # Make prediction (simulated for demo)
            # In production: risk_score = self.ml_model.predict([features])[0]
            risk_score = self._calculate_risk_score(features)
            
            # Determine credit rating based on risk score
            credit_rating = self._get_credit_rating(risk_score)
            
            assessment = RiskAssessment(
                asset_id=asset_data.asset_id,
                risk_score=risk_score,
                credit_rating=credit_rating,
                volatility=asset_data.historical_volatility,
                liquidity_score=self._calculate_liquidity(asset_data),
                market_sentiment=asset_data.news_sentiment,
                timestamp=datetime.now(),
                confidence=0.88,  # Model confidence
            )
            
            self.assessments[asset_data.asset_id] = assessment
            logger.info(
                f"Risk assessment for {asset_data.asset_id}: "
                f"Score={risk_score:.2f}, Rating={credit_rating}"
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            raise
    
    def _extract_features(self, asset_data: AssetData) -> List[float]:
        """Extract numerical features for ML model"""
        return [
            asset_data.price,
            asset_data.volume_24h / 1000000,  # Normalize
            asset_data.market_cap / 10000000,  # Normalize
            asset_data.historical_volatility,
            asset_data.news_sentiment,
            asset_data.macro_factors.get("interest_rate", 0),
            asset_data.macro_factors.get("inflation", 0),
        ]
    
    def _calculate_risk_score(self, features: List[float]) -> float:
        """
        Calculate risk score from features.
        
        In production, this would use the trained ML model.
        Here we use a simplified formula for demo.
        """
        # Simplified risk calculation for demo
        volatility_risk = features[3] * 100  # Historical volatility
        sentiment_risk = (1 - features[4]) * 50  # Inverse of sentiment
        macro_risk = (features[5] + features[6]) * 200  # Interest + inflation
        
        risk_score = min(100, volatility_risk + sentiment_risk + macro_risk)
        return max(0, risk_score)  # Ensure non-negative
    
    def _get_credit_rating(self, risk_score: float) -> str:
        """Convert risk score to credit rating"""
        if risk_score <= 20:
            return "AAA"
        elif risk_score <= 35:
            return "AA"
        elif risk_score <= 50:
            return "A"
        elif risk_score <= 65:
            return "BBB"
        elif risk_score <= 80:
            return "BB"
        else:
            return "B"
    
    def _calculate_liquidity(self, asset_data: AssetData) -> float:
        """Calculate liquidity score from volume and market cap"""
        if asset_data.market_cap == 0:
            return 0.0
        
        volume_ratio = asset_data.volume_24h / asset_data.market_cap
        # Normalize to 0-100 scale
        return min(100, volume_ratio * 1000)
    
    async def post_risk_score_onchain(self, assessment: RiskAssessment) -> str:
        """
        Post verified risk score to Casper blockchain.
        
        Args:
            assessment: RiskAssessment to post
            
        Returns:
            Transaction hash
        """
        try:
            logger.info(
                f"Posting risk score {assessment.risk_score:.2f} "
                f"for {assessment.asset_id} on-chain"
            )
            
            # In production, this would:
            # 1. Use x402 to pay for transaction
            # 2. Call RWARegistry contract via Agent Skill
            # 3. Submit signed transaction
            
            # Simulated transaction for demo
            await asyncio.sleep(0.5)
            tx_hash = "0x" + "risk" * 16
            
            logger.info(f"Risk score posted on-chain: {tx_hash[:10]}...")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Failed to post risk score: {e}")
            raise
    
    async def monitor_assets(self, asset_ids: List[str]) -> None:
        """
        Main monitoring loop for continuous risk assessment.
        
        Args:
            asset_ids: List of asset IDs to monitor
        """
        logger.info(f"Starting risk monitoring for {len(asset_ids)} assets...")
        self.is_running = True
        
        while self.is_running:
            try:
                for asset_id in asset_ids:
                    # Scrape latest data
                    asset_data = await self.scrape_asset_data(asset_id)
                    
                    if asset_data:
                        # Assess risk
                        assessment = self.assess_risk(asset_data)
                        
                        # Check if risk exceeds threshold
                        if assessment.risk_score >= self.risk_threshold:
                            logger.warning(
                                f"HIGH RISK ALERT: {asset_id} "
                                f"score={assessment.risk_score:.2f}"
                            )
                        
                        # Post on-chain
                        await self.post_risk_score_onchain(assessment)
                
                # Wait for next update cycle
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    def stop(self) -> None:
        """Stop the monitoring loop"""
        self.is_running = False
        logger.info("RiskAgent stopped")
    
    def get_accuracy_stats(self) -> Dict[str, Any]:
        """Get prediction accuracy statistics"""
        return {
            "total_predictions": len(self.prediction_history),
            "accuracy_rate": self.accuracy_rate,
            "current_assessments": len(self.assessments),
        }


async def main():
    """Demo function to test RiskAgent"""
    agent = RiskAgent(
        mcp_server_url="http://localhost:8080/mcp",
        risk_threshold=70.0,
    )
    
    # Monitor sample assets
    asset_ids = ["RWA-001", "RWA-002", "RWA-003"]
    
    try:
        await agent.monitor_assets(asset_ids)
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
