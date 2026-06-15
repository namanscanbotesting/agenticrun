# CasperMind - Deployment Scripts

## Prerequisites
- Rust toolchain installed (`rustup`)
- Odra CLI installed (`cargo install odra-cli`)
- Casper client installed
- Testnet CSPR tokens in wallet

## Step 1: Build Smart Contracts

```bash
cd contracts/src/oracle-registry
odra build

cd ../compliance-token
odra build

cd ../agent-identity
odra build
```

This generates `.wasm` files in `target/wasm32-unknown-unknown/release/`

## Step 2: Deploy to Casper Testnet

### Deploy OracleRegistry

```bash
casper-client put-deploy \
  --chain-name casper-testnet \
  --node-address https://testnet.casper.network/rpc \
  --payment-amount 10000000000 \
  --ttl 1h \
  --secret-key /path/to/deployer_secret_key.pem \
  --session-path target/wasm32-unknown-unknown/release/oracle_registry.wasm \
  --entry-point init \
  --args challenge_window:i64:'100'
```

Save the contract hash from the response.

### Deploy ComplianceToken

```bash
casper-client put-deploy \
  --chain-name casper-testnet \
  --node-address https://testnet.casper.network/rpc \
  --payment-amount 10000000000 \
  --ttl 1h \
  --secret-key /path/to/deployer_secret_key.pem \
  --session-path target/wasm32-unknown-unknown/release/compliance_token.wasm \
  --entry-point init
```

### Deploy AgentIdentity

```bash
casper-client put-deploy \
  --chain-name casper-testnet \
  --node-address https://testnet.casper.network/rpc \
  --payment-amount 10000000000 \
  --ttl 1h \
  --secret-key /path/to/deployer_secret_key.pem \
  --session-path target/wasm32-unknown-unknown/release/agent_identity.wasm \
  --entry-point init
```

## Step 3: Update Environment Variables

Copy `.env.example` to `.env` and fill in the deployed contract hashes:

```bash
cp .env.example .env
```

Edit `.env`:
```
ORACLE_REGISTRY_CONTRACT_HASH=hash-from-step-2
COMPLIANCE_TOKEN_CONTRACT_HASH=hash-from-step-2
AGENT_IDENTITY_CONTRACT_HASH=hash-from-step-2
```

## Step 4: Register Agents on AgentIdentity Contract

```bash
# Register Oracle Agent
casper-client put-deploy \
  --chain-name casper-testnet \
  --node-address https://testnet.casper.network/rpc \
  --payment-amount 5000000000 \
  --ttl 1h \
  --secret-key /path/to/oracle_secret_key.pem \
  --session-hash <AGENT_IDENTITY_CONTRACT_HASH> \
  --entry-point register_agent \
  --args \
    agent_address:key:'<ORACLE_AGENT_PUBLIC_KEY>' \
    name:string:'Oracle-Agent-Alpha' \
    agent_type:'{Oracle}' \
    capabilities:"['fetch_rwa_data','post_oracle_data','x402_endpoint']"
```

Repeat for Yield, Compliance, and Governor agents.

## Step 5: Run Agents

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Oracle Agent (in background)
python agents/oracle_agent.py &

# Run Yield Agent
python agents/yield_agent.py
```

## Verification

Check transactions on Casper Testnet Explorer:
https://testnet.cspr.live

Verify contract state:
```bash
casper-client get-state-item \
  --node-address https://testnet.casper.network/rpc \
  --state-root-hash <state-root> \
  --key hash-<CONTRACT_HASH> \
  --query-path oracle_data
```
