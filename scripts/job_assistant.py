#!/usr/bin/env python3
# Local records only: this module never logs into sites or submits applications.
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import sys
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

STATUSES = {'discovered', 'screened', 'skipped', 'drafted', 'needs_input', 'ready',
            'submitted', 'submission_unknown', 'rejected', 'interview', 'withdrawn'}
OUTCOMES = {'rejected', 'interview', 'withdrawn'}
TRACKING = {'gh_src', 'source', 'ref', 'refid', 'trackingid', 'lever-source'}


def load_json(path, default=None):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('submitted_at must include a timezone offset')
    return parsed


def canonical_url(value):
    parts = urlsplit(value)
    if parts.scheme.lower() != 'https' or not parts.hostname or parts.username or parts.password:
        raise ValueError('Job URL must be HTTPS and must not contain credentials')
    if parts.port not in (None, 443):
        raise ValueError('Unexpected job URL port')
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if k.lower() not in TRACKING and not k.lower().startswith('utm_')]
    return urlunsplit(('https', parts.hostname.lower(), parts.path.rstrip('/') or '/',
                       urlencode(sorted(query)), ''))



def desktop_directory():
    # Resolve redirected Windows Desktops and Linux XDG paths without running shell text.
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders') as key:
                value, _ = winreg.QueryValueEx(key, 'Desktop')
            return Path(os.path.expandvars(value)).expanduser().resolve()
        except (ImportError, OSError):
            pass
    if sys.platform.startswith('linux'):
        config = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config'))) / 'user-dirs.dirs'
        if config.exists():
            match = re.search(r'^XDG_DESKTOP_DIR="([^"]+)"', config.read_text(encoding='utf-8'), re.MULTILINE)
            if match:
                value = match.group(1).replace('$HOME', str(Path.home()))
                return Path(os.path.expandvars(value)).expanduser().resolve()
    return (Path.home() / 'Desktop').resolve()


def infer_language(message='', explicit=None):
    if explicit is not None:
        if explicit not in {'en', 'zh'}:
            raise ValueError('Language must be en or zh')
        return explicit
    return 'zh' if re.search(r'[\u3400-\u9fff]', message or '') else 'en'


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(text, encoding='utf-8')
    os.replace(temporary, path)


def company_key(value):
    return ' '.join(value.casefold().split())


def same_job(left, right):
    if left.get('job_id') and right.get('job_id'):
        if (company_key(left['company']) == company_key(right['company'])
                and str(left['job_id']) == str(right['job_id'])):
            return True
    return canonical_url(left['url']) == canonical_url(right['url'])


