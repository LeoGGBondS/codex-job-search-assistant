#!/usr/bin/env python3
# Local records only: this module never logs into sites or submits applications.
import argparse
import hashlib
import json
import os
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

    def init(self):
        self.personal.mkdir(parents=True, exist_ok=True)
        (self.personal / 'resumes').mkdir(exist_ok=True)
        (self.root / 'outputs').mkdir(exist_ok=True)
        (self.root / 'work').mkdir(exist_ok=True)
        blank = {
            'schema_version': 1, 'onboarding_complete': False,
            'name': None, 'email': None, 'phone': None, 'resume_path': None,
            'target_job_types': [], 'target_roles': [], 'target_countries': [],
            'target_locations': [], 'remote': None, 'relocation': None,
            'availability': None, 'education': [],
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
        return self.profile()

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
        for record in value:
            validate_record(record)
            if not record.get('id') or record['id'] in seen:
                raise ValueError('Missing or duplicate record id')
            seen.add(record['id'])
        return value

    def record(self, incoming):
        candidate = dict(incoming)
        records = self.records()
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
            updated = {**previous, **candidate}
            updated['id'] = previous['id']
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

    def render(self):
        records = self.records()
        def clean(value):
            return str(value if value is not None else '-').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
        labels = {'discovered':'已发现', 'screened':'已筛选', 'skipped':'主动跳过',
                  'drafted':'材料已准备', 'needs_input':'待处理', 'ready':'待投递',
                  'submitted':'已提交', 'submission_unknown':'结果待核实',
                  'rejected':'已收到拒信', 'interview':'进入面试', 'withdrawn':'已撤回'}
        submitted = sum(bool(x.get('submitted_at')) for x in records)
        lines = ['# 求职投递记录 / Application log', '',
                 'Updated (UTC): ' + datetime.now(timezone.utc).isoformat(timespec='seconds'), '',
                 f'已确认提交 / Confirmed submissions: **{submitted}**', '',
                 '| 公司 / Company | 岗位 / Role | 状态 / Status | 提交时间 / Submitted | 岗位 / URL | 简历 / Resume | 凭证 / Evidence | 备注 / Notes |',
                 '|---|---|---|---|---|---|---|---|']
        for item in sorted(records, key=lambda x:x.get('submitted_at') or '', reverse=True):
            fields = [item.get('company'), item.get('role'), labels[item['status']], item.get('submitted_at'),
                      item.get('url'), item.get('resume_path'), item.get('submission_evidence'), item.get('notes')]
            lines.append('| ' + ' | '.join(clean(x) for x in fields) + ' |')
        if not records:
            lines.append('| 暂无记录 / No records | - | - | - | - | - | - | - |')
        lines += ['', '只有明确确认收到的申请才计为已提交；结果不明不会自动重投。',
                  'Only verified receipts count as submitted. An uncertain result is not retried automatically.', '']
        output = self.root / 'outputs' / 'applications.md'
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix('.md.tmp')
        temporary.write_text('\n'.join(lines), encoding='utf-8')
        os.replace(temporary, output)
        return output


def main():
    parser = argparse.ArgumentParser(description='Local profile and application log helper; no web submission')
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'status', 'render'):
        commands.add_parser(name)
    for name in ('record', 'gate'):
        child = commands.add_parser(name)
        child.add_argument('--file', type=Path, required=True)
    args = parser.parse_args()
    store = Store(args.workspace)
    try:
        if args.command == 'init':
            store.init()
            print('Blank local state initialized; existing data was preserved. Continue onboarding in Codex.')
        elif args.command == 'status':
            profile = store.profile()
            print(json.dumps({'onboarding_complete': profile.get('onboarding_complete', False),
                              'application_count': len(store.records()),
                              'schedule_enabled': profile.get('schedule', {}).get('enabled', False)}, indent=2))
        elif args.command == 'render':
            store.render()
            print('Updated outputs/applications.md')
        elif args.command == 'record':
            item = store.record(load_json(args.file))
            store.render()
            print('Saved application record: ' + item['id'])
        elif args.command == 'gate':
            allowed, reason = store.gate(load_json(args.file))
            print(reason)
            return 0 if allowed else 2
        return 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
