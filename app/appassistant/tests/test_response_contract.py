from django.test import SimpleTestCase, override_settings

from appassistant.contracts.response import (
    ALLOWED_BLOCK_TYPES,
    SCHEMA_VERSION,
    build_assistant_response,
    build_stub_response,
    validate_response_payload,
)


class ResponseContractTests(SimpleTestCase):
    def test_stub_response_is_valid(self):
        payload = build_stub_response(
            request_id='11111111-1111-1111-1111-111111111111',
            context={'view': 'transactions', 'route_name': None, 'entity_type': None, 'entity_id': None},
        )
        self.assertEqual(validate_response_payload(payload), [])
        self.assertEqual(payload['schema_version'], SCHEMA_VERSION)
        self.assertEqual(payload['blocks'], [])
        self.assertIn('PINV', payload['context']['spend_definition'])
        self.assertEqual(payload['meta']['router'], 'none')
        self.assertEqual(payload['meta']['tools_executed'], [])

    def test_unknown_block_type_rejected(self):
        payload = build_stub_response(
            request_id='11111111-1111-1111-1111-111111111111',
            context={},
        )
        payload['blocks'] = [{'type': 'html', 'id': 'x'}]
        errors = validate_response_payload(payload)
        self.assertTrue(any('not an allowed' in e for e in errors))

    def test_kpi_requires_string_value_and_format(self):
        payload = build_stub_response(
            request_id='11111111-1111-1111-1111-111111111111',
            context={},
        )
        payload['blocks'] = [{'type': 'kpi', 'id': 'k1', 'value': 12.5, 'format': 'currency'}]
        errors = validate_response_payload(payload)
        self.assertTrue(any('non-empty string' in e for e in errors))

    def test_entity_link_allowlist(self):
        payload = build_stub_response(
            request_id='11111111-1111-1111-1111-111111111111',
            context={},
        )
        payload['blocks'] = [{
            'type': 'entity_link',
            'id': 'e1',
            'entity_type': 'document',
            'entity_id': 1,
            'route_key': 'transactions-form',
            'path': '/transactions/form?id=1&mode=view',
        }]
        self.assertEqual(validate_response_payload(payload), [])
        payload['blocks'][0]['route_key'] = 'arbitrary-route'
        errors = validate_response_payload(payload)
        self.assertTrue(any('route_key' in e for e in errors))

    def test_entity_link_path_must_match_template(self):
        payload = build_assistant_response(
            request_id='11111111-1111-1111-1111-111111111111',
            message='ok',
            blocks=[{
                'type': 'entity_link',
                'id': 'e1',
                'entity_type': 'document',
                'entity_id': 1,
                'route_key': 'transactions-form',
                'path': '/evil/path?id=1',
            }],
            context={},
            tools_executed=[],
        )
        errors = validate_response_payload(payload)
        self.assertTrue(any('path must match template' in e for e in errors))

    def test_chart_labels_values_same_length(self):
        payload = build_stub_response(
            request_id='11111111-1111-1111-1111-111111111111',
            context={},
        )
        payload['blocks'] = [{
            'type': 'bar_chart',
            'id': 'c1',
            'labels': ['a', 'b'],
            'values': ['1.00'],
        }]
        errors = validate_response_payload(payload)
        self.assertTrue(any('same length' in e for e in errors))

    def test_allowed_block_types_cover_level_1(self):
        expected = {
            'text', 'kpi', 'kpi_group', 'table',
            'bar_chart', 'line_chart', 'donut_chart',
            'entity_link', 'source',
        }
        self.assertEqual(ALLOWED_BLOCK_TYPES, expected)

    @override_settings(TIME_ZONE='America/New_York')
    def test_timezone_from_settings(self):
        payload = build_stub_response(
            request_id='11111111-1111-1111-1111-111111111111',
            context={},
        )
        self.assertEqual(payload['meta']['timezone'], 'America/New_York')
