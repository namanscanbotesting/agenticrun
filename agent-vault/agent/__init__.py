"""
AgentVault - Autonomous AI Agents for RWA Portfolio Management

This module contains all AI agents that power the AgentVault system:
- YieldAgent: Monitors DeFi protocols and optimizes yields
- RiskAgent: Assesses RWA market risks using ML models
- ComplianceAgent: Handles KYC/AML verification
- ExecutionAgent: Signs and submits transactions autonomously
"""

from .agents.yield_agent import YieldAgent
from .agents.risk_agent import RiskAgent
from .agents.compliance_agent import ComplianceAgent
from .agents.execution_agent import ExecutionAgent
from .mcp_servers.casper_mcp import CasperMCPServer
from .mcp_servers.data_oracle_mcp import DataOracleMCP

__version__ = "0.1.0"
__all__ = [
    "YieldAgent",
    "RiskAgent", 
    "ComplianceAgent",
    "ExecutionAgent",
    "CasperMCPServer",
    "DataOracleMCP",
]
