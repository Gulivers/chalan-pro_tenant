"""Parse and validate public onboarding form payloads."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email

from tenants.models import Tenant


class OnboardingValidationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class OnboardingFormData:
    company_name: str
    email: str
    client_type: str = 'general'
    address: Optional[str] = None
    monthly_operations: Optional[str] = None
    crew_count: Optional[int] = None
    recommended_plan: Optional[str] = None
    landing_selected_plan: Optional[str] = None
    admin_name: Optional[str] = None
    admin_password: Optional[str] = None
    preferences: list[str] = field(default_factory=list)


VALID_PREFERENCES = {
    'operations',
    'inventory',
    'contracts_pricing',
    'entities',
    'crews_fleet',
    'communities',
    'contracts',
    'schedule',
    'crews',
    'notes',
}


def _parse_preferences(request) -> list[str]:
    preferences: list[str] = []
    prefs_data = request.data.get('preferences', [])

    if isinstance(prefs_data, list):
        preferences = prefs_data
    elif isinstance(prefs_data, str):
        try:
            preferences = json.loads(prefs_data)
        except json.JSONDecodeError:
            preferences = [p.strip() for p in prefs_data.split(',') if p.strip()]
    else:
        prefs_list = request.data.getlist('preferences', [])
        if prefs_list:
            preferences = prefs_list

    return [p for p in preferences if p in VALID_PREFERENCES]


def _parse_admin_fields(request) -> tuple[Optional[str], Optional[str], str]:
    email = (request.data.get('email') or '').strip()
    admin_name = None
    admin_password = None

    admin_data = request.data.get('admin', {})
    if isinstance(admin_data, dict):
        if not email:
            email = (admin_data.get('email') or '').strip()
        admin_name = (admin_data.get('name') or '').strip() or None
        admin_password = (admin_data.get('password') or '').strip() or None
    elif isinstance(admin_data, str):
        try:
            parsed = json.loads(admin_data)
            if not email:
                email = (parsed.get('email') or '').strip()
            admin_name = (parsed.get('name') or '').strip() or None
            admin_password = (parsed.get('password') or '').strip() or None
        except json.JSONDecodeError:
            pass

    if not admin_name:
        admin_name = (request.data.get('admin_name') or '').strip() or None
    if not admin_password:
        admin_password = (request.data.get('admin_password') or '').strip() or None

    return admin_name, admin_password, email


def parse_onboarding_request(request) -> OnboardingFormData:
    company_name = (request.data.get('company_name') or '').strip()
    client_type = request.data.get('client_type', 'general')
    address = (request.data.get('address') or '').strip() or None
    monthly_operations = (request.data.get('monthly_operations') or '').strip() or None
    crew_count_raw = request.data.get('crew_count', None)
    recommended_plan = (request.data.get('recommended_plan') or '').strip() or None
    landing_selected_plan = (request.data.get('landing_selected_plan') or '').strip() or None

    crew_count = None
    if crew_count_raw:
        try:
            crew_count = int(crew_count_raw)
            if crew_count < 1:
                crew_count = None
        except (ValueError, TypeError):
            crew_count = None

    valid_monthly_ops = ['0-10', '11-25', '26-50', '51-100', '100+']
    if monthly_operations and monthly_operations not in valid_monthly_ops:
        monthly_operations = None

    valid_plans = ['Starter', 'Professional', 'Enterprise']
    if recommended_plan and recommended_plan not in valid_plans:
        recommended_plan = None
    if landing_selected_plan and landing_selected_plan not in valid_plans:
        landing_selected_plan = None

    admin_name, admin_password, email = _parse_admin_fields(request)
    preferences = _parse_preferences(request)

    if not company_name or len(company_name) < 3:
        raise OnboardingValidationError('Company name must be at least 3 characters long.')
    if not email:
        raise OnboardingValidationError('Email is required.')
    try:
        validate_email(email)
    except DjangoValidationError:
        raise OnboardingValidationError('Please enter a valid email address.')

    if Tenant.objects.filter(email=email).exists():
        raise OnboardingValidationError(
            'This email is already registered. Please use a different email.'
        )
    if Tenant.objects.filter(name__iexact=company_name).exists():
        raise OnboardingValidationError(
            'This company name is already registered. Please choose a different name.'
        )

    valid_client_types = [choice[0] for choice in Tenant.CLIENT_TYPE_CHOICES]
    if client_type not in valid_client_types:
        client_type = 'general'

    return OnboardingFormData(
        company_name=company_name,
        email=email,
        client_type=client_type,
        address=address,
        monthly_operations=monthly_operations,
        crew_count=crew_count,
        recommended_plan=recommended_plan,
        landing_selected_plan=landing_selected_plan,
        admin_name=admin_name,
        admin_password=admin_password,
        preferences=preferences,
    )


def form_data_to_payload(data: OnboardingFormData, sealed_password: str) -> dict[str, Any]:
    return {
        'company_name': data.company_name,
        'email': data.email,
        'client_type': data.client_type,
        'address': data.address,
        'monthly_operations': data.monthly_operations,
        'crew_count': data.crew_count,
        'recommended_plan': data.recommended_plan,
        'landing_selected_plan': data.landing_selected_plan,
        'admin_name': data.admin_name,
        'admin_password_sealed': sealed_password,
        'preferences': data.preferences,
    }


def payload_to_form_data(payload: dict[str, Any]) -> OnboardingFormData:
    from tenants.services.onboarding_secrets import safe_unseal_admin_password

    sealed = payload.get('admin_password_sealed') or ''
    return OnboardingFormData(
        company_name=payload['company_name'],
        email=payload['email'],
        client_type=payload.get('client_type') or 'general',
        address=payload.get('address'),
        monthly_operations=payload.get('monthly_operations'),
        crew_count=payload.get('crew_count'),
        recommended_plan=payload.get('recommended_plan'),
        landing_selected_plan=payload.get('landing_selected_plan'),
        admin_name=payload.get('admin_name'),
        admin_password=safe_unseal_admin_password(sealed) or None,
        preferences=payload.get('preferences') or [],
    )
