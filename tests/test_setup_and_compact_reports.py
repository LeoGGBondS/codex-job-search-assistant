from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch
import tempfile
import unittest
from urllib.parse import unquote
import re
from test_job_assistant import module


class SetupReportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.store=module.Store(self.base/'checkout')
        self.store.init(output_dir=self.base/'old reports')
        self.target=self.base/'Desktop'/'Codex Job Search'
        self.now=datetime(2030,6,2,1,tzinfo=timezone.utc)
        self.job={'company':'Example','role':'Backend Intern','status':'needs_input',
                  'url':'https://careers.example.invalid/jobs/a-very-long-job-id?utm_source=test',
                  'notes':'Long contextual notes that need the full report width.',
                  'blocking_items':[{'description':'Transcript unavailable','next_action':'Attach transcript','retry_when':'Transcript verified'}]}

    def test_setup_creates_private_tree_and_reopens_canonical_data(self):
        resume=self.store.personal/'resumes'/'source resume.pdf'
        resume.write_bytes(b'synthetic fixture, not a real resume')
        profile=self.store.profile();profile['resume_path']=str(resume);profile['resume_paths']=[str(resume)]
        module.write_json(self.store.profile_path,profile)
        record=self.store.record({**self.job,'resume_path':str(resume)},now=self.now)
        self.store.render(now=self.now)
        old_daily=(self.base/'old reports/daily/2030-06-02.md').read_bytes()
        self.assertEqual(self.store.setup_desktop(self.target),self.target)
        fresh=module.Store(self.store.root)
        self.assertEqual(fresh.personal,self.target/'personal')
        self.assertEqual(fresh.lookup(record['case_id'])['id'],record['id'])
        self.assertTrue(Path(fresh.profile()['resume_path']).is_file())
        self.assertEqual(Path(fresh.profile()['resume_path']).parent,self.target/'personal/resumes')
        self.assertEqual((self.target/'daily/2030-06-02.md').read_bytes(),old_daily)
        self.assertTrue((self.target/'personal/cover-letters').is_dir())
        self.assertTrue((self.target/'START_HERE.md').is_file())
        self.assertTrue(resume.exists())

    def test_setup_repeat_preserves_receipt_and_new_answers(self):
        receipt='Explicit synthetic confirmation'
        self.store.record({**self.job,'status':'submitted','submitted_at':self.now.isoformat(),
                           'submission_evidence':receipt},now=self.now)
        self.store.setup_desktop(self.target)
        profile=self.store.profile();profile['application_answers']={'confirmed':'new answer'}
        module.write_json(self.store.profile_path,profile)
        self.store.setup_desktop(self.target)
        fresh=module.Store(self.store.root)
        self.assertEqual(fresh.records()[0]['submission_evidence'],receipt)
        self.assertEqual(fresh.profile()['application_answers'],{'confirmed':'new answer'})

    def test_conflict_or_denied_copy_never_publishes_storage_pointer(self):
        (self.target/'personal').mkdir(parents=True)
        (self.target/'personal/profile.json').write_text('{"unrelated":true}',encoding='utf-8')
        with self.assertRaises(ValueError):self.store.setup_desktop(self.target)
        self.assertFalse(self.store.storage_pointer.exists())
        other=self.base/'another desktop'
        with patch.object(module.shutil,'copy2',side_effect=PermissionError('write denied')):
            with self.assertRaises(PermissionError):self.store.setup_desktop(other)
        self.assertFalse(self.store.storage_pointer.exists())

    def test_access_probe_leaves_no_files_or_claim_of_future_grant(self):
        result=self.store.check_access()
        self.assertTrue(result['write_verified_now'])
        self.assertIn('host_managed',result['future_permission_scope'])
        self.assertEqual(list(self.base.rglob('.job-access-*')),[])

    def test_compact_links_resolve_in_master_and_daily_without_narrow_notes_cell(self):
        resume=self.base/'old reports/2030-06-02/J0001/resume (precise).pdf'
        resume.parent.mkdir(parents=True);resume.write_bytes(b'synthetic')
        proof=resume.with_name('proof #1.jpg');proof.write_bytes(b'synthetic')
        self.store.record({**self.job,'resume_path':str(resume),'confirmation_path':str(proof)},now=self.now)
        self.store.render(now=self.now)
        for file in (self.base/'old reports/applications.md',self.base/'old reports/daily/2030-06-02.md'):
            content=file.read_text(encoding='utf-8')
            rows=[x for x in content.splitlines() if x.startswith('|')]
            self.assertTrue(all(x.count('|')==6 for x in rows))
            self.assertIn('**Notes:** Long contextual',content)
            self.assertIn('**Next action:** Attach transcript',content)
            self.assertNotIn(str(resume),content)
            self.assertIn('[Job](https://',content)
            for label,href in re.findall(r'\[(CV|Proof)\]\(([^)]+)\)',content):
                self.assertTrue((file.parent/unquote(href)).resolve().is_file(),(label,href))
            self.assertIn('%28precise%29',content)
            self.assertIn('%231.jpg',content)


if __name__=='__main__':unittest.main()
