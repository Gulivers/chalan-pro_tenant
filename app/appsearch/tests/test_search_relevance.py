from unittest.mock import patch

from django.test import SimpleTestCase

from appsearch.services.entities import looks_like_unresolved_document_type

_MOCK_VOCAB = frozenset({
    'missing', 'material', 'sales', 'order',
    'purchase', 'invoice', 'inventory',
    'goods', 'receipt', 'note', 'return', 'credit', 'delivery',
})


@patch('appsearch.services.entities._transaction_vocabulary', return_value=_MOCK_VOCAB)
class UnresolvedDocumentTypeIntentTests(SimpleTestCase):
    def test_missing_material_without_resolved_type(self, _mock_vocab):
        self.assertTrue(
            looks_like_unresolved_document_type(
                'missing material',
                document_type_resolved=False,
            )
        )

    def test_construction_material_is_product_search(self, _mock_vocab):
        self.assertFalse(
            looks_like_unresolved_document_type(
                'construction material',
                document_type_resolved=False,
            )
        )

    def test_resolved_type_skips_check(self, _mock_vocab):
        self.assertFalse(
            looks_like_unresolved_document_type(
                'missing material',
                document_type_resolved=True,
            )
        )

    def test_party_product_query_not_type_intent(self, _mock_vocab):
        self.assertFalse(
            looks_like_unresolved_document_type(
                'red stucco tape',
                document_type_resolved=False,
            )
        )

    def test_compras_is_purchase_intent_not_missing_type(self, _mock_vocab):
        self.assertFalse(
            looks_like_unresolved_document_type(
                'compras',
                document_type_resolved=False,
            )
        )

    def test_sales_is_sales_intent_not_missing_type(self, _mock_vocab):
        self.assertFalse(
            looks_like_unresolved_document_type(
                'sales',
                document_type_resolved=False,
            )
        )
