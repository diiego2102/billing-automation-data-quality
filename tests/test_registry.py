import unittest
import billing

class RegistryCoverage(unittest.TestCase):
    def test_fully_absent_account_is_held(self):
        rows=[dict(account_id='A',reading_date=day,cumulative_units=value)
              for day,value in [(billing.START,'10'),(billing.END,'20')]]
        drafts,holds,summary=billing.prepare(rows,eligible_accounts=['A','B'])
        self.assertEqual([x['account_id'] for x in drafts],['A'])
        self.assertEqual([x['account_id'] for x in holds],['B'])
        self.assertEqual(holds[0]['reasons'],'missing_boundary')
        self.assertEqual(summary['accounts'],2)

    def test_unknown_account_is_not_silently_billed(self):
        with self.assertRaises(ValueError):
            billing.prepare([dict(account_id='X',reading_date=billing.START,cumulative_units='10')],eligible_accounts=['A'])
