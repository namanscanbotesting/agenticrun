//! ComplianceToken Smart Contract
//! Issues and manages on-chain compliance status tokens for users.

use odra::prelude::*;
use odra::collections::Mapping;

/// Compliance Levels
#[odra::type]
pub enum ComplianceLevel {
    Level1 = 1, // Basic KYC (name + email)
    Level2 = 2, // Enhanced KYC (government ID)
    Level3 = 3, // Institutional (full AML + accreditation)
}

/// Structure representing a compliance token
#[odra::type]
pub struct ComplianceToken {
    pub user: Key,
    pub level: ComplianceLevel,
    pub issued_at: u64,
    pub expires_at: u64,
    pub is_active: bool,
}

/// Compliance Status result
#[odra::type]
pub struct ComplianceStatus {
    pub is_compliant: bool,
    pub level: Option<ComplianceLevel>,
    pub expires_at: Option<u64>,
}

/// ComplianceToken Contract
#[odra::module]
pub struct ComplianceTokenContract {
    /// Map of user address to ComplianceToken
    tokens: Mapping<Key, ComplianceToken>,
    /// Admin/Compliance Agent address
    admin: Key,
}

#[odra::module]
impl ComplianceTokenContract {
    /// Constructor
    #[odra(init)]
    pub fn init(&mut self) {
        self.admin.set(caller());
    }

    /// Issue a new compliance token (Called by Compliance Agent)
    pub fn issue_token(
        &mut self,
        user: Key,
        level: ComplianceLevel,
        expires_at: u64,
    ) {
        self.require_admin();
        
        let now = block_time();
        let token = ComplianceToken {
            user,
            level,
            issued_at: now,
            expires_at,
            is_active: true,
        };

        self.tokens.insert(user, token);

        self.emit_event(TokenIssued {
            user,
            level,
            expires_at,
        });
    }

    /// Revoke a compliance token (Called by Compliance Agent)
    pub fn revoke_token(&mut self, user: Key, reason: String) {
        self.require_admin();

        if let Some(mut token) = self.tokens.get(&user) {
            token.is_active = false;
            self.tokens.insert(user, token);

            self.emit_event(TokenRevoked {
                user,
                reason,
            });
        }
    }

    /// Upgrade compliance level (Called by Compliance Agent)
    pub fn upgrade_compliance(&mut self, user: Key, new_level: ComplianceLevel, expires_at: u64) {
        self.require_admin();

        if let Some(mut token) = self.tokens.get(&user) {
            token.level = new_level;
            token.expires_at = expires_at;
            token.is_active = true;
            self.tokens.insert(user, token);

            self.emit_event(TokenUpgraded {
                user,
                new_level,
                expires_at,
            });
        }
    }

    /// Check compliance status (Called by DeFi protocols or anyone)
    pub fn check_compliance(&self, user: Key) -> ComplianceStatus {
        if let Some(token) = self.tokens.get(&user) {
            let now = block_time();
            let is_valid = token.is_active && now < token.expires_at;
            
            ComplianceStatus {
                is_compliant: is_valid,
                level: if is_valid { Some(token.level) } else { None },
                expires_at: if is_valid { Some(token.expires_at) } else { None },
            }
        } else {
            ComplianceStatus {
                is_compliant: false,
                level: None,
                expires_at: None,
            }
        }
    }

    /// Get token details (Public)
    pub fn get_token(&self, user: Key) -> Option<ComplianceToken> {
        self.tokens.get(&user)
    }

    /// Helper: Ensure caller is admin
    fn require_admin(&self) {
        assert_eq!(caller(), self.admin.get(), "Only admin can call this");
    }
}

// Events
#[odra::type]
pub struct TokenIssued {
    pub user: Key,
    pub level: ComplianceLevel,
    pub expires_at: u64,
}

#[odra::type]
pub struct TokenRevoked {
    pub user: Key,
    pub reason: String,
}

#[odra::type]
pub struct TokenUpgraded {
    pub user: Key,
    pub new_level: ComplianceLevel,
    pub expires_at: u64,
}
