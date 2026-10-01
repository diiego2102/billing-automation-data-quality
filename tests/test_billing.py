import importlib.util
from pathlib import Path
from decimal import Decimal
import unittest

spec=importlib.util.spec_from_file_location('billing',Path(__file__).resolve().parents[1]/'billing.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def pair(account='A',start='100',end='250'):
    return [dict(account_id=account,reading_date=b.START,cumulative_units=start),
            dict(account_id=account,reading_date=b.END,cumulative_units=end)]


class BillingTests(unittest.TestCase):
    def test_verified_amount_and_idempotence(self):
        rows=pair();drafts,held,summary=b.prepare(rows)
        self.assertEqual(drafts[0]['consumption_units'],'150')
        self.assertEqual(drafts[0]['variable_charge'],'27.00')
        self.assertEqual(drafts[0]['total_before_tax'],'31.50')
        self.assertEqual(held,[])
        self.assertEqual(b.prepare(rows),b.prepare(list(reversed(rows))))

    def test_defects_block_account_and_partition(self):
        rows=b.generate();drafts,held,summary=b.prepare(rows)
        self.assertEqual((len(drafts),len(held)),(95,5))
        self.assertEqual(summary['accounts'],100)
        actual={e['account_id']:e['reasons'] for e in held}
        expected=dict(zip([f'DEMO-{i:04}' for i in range(1,6)],
            ['duplicate_boundary','missing_boundary','negative_delta_or_reset','high_consumption_review','invalid_reading']))
        self.assertEqual(actual,expected)
        self.assertEqual(Decimal(summary['total_before_tax']),sum(Decimal(d['total_before_tax']) for d in drafts))

    def test_zero_consumption_and_decimal_rounding(self):
        self.assertEqual(b.prepare(pair(end='100'))[0][0]['total_before_tax'],'4.50')
        self.assertEqual(b.prepare(pair(start='100',end='100.25'))[0][0]['variable_charge'],'0.05')

    def test_nonfinite_and_unexpected_dates_are_held(self):
        for invalid in ['NaN','Infinity','-1','unknown']:
            drafts,held,_=b.prepare(pair(end=invalid))
            self.assertEqual(drafts,[]);self.assertIn('invalid_reading',held[0]['reasons'])
        rows=pair()+[dict(account_id='A',reading_date='2026-09-10',cumulative_units='120')]
        self.assertEqual(b.prepare(rows)[1][0]['reasons'],'unexpected_date')

    def test_orphans_raise_instead_of_silent_drop(self):
        with self.assertRaises(ValueError):b.prepare([dict(account_id='',reading_date=b.START,cumulative_units='100')])


if __name__=='__main__':unittest.main()