def validate_record(item):
    if not isinstance(item, dict):
        raise ValueError('Application must be a JSON object')
    for key in ('company', 'role', 'url', 'status'):
        if not isinstance(item.get(key), str) or not item[key].strip():
            raise ValueError('Missing application field: ' + key)
    if item['status'] not in STATUSES:
        raise ValueError('Unknown application status')
    item['url'] = canonical_url(item['url'])
    if item.get('job_id') is not None:
        item['job_id'] = str(item['job_id'])
    if item.get('submitted_at'):
        timestamp(item['submitted_at'])
        if not item.get('submission_evidence'):
            raise ValueError('Submission timestamp requires receipt evidence')
    if item['status'] == 'submitted' and not (item.get('submitted_at') and item.get('submission_evidence')):
        raise ValueError('Submitted records require timestamp and confirmation evidence')
    return item


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.personal = self.root / 'personal'
        self.profile_path = self.personal / 'profile.json'
        self.records_path = self.personal / 'applications.json'

    def init(self, language=None, mode=None, output_dir=None, message=None):
        if mode is not None and mode not in {'general', 'precise'}:
            raise ValueError('Mode must be general or precise')
        self.personal.mkdir(parents=True, exist_ok=True)
        (self.personal / 'resumes').mkdir(exist_ok=True)
        (self.root / 'outputs').mkdir(exist_ok=True)
        (self.root / 'work').mkdir(exist_ok=True)
        blank = {
            'schema_version': 2, 'onboarding_complete': False,
            'language': infer_language(message, language),
            'application_mode': mode or 'general', 'resume_paths': [],
            'output_settings': {'directory': str(Path(output_dir).expanduser().resolve() if output_dir is not None else desktop_directory()/'Codex Job Search')},
            'name': None, 'email': None, 'phone': None, 'resume_path': None,
            'target_job_types': [], 'target_roles': [], 'target_countries': [],
            'target_locations': [], 'remote': None, 'relocation': None,
            'availability': None, 'education': [],
            'current_location': {'city': None, 'region': None, 'country': None},
            'preference_policy': {'resume_based_ranking': None, 'engineering_ranking': [], 'office_ranking': []},
            'application_answers': {},
            'work_authorization': {}, 'sponsorship_required': {},
            'gpa': {'actual': None, 'estimated': None, 'scale': None, 'source': None},
            'schedule': {'enabled': False, 'timezone': None, 'local_time': None,
                         'max_submissions_per_day': None, 'automation_id': None}
        }
        for path, value in ((self.profile_path, blank), (self.records_path, []),
                            (self.personal / 'consents.json', [])):
            if not path.exists():
                write_json(path, value)
        experience = self.personal / 'experience.md'
        if not experience.exists():
            experience.write_text('# Candidate evidence\n\nOnly add facts from this user and their supplied resume.\n', encoding='utf-8')
        profile = self.profile()
        # Old installations keep their existing output folder until explicitly reconfigured.
        if profile.get('schema_version', 1) < 2:
            profile.setdefault('language', infer_language(message, language))
            profile.setdefault('application_mode', 'general')
            profile.setdefault('resume_paths', [profile['resume_path']] if profile.get('resume_path') else [])
            profile.setdefault('output_settings', {'directory': str(self.root/'outputs')})
            profile['schema_version'] = 2
            write_json(self.profile_path, profile)
        records = self.records()
        if records:
            write_json(self.records_path, records)
        return profile

    def profile(self):
        value = load_json(self.profile_path)
        if not isinstance(value, dict):
            raise ValueError('Run init and complete candidate onboarding first')
        return value

    def records(self):
        value = load_json(self.records_path, [])
        if not isinstance(value, list):
            raise ValueError('Application store must contain an array')
        seen = set()
        seen_cases = set()
        case_ids = {x.get('case_id') for x in value if isinstance(x, dict) and x.get('case_id')}
        next_case = max([int(x[1:]) for x in case_ids if re.fullmatch(r'J[0-9]{4,}', x)] or [0]) + 1
        for record in value:
            if not record.get('case_id'):
                record['case_id'] = 'J' + str(next_case).zfill(4)
                next_case += 1
            validate_record(record)
            if not record.get('id') or record['id'] in seen:
                raise ValueError('Missing or duplicate record id')
            seen.add(record['id'])
            if not re.fullmatch(r'J[0-9]{4,}', record['case_id']) or record['case_id'] in seen_cases:
                raise ValueError('Invalid or duplicate case ID')
            seen_cases.add(record['case_id'])
        return value

    def record(self, incoming, now=None):
        candidate = dict(incoming)
        records = self.records()
        changed_at = (now or datetime.now(timezone.utc)).isoformat(timespec='seconds')
        timestamp(changed_at)
        # Validate required identity before attempting deduplication.
        for key in ('company', 'role', 'url', 'status'):
            if not candidate.get(key):
                raise ValueError('Missing application field: ' + key)
        candidate['url'] = canonical_url(candidate['url'])
        matches = [i for i, old in enumerate(records) if same_job(old, candidate)]
        if len(matches) > 1:
            raise ValueError('Multiple existing records match; reconcile before updating')
        if matches:
            index = matches[0]
            previous = records[index]
            if candidate.get('id') and candidate['id'] != previous['id']:
                raise ValueError('Cannot change an existing job record ID')
            if previous.get('submitted_at') and candidate['status'] not in {'submitted'} | OUTCOMES:
                raise ValueError('Cannot reset a submitted application to a pending state')
            if previous['status'] == 'submission_unknown' and candidate['status'] not in {'submission_unknown', 'submitted', 'withdrawn'}:
                raise ValueError('Uncertain submission requires verification, not an automatic retry')
            for key in ('submitted_at', 'submission_evidence'):
                if previous.get(key):
                    if key in candidate and candidate[key] != previous[key]:
                        raise ValueError('Cannot erase or change recorded submission receipt')
                    candidate[key] = previous[key]
            if candidate.get('case_id') and candidate['case_id'] != previous['case_id']:
                raise ValueError('Cannot change an existing case ID')
            updated = {**previous, **candidate}
            updated['id'] = previous['id']
            updated['case_id'] = previous['case_id']
            updated['created_at'] = previous.get('created_at')
            updated['updated_at'] = changed_at
            validate_record(updated)
            records[index] = updated
        else:
            validate_record(candidate)
            identity = company_key(candidate['company']) + ':' + str(candidate.get('job_id') or candidate['url'])
            candidate.setdefault('id', hashlib.sha256(identity.encode()).hexdigest()[:20])
            if not isinstance(candidate['id'], str) or not candidate['id'].strip():
                raise ValueError('Record id must be a nonempty string')
            if any(x['id'] == candidate['id'] for x in records):
                raise ValueError('Record ID already belongs to another job')
            sequence = max([int(x['case_id'][1:]) for x in records] or [0]) + 1
            case_id = 'J' + str(sequence).zfill(4)
            if candidate.get('case_id') and candidate['case_id'] != case_id:
                raise ValueError('Case IDs are allocated by the local store')
            candidate['case_id'] = case_id
            candidate['created_at'] = changed_at
            candidate['updated_at'] = changed_at
            records.append(candidate)
        write_json(self.records_path, records)
        return next(x for x in records if same_job(x, candidate))

    def gate(self, candidate, now=None):
        # Local guard only; browser permissions and eligibility are separate checks.
        for key in ('company', 'url'):
            if not candidate.get(key):
                raise ValueError('Missing application field: ' + key)
        candidate = {**candidate, 'url': canonical_url(candidate['url'])}
        records = self.records()
        for previous in records:
            if same_job(previous, candidate):
                if previous['status'] == 'needs_input':
                    return False, 'Review the missing materials/answers and mark this case ready before submitting'
                if previous.get('submitted_at') or previous['status'] in {
                    'submitted', 'submission_unknown', 'withdrawn', 'rejected', 'interview', 'skipped'
                }:
                    return False, 'Existing application or stop status; inspect instead of submitting again'
        schedule = self.profile().get('schedule', {})
        cap = schedule.get('max_submissions_per_day')
        if not isinstance(cap, int) or isinstance(cap, bool) or cap < 1:
            return False, 'Choose a positive daily cap before submitting (one is valid for a single manual run)'
        zone_name = schedule.get('timezone')
        if not zone_name:
            return False, 'Choose the candidate timezone before counting daily submissions'
        try:
            zone = ZoneInfo(zone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError('Invalid/unavailable IANA timezone; check spelling or install tzdata') from exc
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError('Current time must have timezone information')
        today = now.astimezone(zone).date()
        count = sum(1 for x in records if x.get('submitted_at')
                    and timestamp(x['submitted_at']).astimezone(zone).date() == today)
        if count >= cap:
            return False, 'Daily submission cap reached'
        return True, f'Local checks passed ({count}/{cap} today); verify consent, eligibility and page state separately'

    def configure(self, language=None, mode=None, output_dir=None):
        profile = self.profile()
        if language is not None:
            profile['language'] = infer_language(explicit=language)
        if mode is not None:
            if mode not in {'general', 'precise'}:
                raise ValueError('Mode must be general or precise')
            profile['application_mode'] = mode
        if output_dir is not None:
            target = desktop_directory()/'Codex Job Search' if str(output_dir) == 'desktop' else Path(output_dir).expanduser().resolve()
            profile['output_settings'] = {'directory': str(target)}
        write_json(self.profile_path, profile)
        return profile

    def lookup(self, reference):
        records = self.records()
        if reference.lower().startswith('https://'):
            url = canonical_url(reference)
            matches = [x for x in records if canonical_url(x['url']) == url]
        else:
            matches = [x for x in records if x['id'] == reference or x['case_id'].upper() == reference.upper()]
        if len(matches) != 1:
            raise ValueError('No unique case found; use its case ID or original job link')
        return matches[0]

    def request_resume(self, reference, materials=None, answers=None, now=None):
        item = self.lookup(reference)
        if item.get('submitted_at') or item['status'] in {'submitted', 'submission_unknown', 'interview', 'rejected', 'withdrawn'}:
            raise ValueError('Verify existing submission/outcome; this case cannot be automatically reapplied')
        if answers is not None and not isinstance(answers, dict):
            raise ValueError('Resume answers must be a JSON object of user-confirmed answers')
        paths = []
        for material in materials or []:
            path = Path(material).expanduser().resolve()
            if not path.is_file():
                raise ValueError('Provided material is not a local file')
            paths.append(str(path))
        item['resume_request'] = {'requested_at': (now or datetime.now(timezone.utc)).isoformat(timespec='seconds'),
                                  'materials': paths, 'answers': answers or {}}
        # Remain pending until the agent re-reads the JD and resolves each blocker.
        item['status'] = 'needs_input'
        return self.record(item, now=now)

    def report_root(self):
        settings = self.profile().get('output_settings') or {}
        target = Path(settings.get('directory') or self.root/'outputs').expanduser().resolve()
        if target.is_relative_to(self.root) and not target.is_relative_to(self.root/'outputs'):
            raise ValueError('Reports must be outside the public source tree or under ignored outputs/')
        return target

    def local_time(self, now=None):
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError('Current time must include timezone information')
        zone_name = self.profile().get('schedule', {}).get('timezone')
        try:
            zone = ZoneInfo(zone_name) if zone_name else timezone.utc
        except ZoneInfoNotFoundError as exc:
            raise ValueError('Invalid/unavailable IANA timezone; check spelling or install tzdata') from exc
        return now.astimezone(zone)

    def artifact_directory(self, reference, now=None):
        case = self.lookup(reference)
        target = self.report_root()/self.local_time(now).date().isoformat()/case['case_id']
        target.mkdir(parents=True, exist_ok=True)
        return target

    def render(self, now=None):
        records = self.records()
        profile = self.profile()
        language = profile.get('language', 'en')
        if language not in {'en', 'zh'}:
            raise ValueError('Choose report language en or zh')
        local = self.local_time(now)
        day = local.date().isoformat()
        zh = language == 'zh'
        text = {
            'title': '求职记录' if zh else 'Application log',
            'updated': '更新时间' if zh else 'Updated',
            'date': '日期' if zh else 'Date',
            'count': '已确认投递' if zh else 'Confirmed submissions',
            'submitted': '已投递及后续结果' if zh else 'Submitted applications and outcomes',
            'pending': '待处理及其他岗位' if zh else 'Pending and other jobs',
            'daily': '每日记录' if zh else 'Daily record',
            'empty': '暂无记录' if zh else 'No records',
            'headers': ['编号','公司','岗位','状态','提交时间','更新时间','岗位链接','简历','凭证','待补材料 / 备注'] if zh else
                       ['Case','Company','Role','Status','Submitted','Updated','Job URL','Resume','Evidence','Missing materials / notes'],
            'footer': '继续处理：发送“继续 J0001”并附上所缺材料。也支持原岗位链接。已投递或结果不明的岗位先核实，不自动重投。' if zh else
                      'To resume, say "Resume J0001" and attach the missing materials. The original job link also works. Submitted or uncertain cases require verification, never automatic reapplication.'
        }
        labels = ({'discovered':'已发现','screened':'已筛选','skipped':'主动跳过','drafted':'材料已准备',
                   'needs_input':'待处理','ready':'待投递','submitted':'已提交','submission_unknown':'结果待核实',
                   'rejected':'已收到拒信','interview':'进入面试','withdrawn':'已撤回'} if zh else
                  {'discovered':'Discovered','screened':'Screened','skipped':'Skipped','drafted':'Drafted',
                   'needs_input':'Needs input','ready':'Ready','submitted':'Submitted','submission_unknown':'Receipt unverified',
                   'rejected':'Rejected','interview':'Interview','withdrawn':'Withdrawn'})
        def clean(value):
            return str(value if value is not None else '-').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('|','\\|').replace('\n',' ').replace('\r',' ')
        def stamp(value):
            return timestamp(value).astimezone(local.tzinfo).isoformat(timespec='seconds') if value else None
        def table(items):
            lines = ['| '+' | '.join(text['headers'])+' |', '|'+'|'.join(['---']*10)+'|']
            for item in sorted(items, key=lambda x:x.get('updated_at') or x.get('submitted_at') or '', reverse=True):
                missing = item.get('blocking_items') or []
                missing = '; '.join(x if isinstance(x,str) else x.get('description',x.get('name','')) for x in missing)
                notes = '; '.join(x for x in [missing,item.get('notes')] if x)
                fields = [item['case_id'],item['company'],item['role'],labels[item['status']],stamp(item.get('submitted_at')),
                          stamp(item.get('updated_at')),item['url'],item.get('resume_path'),item.get('submission_evidence'),notes]
                lines.append('| '+' | '.join(clean(x) for x in fields)+' |')
            if not items:
                lines.append('| '+text['empty']+' | '+' | '.join(['-']*9)+' |')
            return lines
        def report(items, daily=False):
            submitted = [x for x in items if x.get('submitted_at')]
            pending = [x for x in items if not x.get('submitted_at')]
            title = text['daily']+' — '+day if daily else text['title']
            receipt_count = sum(1 for x in submitted if not daily or timestamp(x['submitted_at']).astimezone(local.tzinfo).date() == local.date())
            return '\n'.join(['# '+title,'',text['date']+': '+day,'',text['updated']+': '+local.isoformat(timespec='seconds'),'',
                              text['count']+': **'+str(receipt_count)+'**','',
                              '## '+text['submitted'],'',*table(submitted),'','## '+text['pending'],'',*table(pending),'',text['footer'],''])
        touched = [x for x in records if any(timestamp(x[k]).astimezone(local.tzinfo).date() == local.date()
                   for k in ('created_at','updated_at','submitted_at') if x.get(k))]
        output = self.report_root()/'applications.md'
        atomic_text(output, report(records))
        atomic_text(output.parent/'daily'/(day+'.md'), report(touched,daily=True))
        return output


def main():
    parser = argparse.ArgumentParser(description='Local job-search profiles and records; no web submission')
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('init','configure'):
        child = commands.add_parser(name)
        child.add_argument('--language',choices=['en','zh'])
        child.add_argument('--mode',choices=['general','precise'])
        child.add_argument('--output-dir')
        if name == 'init':
            child.add_argument('--message',default='')
    for name in ('status','render'):
        commands.add_parser(name)
    for name in ('record','gate'):
        commands.add_parser(name).add_argument('--file',type=Path,required=True)
    for name in ('lookup','resume','artifact-dir'):
        child=commands.add_parser(name)
        child.add_argument('reference')
        if name == 'resume':
            child.add_argument('--material',action='append',default=[])
            child.add_argument('--answers-file',type=Path)
    args=parser.parse_args()
    store=Store(args.workspace)
    try:
        if args.command == 'init':
            output_dir = desktop_directory()/'Codex Job Search' if args.output_dir == 'desktop' else args.output_dir
            profile=store.init(args.language,args.mode,output_dir,args.message)
            print(json.dumps({'onboarding_complete':profile.get('onboarding_complete',False),'language':profile.get('language'),
                              'application_mode':profile.get('application_mode'),'output_directory':profile.get('output_settings',{}).get('directory')},ensure_ascii=True))
        elif args.command == 'configure':
            store.configure(args.language,args.mode,args.output_dir)
            print('Preferences updated; existing reports and records preserved.')
        elif args.command == 'status':
            profile=store.profile()
            print(json.dumps({'onboarding_complete':profile.get('onboarding_complete',False),'application_count':len(store.records()),
                              'schedule_enabled':profile.get('schedule',{}).get('enabled',False),'language':profile.get('language','en'),
                              'application_mode':profile.get('application_mode','general'),'output_directory':str(store.report_root())},ensure_ascii=True))
        elif args.command == 'render':
            print(json.dumps({'report':str(store.render())},ensure_ascii=True))
        elif args.command == 'record':
            item=store.record(load_json(args.file))
            store.render()
            print('Saved case '+item['case_id'])
        elif args.command == 'gate':
            allowed,reason=store.gate(load_json(args.file))
            print(reason)
            return 0 if allowed else 2
        elif args.command == 'lookup':
            print(json.dumps(store.lookup(args.reference),ensure_ascii=True,separators=(',',':')))
        elif args.command == 'resume':
            answers=load_json(args.answers_file) if args.answers_file else None
            item=store.request_resume(args.reference,args.material,answers)
            store.render()
            print(json.dumps(item,ensure_ascii=True,separators=(',',':')))
        elif args.command == 'artifact-dir':
            print(json.dumps({'directory':str(store.artifact_directory(args.reference))},ensure_ascii=True))
        return 0
    except (ValueError,TypeError,KeyError,OSError) as exc:
        print('Error: '+str(exc),file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
