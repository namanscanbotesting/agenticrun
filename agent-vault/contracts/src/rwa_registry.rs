//! RWA Registry Contract
//! 
//! Manages registration and metadata for Real World Assets (RWAs) on Casper Network.
//! Tracks asset ownership, valuation, and compliance status.

use odra::prelude::*;
use odra::casper_types::{U512, Address};

/// Asset type enumeration
#[derive(Clone, Debug, PartialEq)]
pub enum AssetType {
    RealEstate,
    Commodity,
    Bond,
    Equity,
    Other,
}

/// RWA Asset information
#[derive(Clone, Debug)]
pub struct RWAAsset {
    pub id: U512,
    pub name: String,
    pub asset_type: AssetType,
    pub total_supply: U512,
    pub circulating_supply: U512,
    pub owner: Address,
    pub metadata_uri: String,
    pub is_compliant: bool,
    pub created_at: u64,
}

/// Compliance status for an asset
#[derive(Clone, Debug)]
pub struct ComplianceStatus {
    pub is_verified: bool,
    pub verified_by: Address,
    pub verified_at: u64,
    pub kyc_status: bool,
    pub aml_status: bool,
}

/// RWA Registry Contract
/// 
/// Registers and manages Real World Assets with compliance tracking
#[odra::module]
pub struct RWARegistry {
    owner: Address,
    next_asset_id: U512,
    assets: Mapping<U512, RWAAsset>,
    asset_owners: Mapping<Address, Vec<U512>>,
    compliance_statuses: Mapping<U512, ComplianceStatus>,
}

#[odra::module]
impl RWARegistry {
    /// Initialize the RWA registry contract
    #[odra(init)]
    pub fn init(&mut self, owner: Address) {
        self.owner = owner;
        self.next_asset_id = U512::one();
    }

    /// Register a new RWA asset
    #[odra(execute)]
    pub fn register_asset(
        &mut self,
        name: String,
        asset_type: AssetType,
        total_supply: U512,
        metadata_uri: String,
    ) -> Result<U512, OdraError> {
        if self.env().caller() != self.owner {
            return Err(OdraError::CustomError("Only owner can register assets".into()));
        }

        if total_supply.is_zero() {
            return Err(OdraError::CustomError("Total supply must be greater than zero".into()));
        }

        let asset_id = self.next_asset_id;
        self.next_asset_id = self.next_asset_id + U512::one();

        let asset = RWAAsset {
            id: asset_id,
            name,
            asset_type,
            total_supply,
            circulating_supply: U512::zero(),
            owner: self.env().caller(),
            metadata_uri,
            is_compliant: false,
            created_at: self.env().get_block_time(),
        };

        self.assets.set(&asset_id, &asset);

        // Emit registration event
        self.env().emit_event(AssetRegisteredEvent {
            asset_id,
            name: asset.name.clone(),
            asset_type: format!("{:?}", asset.asset_type),
            timestamp: self.env().get_block_time(),
        });

        Ok(asset_id)
    }

    /// Update compliance status for an asset
    #[odra(execute)]
    pub fn update_compliance(
        &mut self,
        asset_id: U512,
        kyc_status: bool,
        aml_status: bool,
    ) -> Result<(), OdraError> {
        if self.env().caller() != self.owner {
            return Err(OdraError::CustomError("Only owner can update compliance".into()));
        }

        let mut asset = self.assets.get(&asset_id).ok_or_else(|| {
            OdraError::CustomError("Asset not found".into())
        })?;

        let compliance = ComplianceStatus {
            is_verified: kyc_status && aml_status,
            verified_by: self.env().caller(),
            verified_at: self.env().get_block_time(),
            kyc_status,
            aml_status,
        };

        asset.is_compliant = compliance.is_verified;
        self.assets.set(&asset_id, &asset);
        self.compliance_statuses.set(&asset_id, &compliance);

        // Emit compliance update event
        self.env().emit_event(ComplianceUpdatedEvent {
            asset_id,
            is_compliant: compliance.is_verified,
            timestamp: self.env().get_block_time(),
        });

        Ok(())
    }

    /// Get asset information
    #[odra(view)]
    pub fn get_asset(&self, asset_id: U512) -> Option<RWAAsset> {
        self.assets.get(&asset_id)
    }

    /// Get compliance status for an asset
    #[odra(view)]
    pub fn get_compliance_status(&self, asset_id: U512) -> Option<ComplianceStatus> {
        self.compliance_statuses.get(&asset_id)
    }

    /// Get all assets owned by an address
    #[odra(view)]
    pub fn get_assets_by_owner(&self, owner: Address) -> Vec<U512> {
        self.asset_owners.get(&owner).unwrap_or_default()
    }

    /// Get total number of registered assets
    #[odra(view)]
    pub fn get_total_assets(&self) -> U512 {
        self.next_asset_id - U512::one()
    }
}

// Events
#[odra(event)]
pub struct AssetRegisteredEvent {
    pub asset_id: U512,
    pub name: String,
    pub asset_type: String,
    pub timestamp: u64,
}

#[odra(event)]
pub struct ComplianceUpdatedEvent {
    pub asset_id: U512,
    pub is_compliant: bool,
    pub timestamp: u64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use odra_test::env;

    #[test]
    fn test_register_asset() {
        let env = env::test_env();
        let owner = env.get_account(0);

        let mut contract = RWARegistry::deploy(&env, owner);
        
        env.caller(owner);
        let asset_id = contract.register_asset(
            "Test Real Estate".into(),
            AssetType::RealEstate,
            U512::from(1000000),
            "ipfs://QmTest123".into(),
        ).unwrap();
        
        assert_eq!(asset_id, U512::one());
        
        let asset = contract.get_asset(asset_id).unwrap();
        assert_eq!(asset.name, "Test Real Estate");
        assert_eq!(asset.asset_type, AssetType::RealEstate);
    }

    #[test]
    fn test_update_compliance() {
        let env = env::test_env();
        let owner = env.get_account(0);

        let mut contract = RWARegistry::deploy(&env, owner);
        
        env.caller(owner);
        let asset_id = contract.register_asset(
            "Test Commodity".into(),
            AssetType::Commodity,
            U512::from(500000),
            "ipfs://QmTest456".into(),
        ).unwrap();
        
        contract.update_compliance(asset_id, true, true).unwrap();
        
        let compliance = contract.get_compliance_status(asset_id).unwrap();
        assert!(compliance.is_verified);
        assert!(compliance.kyc_status);
        assert!(compliance.aml_status);
    }
}
