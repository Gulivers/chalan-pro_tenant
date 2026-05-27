"""Legacy import — use tenants.middleware.TenantAccessEnforcementMiddleware."""

from tenants.middleware import TenantAccessEnforcementMiddleware as BillingEnforcementMiddleware

__all__ = ['BillingEnforcementMiddleware']
