from django.test import SimpleTestCase

from appsearch.services.search import (
    _clean_semantic_query,
    _filter_rows_by_snippet_tokens,
    _normalize_query_text,
)


class SemanticQueryCleanupTests(SimpleTestCase):
    def test_strip_trailing_question_mark(self):
        self.assertEqual(_normalize_query_text('Home Depot purchases this month?'), 'Home Depot purchases this month')

    def test_remove_stopword_from(self):
        self.assertEqual(_clean_semantic_query('from'), '')

    def test_filter_rows_requires_product_tokens_in_snippet(self):
        rows = [
            {'snippet': 'PINV | Home Depot | Red Stucco Tape | TAPE-STUCCO', 'score': 0.5},
            {'snippet': 'PK | Pulte | 14/3 Romex | NM-B-14/3-CU', 'score': 0.3},
        ]
        filtered = _filter_rows_by_snippet_tokens(rows, 'red stucco tape')
        self.assertEqual(len(filtered), 1)
        self.assertIn('Red Stucco Tape', filtered[0]['snippet'])
