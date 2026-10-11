"""Unit tests for DocumentType Assistant intention helpers."""

from django.test import SimpleTestCase

from apptransactions.assistant_intentions import (
    INTENTION_JOB_MATERIAL_ISSUE,
    INTENTION_NET_INVOICED_SPEND,
    INTENTION_PURCHASE_RETURN,
    suggest_intentions_from_flags,
)


class SuggestIntentionsTests(SimpleTestCase):
    def test_pinv_and_po_inv_suggest_spend(self):
        for code in ('PINV', 'PO-INV', 'po_inv'):
            sug = suggest_intentions_from_flags(type_code=code)
            self.assertTrue(sug[INTENTION_NET_INVOICED_SPEND], code)
            self.assertFalse(sug[INTENTION_PURCHASE_RETURN], code)

    def test_iniinv_not_forced_by_code(self):
        sug = suggest_intentions_from_flags(
            type_code='INIINV',
            is_purchase=True,
            affects_physical=True,
            stock_movement=1,
        )
        self.assertFalse(sug[INTENTION_NET_INVOICED_SPEND])

    def test_pk_suggests_job_material(self):
        sug = suggest_intentions_from_flags(type_code='PK')
        self.assertTrue(sug[INTENTION_JOB_MATERIAL_ISSUE])

    def test_prn_suggests_purchase_return(self):
        sug = suggest_intentions_from_flags(type_code='PRN')
        self.assertTrue(sug[INTENTION_PURCHASE_RETURN])
        self.assertFalse(sug[INTENTION_NET_INVOICED_SPEND])
