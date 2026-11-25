from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from test_job_assistant import module


class PendingEmailTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.store = module.Store(root/'checkout')
        self.store.init(output_dir=root/'reports')
        profile = self.store.profile()
        profile['schedule'].update(timezone='America/Los_Angeles', max_submissions_per_day=5)
        module.write_json(self.store.profile_path, profile)
        self.now = datetime(2030, 6, 2, 1, tzinfo=timezone.utc)
        self.case = self.store.record({'company':'Example', 'role':'SWE',
            'url':'https://example.invalid/jobs/1', 'status':'drafted'}, now=self.now)
        self.event = {'provider':'gmail','account_key':'job-inbox','message_id':'msg-1',
            'received_at':self.now.isoformat(),'category':'interview','summary':'Interview requested',
            'source':'provider message msg-1','case_id':self.case['case_id'],
            'match_evidence':'Exact job ID 1 and company in message'}

    def enable(self):
        self.store.configure_email(True,'gmail','job-inbox','job label; last 7 days')

    def test_email_and_optional_materials_default_without_authorization(self):
        self.assertFalse(self.store.profile()['email_tracking']['enabled'])
        self.assertFalse(self.store.profile()['email_tracking']['verification_assistance'])
        self.assertEqual(self.store.profile()['optional_materials']['transcripts'], [])
        with self.assertRaises(ValueError):
            self.store.email_event(self.event)
        self.assertTrue(self.store.render(now=self.now).exists())

    def test_all_blocker_categories_have_actions_and_render(self):
        for kind in module.BLOCKER_KINDS - {'receipt_unverified'}:
            self.store.block(self.case['case_id'],kind,kind+' observed','Provide missing item','Item verified',now=self.now)
        item=self.store.lookup(self.case['case_id'])
        self.assertEqual(item['status'],'needs_input')
        self.assertEqual(len(item['blocking_items']),len(module.BLOCKER_KINDS)-1)
        content=self.store.render(now=self.now).read_text(encoding='utf-8')
        self.assertIn('Provide missing item',content)
        self.assertIn('Item verified',content)
        self.assertFalse(self.store.gate(item,now=self.now)[0])
        with self.assertRaises(ValueError):
            self.store.block(item['case_id'],'other','reason','','later')

    def test_uncertainty_survives_more_blockers_and_cannot_resume(self):
        self.store.block(self.case['case_id'],'receipt_unverified','No receipt','Inspect receipt','Verified',now=self.now)
        item=self.store.block(self.case['case_id'],'site_error','Timeout','Inspect page','Available',now=self.now)
        self.assertEqual(item['status'],'submission_unknown')
        with self.assertRaises(ValueError):
            self.store.request_resume(item['case_id'])
        self.assertFalse(self.store.gate(item,now=self.now)[0])

    def test_confirmed_receipt_cannot_become_pending(self):
        item=self.store.record({**self.case,'status':'submitted','submitted_at':self.now.isoformat(),
            'submission_evidence':'Explicit confirmation'},now=self.now)
        with self.assertRaises(ValueError):
            self.store.block(item['case_id'],'email_verification','Code needed','User handoff','Complete')

    def test_unresolved_blockers_block_gate_even_if_marked_ready(self):
        item=self.store.block(self.case['case_id'],'missing_material','Transcript missing','Supply','Verified')
        item=self.store.record({**item,'status':'ready'})
        self.assertFalse(self.store.gate(item,now=self.now)[0])

    def test_mail_dedup_and_receipt_state_are_independent(self):
        self.enable()
        self.store.email_event(self.event,now=self.now)
        self.store.email_event(self.event,now=self.now)
        self.assertEqual(len(module.load_json(self.store.personal/'email_events.json')),1)
        self.assertEqual(self.store.lookup(self.case['case_id'])['status'],'drafted')
        self.assertNotIn('submitted_at',self.store.lookup(self.case['case_id']))
        self.assertIn('Interview requested',self.store.render(now=self.now).read_text(encoding='utf-8'))

    def test_ambiguous_mail_keeps_case_unlinked(self):
        self.enable()
        event={k:v for k,v in self.event.items() if k not in {'case_id','match_evidence'}}
        saved=self.store.email_event(event,now=self.now)
        self.assertNotIn('case_id',saved)
        self.assertNotIn('email_updated_at',self.store.lookup(self.case['case_id']))
        self.assertIn('Unlinked',self.store.render(now=self.now).read_text(encoding='utf-8'))
        with self.assertRaises(ValueError):
            self.store.email_event({**event,'case_id':self.case['case_id']})

    def test_mail_schema_scope_codes_and_deadlines(self):
        self.enable()
        for update in ({'raw_body':'not allowed'}, {'code':'not allowed'},
                       {'category':'verification'}, {'account_key':'other'},
                       {'deadline_at':'2030-06-04T10:00:00'},
                       {'deadline_at':'2030-06-04T10:00:00-07:00'}):
            with self.assertRaises(ValueError):
                self.store.email_event({**self.event,**update})
        self.store.email_event({**self.event,'deadline_at':'2030-06-04T10:00:00-07:00',
                               'next_action':'Choose an interview slot'},now=self.now)
        content=self.store.render(now=self.now).read_text(encoding='utf-8')
        self.assertIn('2030-06-04T10:00:00-07:00',content)
        self.assertIn('Choose an interview slot',content)

    def test_disable_hides_email_without_breaking_search_or_deleting_history(self):
        self.enable()
        self.store.email_event(self.event,now=self.now)
        self.store.configure_email(False)
        with self.assertRaises(ValueError):
            self.store.email_event(self.event)
        self.assertNotIn('Job email tracking',self.store.render(now=self.now).read_text(encoding='utf-8'))
        self.assertTrue((self.store.personal/'email_events.json').exists())
        self.assertTrue(self.store.gate(self.case,now=self.now)[0])

    def test_email_local_day_and_account_switch(self):
        self.enable()
        self.store.email_event(self.event,now=self.now)
        self.store.configure(language='zh')
        self.store.render(now=self.now)
        self.assertIn('求职邮件追踪',(self.store.report_root()/'daily/2030-06-01.md').read_text(encoding='utf-8'))
        self.assertIn('面试',self.store.email_report(zh=True)[-1])
        self.assertNotIn('Interview requested','\n'.join(self.store.email_report(day='2030-06-02')))
        self.store.configure_email(True,'gmail','new-inbox','job label')
        self.assertNotIn('Interview requested',self.store.render(now=self.now).read_text(encoding='utf-8'))

    def test_reinitializing_preserves_optin_and_materials(self):
        self.enable()
        self.store.init()
        self.assertTrue(self.store.profile()['email_tracking']['enabled'])


if __name__ == '__main__':
    unittest.main()
