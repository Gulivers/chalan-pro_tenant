from django.test import SimpleTestCase

from appsearch.services.intent import parse_search_intent


class CompoundDocumentTypeIntentTests(SimpleTestCase):
    def test_sales_order_keeps_phrase_for_entity_resolution(self):
        filters, remaining = parse_search_intent('sales order')
        self.assertEqual(filters, {})
        self.assertEqual(remaining, 'sales order')

    def test_purchase_order_keeps_phrase_for_entity_resolution(self):
        filters, remaining = parse_search_intent('purchase order')
        self.assertEqual(filters, {})
        self.assertEqual(remaining, 'purchase order')

    def test_purchase_return_keeps_phrase_for_entity_resolution(self):
        filters, remaining = parse_search_intent('purchase return')
        self.assertEqual(filters, {})
        self.assertEqual(remaining, 'purchase return')

    def test_sales_purchases_still_sets_both_flags(self):
        filters, remaining = parse_search_intent('sales purchases')
        self.assertTrue(filters.get('is_sales'))
        self.assertTrue(filters.get('is_purchase'))

    def test_generic_sales_still_strips(self):
        filters, remaining = parse_search_intent('sales from Home Depot')
        self.assertTrue(filters.get('is_sales'))
        self.assertNotIn('sales', remaining.lower())
