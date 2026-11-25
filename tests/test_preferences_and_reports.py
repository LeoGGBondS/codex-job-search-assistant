from pathlib import Path
from datetime import datetime, timezone
import tempfile
import unittest
from unittest.mock import patch
from test_job_assistant import module


class PreferenceReportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.store=module.Store(self.root/'checkout')
        self.out=self.root/'Desktop'/'Codex Job Search'
        self.store.init(message='Start my job search',output_dir=self.out)
        profile=self.store.profile()
        profile['schedule'].update(timezone='America/Los_Angeles',max_submissions_per_day=3)
        module.write_json(self.store.profile_path,profile)
        self.now=datetime(2030,6,2,1,tzinfo=timezone.utc)
        self.job={'company':'Example Robotics','role':'Backend Intern','url':'https://careers.example.invalid/jobs/1','status':'needs_input','blocking_items':['Transcript']}

    def test_initialization_language_and_explicit_override(self):
        self.assertEqual(module.infer_language('帮我初始化求职助手'),'zh')
        self.assertEqual(module.infer_language('Initialize my job assistant'),'en')
        self.assertEqual(module.infer_language('帮我初始化求职助手','en'),'en')

    def test_desktop_default_is_configured_without_writing_there(self):
        fake=self.root/'Redirected Desktop'
        with patch.object(module,'desktop_directory',return_value=fake):
            other=module.Store(self.root/'another-checkout')
            profile=other.init(message='帮我初始化求职助手',mode='precise')
        self.assertEqual(Path(profile['output_settings']['directory']),fake/'Codex Job Search')
        self.assertFalse(fake.exists())
        self.assertEqual(profile['language'],'zh')
        self.assertEqual(profile['application_mode'],'precise')

    def test_settings_survive_another_init_and_allow_explicit_change(self):
        self.store.configure(language='zh',mode='precise')
        self.store.init(language='en',mode='general',output_dir=self.root/'other')
        self.assertEqual(self.store.profile()['language'],'zh')
        self.assertEqual(self.store.profile()['application_mode'],'precise')
        self.store.configure(language='en',mode='general')
        self.assertEqual(self.store.profile()['language'],'en')
        self.assertEqual(self.store.profile()['application_mode'],'general')

    def test_report_is_real_multiline_markdown_in_selected_language(self):
        self.store.record(self.job,now=self.now)
        output=self.store.render(now=self.now)
        content=output.read_text(encoding='utf-8')
        self.assertGreater(len(content.splitlines()),15)
        self.assertIn('## Pending and other jobs',content)
        self.assertIn('Needs input',content)
        self.assertNotIn('待处理',content)
        self.store.configure(language='zh')
        self.assertEqual(self.store.render(now=self.now),output)
        chinese=output.read_text(encoding='utf-8')
        self.assertIn('待处理及其他岗位',chinese)
        self.assertNotIn('Pending and other jobs',chinese)

    def test_daily_record_uses_local_day_preserves_previous_days(self):
        item=self.store.record(self.job,now=self.now)
        self.store.render(now=self.now)
        first=self.out/'daily'/'2030-06-01.md'
        saved=first.read_bytes()
        later=datetime(2030,6,2,8,tzinfo=timezone.utc)
        self.store.record({**self.job,'status':'ready','blocking_items':[]},now=later)
        self.store.render(now=later)
        self.assertEqual(first.read_bytes(),saved)
        current=(self.out/'daily'/'2030-06-02.md').read_text(encoding='utf-8')
        self.assertIn(item['case_id'],current)
        self.assertIn('2030-06-02',current)
        self.assertIn('Ready',current)

    def test_same_day_refresh_updates_same_daily_file(self):
        self.store.record(self.job,now=self.now)
        self.store.render(now=self.now)
        self.store.record({**self.job,'notes':'Received new materials'},now=self.now)
        self.store.render(now=self.now)
        self.assertEqual(len(list((self.out/'daily').glob('*.md'))),1)
        self.assertIn('Received new materials',(self.out/'daily'/'2030-06-01.md').read_text(encoding='utf-8'))

    def test_short_case_survives_edits_and_link_lookup(self):
        first=self.store.record(self.job,now=self.now)
        self.assertEqual(first['case_id'],'J0001')
        self.store.record({**self.job,'notes':'Added detail'},now=self.now)
        self.assertEqual(self.store.lookup('j0001')['id'],first['id'])
        self.assertEqual(self.store.lookup(self.job['url']+'?utm_source=example')['case_id'],'J0001')
        other=self.store.record({**self.job,'url':'https://careers.example.invalid/jobs/2'},now=self.now)
        self.assertEqual(other['case_id'],'J0002')

    def test_resume_materials_reopen_only_that_case_without_resubmission(self):
        first=self.store.record(self.job,now=self.now)
        transcript=self.root/'transcript.txt'
        transcript.write_text('Synthetic academic record',encoding='utf-8')
        resumed=self.store.request_resume('J0001',[transcript],{'deadline':'None as confirmed for this case'},now=self.now)
        self.assertEqual(len(self.store.records()),1)
        self.assertEqual(resumed['id'],first['id'])
        self.assertEqual(resumed['status'],'needs_input')
        self.assertEqual(resumed['resume_request']['materials'],[str(transcript.resolve())])
        self.assertFalse(self.store.gate(self.job,self.now)[0])
        self.store.record({**self.job,'status':'ready','blocking_items':[]},now=self.now)
        self.assertTrue(self.store.gate(self.job,self.now)[0])

    def test_resume_never_reapplies_submitted_or_uncertain_case(self):
        self.store.record({**self.job,'status':'submission_unknown'},now=self.now)
        with self.assertRaises(ValueError):
            self.store.request_resume('J0001',now=self.now)
        self.store.record({**self.job,'status':'submitted','submitted_at':self.now.isoformat(),'submission_evidence':'Synthetic receipt'},now=self.now)
        with self.assertRaises(ValueError):
            self.store.request_resume('J0001',now=self.now)

    def test_legacy_migration_preserves_original_output_and_resume(self):
        profile=self.store.profile()
        profile['schema_version']=1
        profile['resume_path']='personal/resumes/original.pdf'
        for key in ('language','application_mode','resume_paths','output_settings'):
            profile.pop(key,None)
        module.write_json(self.store.profile_path,profile)
        item=self.store.record(self.job,now=self.now)
        records=self.store.records()
        records[0].pop('case_id')
        module.write_json(self.store.records_path,records)
        migrated=self.store.init()
        self.assertEqual(migrated['resume_paths'],['personal/resumes/original.pdf'])
        self.assertEqual(Path(migrated['output_settings']['directory']),self.store.root/'outputs')
        self.assertEqual(self.store.lookup('J0001')['id'],item['id'])

    def test_artifacts_are_grouped_by_local_date_and_case(self):
        self.store.record(self.job,now=self.now)
        target=self.store.artifact_directory('J0001',now=self.now)
        self.assertEqual(target,self.out/'2030-06-01'/'J0001')
        self.assertTrue(target.is_dir())

    def test_public_source_directory_cannot_receive_private_reports(self):
        self.store.configure(output_dir=self.store.root/'scripts')
        with self.assertRaises(ValueError):
            self.store.render(now=self.now)

    def test_multiple_resume_sources_are_preserved(self):
        profile=self.store.profile()
        profile['resume_paths']=['personal/resumes/full.pdf','personal/resumes/research.pdf']
        module.write_json(self.store.profile_path,profile)
        self.store.init()
        self.assertEqual(len(self.store.profile()['resume_paths']),2)


    def test_daily_new_submission_count_does_not_recount_old_outcomes(self):
        self.store.record({**self.job,'status':'submitted','submitted_at':self.now.isoformat(),'submission_evidence':'Synthetic receipt'},now=self.now)
        later=datetime(2030,6,2,8,tzinfo=timezone.utc)
        self.store.record({**self.job,'status':'interview'},now=later)
        self.store.render(now=later)
        daily=(self.out/'daily'/'2030-06-02.md').read_text(encoding='utf-8')
        self.assertIn('Confirmed submissions: **0**',daily)
        self.assertIn('Interview',daily)
        self.assertIn('Confirmed submissions: **1**',(self.out/'applications.md').read_text(encoding='utf-8'))

if __name__ == '__main__':
    unittest.main()
