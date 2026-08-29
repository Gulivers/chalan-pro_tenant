"""
One-off smoke against tenant schema test_dominio_local (id=3).
Run inside backend container:

  python manage.py shell < appassistant/scripts/smoke_test_dominio_local.py
"""

from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.db.models import Max, Min
from django_tenants.utils import schema_context
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate

from appassistant.contracts.response import validate_response_payload
from appassistant.services.deterministic_router import route
from appassistant.views import AssistantQueryView
from apptransactions.models import Document

SCHEMA = 'test_dominio_local'

# Acceptance-shaped prompts using vendors present in test_dominio_local.
PROMPTS_EXACT = [
    'Show me Home Depot transactions over $1,500 this month.',
    'How much did we spend with Home Depot this month?',
    'Show purchases by vendor this month.',
    'Compare purchases by supplier for the last six months.',
    'Show the five vendors with the highest spending.',
    'Graph spending for the last three months.',
]

PROMPTS_ADAPTED = [
    'Show me Home Depot transactions over $1,500 this month.',
    'How much did we spend with Home Depot this month?',
    'How much did we spend with Globo Dine this month?',
    'Show purchases by vendor this month.',
    'Compare purchases by supplier for the last six months.',
    'Show the five vendors with the highest spending.',
    'Graph spending for the last three months.',
]


def _summarize_blocks(blocks):
    lines = []
    for b in blocks or []:
        btype = b.get('type')
        if btype == 'kpi':
            lines.append(
                f"kpi[{b.get('id')}]={b.get('value')} {b.get('format')}"
            )
        elif btype == 'table':
            rows = b.get('rows') or []
            lines.append(
                f"table rows={len(rows)} total={b.get('pagination', {}).get('total')}"
            )
            for row in rows[:5]:
                lines.append('  ' + json.dumps(row, default=str)[:180])
        elif btype in ('bar_chart', 'line_chart'):
            lines.append(
                f"{btype} labels={b.get('labels')} values={b.get('values')}"
            )
        elif btype == 'text':
            text = (b.get('text') or '')[:140].replace('\n', ' | ')
            lines.append(f'text: {text}')
        elif btype == 'entity_link':
            lines.append(
                f"link {b.get('entity_type')}#{b.get('entity_id')} -> {b.get('path')}"
            )
    return lines


def run_set(label, prompts, user, view, factory, token):
    print('=' * 72)
    print(label)
    print('=' * 72)
    for i, msg in enumerate(prompts, 1):
        routed = route(msg)
        payload = {
            'schema_version': '1',
            'message': msg,
            'context': {'view': 'transactions', 'route_name': 'transactions'},
        }
        request = factory.post('/api/assistant/query/', payload, format='json')
        force_authenticate(request, user=user, token=token)
        response = view(request)
        data = response.data
        errs = (
            validate_response_payload(data)
            if response.status_code == 200
            else ['non-200']
        )
        tools = data.get('meta', {}).get('tools_executed') if isinstance(data, dict) else None
        blocks = data.get('blocks') if isinstance(data, dict) else []
        btypes = [b.get('type') for b in (blocks or [])]
        message = data.get('message') if isinstance(data, dict) else data
        print(f'--- Case {i} ---')
        print(f'Q: {msg}')
        print(
            f'route: case={routed.matched_case} tool={routed.tool_name} '
            f'params={routed.params}'
        )
        print(
            f'HTTP {response.status_code} tools_executed={tools} '
            f'contract_ok={errs == []}'
        )
        print(f'message: {str(message)[:240]}')
        print(f'blocks: {btypes}')
        for line in _summarize_blocks(blocks)[:14]:
            print(line)
        print()


with schema_context(SCHEMA):
    User = get_user_model()
    user = User.objects.get(username='Oliver')
    qs = Document.objects.filter(document_type__type_code='PINV', is_active=True)
    agg = qs.aggregate(dmin=Min('date'), dmax=Max('date'))
    print(f'Tenant schema={SCHEMA}')
    print(f'User={user.username} (id={user.pk})')
    print(f'PINV active n={qs.count()} date range={agg["dmin"]} .. {agg["dmax"]}')
    print()

    factory = APIRequestFactory()
    view = AssistantQueryView.as_view()
    token, _ = Token.objects.get_or_create(user=user)

    run_set('A) 6 PROMPTS EXACTOS (aceptación)', PROMPTS_EXACT, user, view, factory, token)
    run_set(
        'B) VARIANTES CON VENDOR REAL (Home Depot)',
        PROMPTS_ADAPTED,
        user,
        view,
        factory,
        token,
    )

print('SMOKE_DONE')
