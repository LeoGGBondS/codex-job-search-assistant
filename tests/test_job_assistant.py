import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location('job_assistant', Path(__file__).resolve().parents[1] / 'scripts/job_assistant.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = module.Store(self.temp.name)
        self.store.init()
        profile = self.store.profile()
        profile['schedule'].update(timezone='UTC', max_submissions_per_day=1)
        module.write_json(self.store.profile_path, profile)
        self.job = {'company':'Example Robotics', 'role':'Backend Intern',
                    'url':'https://careers.example.invalid/jobs/1', 'job_id':'1', 'status':'screened'}
        self.now = datetime(2030, 6, 1, 12, tzinfo=timezone.utc)

    def submitted(self):
        return {**self.job, 'status':'submitted', 'submitted_at':'2030-06-01T11:00:00+00:00',
                'submission_evidence':'Synthetic confirmation receipt'}

    def test_init_preserves_existing_profile_and_records(self):
        profile = self.store.profile()
        profile['target_roles'] = ['Backend']
        module.write_json(self.store.profile_path, profile)
        self.store.record(self.job)
        self.store.init()
        self.assertEqual(self.store.profile()['target_roles'], ['Backend'])
        self.assertEqual(len(self.store.records()), 1)
        self.assertFalse(self.store.profile()['onboarding_complete'])
        self.assertIsNone(self.store.profile()['gpa']['actual'])

    def test_tracking_parameters_do_not_duplicate_a_job(self):
        first = self.store.record(self.job)
        changed = {**self.job, 'url':self.job['url']+'/?gh_src=demo&utm_source=test#apply', 'status':'ready'}
        second = self.store.record(changed)
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(len(self.store.records()), 1)

    def test_same_company_job_id_deduplicates_alternate_url(self):
        self.store.record(self.job)
        self.store.record({**self.job, 'company':'  EXAMPLE   Robotics ', 'url':'https://careers.example.invalid/alternate/1'})
        self.assertEqual(len(self.store.records()), 1)

    def test_different_company_same_job_id_is_not_duplicate(self):
        self.store.record(self.job)
        self.store.record({**self.job, 'company':'Another Example', 'url':'https://other.example.invalid/jobs/1'})
        self.assertEqual(len(self.store.records()), 2)

    def test_submission_requires_explicit_evidence_and_timezone(self):
        for item in ({**self.job, 'status':'submitted'},
                     {**self.submitted(), 'submitted_at':'2030-06-01T11:00:00'}):
            with self.assertRaises(ValueError):
                self.store.record(item)
        self.assertEqual(self.store.records(), [])

    def test_cannot_reset_receipt_or_make_submitted_job_pending(self):
        self.store.record(self.submitted())
        with self.assertRaises(ValueError):
            self.store.record(self.job)
        with self.assertRaises(ValueError):
            self.store.record({**self.submitted(), 'submission_evidence':None})
        self.assertFalse(self.store.gate(self.job, self.now)[0])

    def test_uncertain_submission_blocks_retry(self):
        self.store.record({**self.job, 'status':'submission_unknown'})
        self.assertFalse(self.store.gate(self.job, self.now)[0])
        with self.assertRaises(ValueError):
            self.store.record({**self.job, 'status':'ready'})
        self.store.record(self.submitted())
        self.assertEqual(self.store.records()[0]['status'], 'submitted')

    def test_later_outcome_still_counts_towards_cap(self):
        self.store.record(self.submitted())
        self.store.record({**self.job, 'status':'interview'})
        other = {**self.job, 'job_id':'2', 'url':'https://careers.example.invalid/jobs/2'}
        self.assertFalse(self.store.gate(other, self.now)[0])
        tomorrow = datetime(2030, 6, 2, 1, tzinfo=timezone.utc)
        self.assertTrue(self.store.gate(other, tomorrow)[0])

    def test_daily_count_uses_candidate_timezone(self):
        profile = self.store.profile()
        profile['schedule']['timezone'] = 'America/Los_Angeles'
        module.write_json(self.store.profile_path, profile)
        self.store.record({**self.submitted(), 'submitted_at':'2030-06-02T01:00:00+00:00'})
        # Still June 1 in Los Angeles.
        now = datetime(2030, 6, 2, 6, tzinfo=timezone.utc)
        other = {**self.job, 'job_id':'2', 'url':'https://careers.example.invalid/jobs/2'}
        self.assertFalse(self.store.gate(other, now)[0])
        self.assertTrue(self.store.gate(other, datetime(2030, 6, 2, 8, tzinfo=timezone.utc))[0])

    def test_profile_starts_with_no_live_schedule_or_identity(self):
        profile = self.store.profile()
        self.assertFalse(profile['schedule']['enabled'])
        self.assertIsNone(profile['name'])
        self.assertIsNone(profile['work_authorization'].get('US'))

    def test_log_escapes_html_pipes_and_linebreaks(self):
        self.store.record({**self.job, 'notes':'<script>bad</script> | next\nline'})
        content = self.store.render().read_text(encoding='utf-8')
        self.assertNotIn('<script>', content)
        self.assertIn('&lt;script&gt;', content)
        self.assertIn('\\| next line', content)
        self.assertIn('已筛选', content)

    def test_credential_urls_rejected_without_mutation(self):
        with self.assertRaises(ValueError):
            self.store.record({**self.job, 'url':'https://name:secret@example.invalid/jobs/1'})
        self.assertEqual(self.store.records(), [])


if __name__ == '__main__':
    unittest.main()
