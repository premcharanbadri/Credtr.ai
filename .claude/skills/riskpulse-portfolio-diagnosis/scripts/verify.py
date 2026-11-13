#!/usr/bin/env python3
"""RiskPulse synthetic portfolio diagnostic; stdlib only, no API, no remote data."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import time
from collections import defaultdict
from pathlib import Path

NEEDED = {"account_id", "snapshot_month", "cohort", "dpd30_next_60d", "utilization", "missed_payments_3m"}

def summarize(path: Path, start: str = "2024-12", end: str = "2025-03") -> dict:
    t0 = time.perf_counter()
    months: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    cohort: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    flags: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    ids: set[str] = set()
    keys: set[tuple[str, str]] = set()
    bad_keys = 0
    missing_required = 0
    full_rows = 0
    full_months: set[str] = set()
    test_rows = test_events = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = NEEDED - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        for row in reader:
            full_rows += 1
            acc, month = row['account_id'], row['snapshot_month']
            ids.add(acc)
            full_months.add(month)
            key = (acc, month)
            if key in keys:
                bad_keys += 1
                continue  # count each account-month once; duplicates are flagged, not double-counted
            keys.add(key)
            if any(row.get(k, '') in ('', None) for k in NEEDED):
                missing_required += 1
                continue
            if not (start <= month <= end):
                continue
            event = int(row['dpd30_next_60d'])
            if event not in (0, 1): raise ValueError(f"Invalid target value at row {full_rows}")
            test_rows += 1
            test_events += event
            months[month][0] += 1
            months[month][1] += event
            cohort[row['cohort']][0] += 1
            cohort[row['cohort']][1] += event
            high_util = float(row['utilization']) >= .85
            missed = float(row['missed_payments_3m']) >= 1
            g = f"util85={int(high_util)},missed_payment={int(missed)}"
            flags[g][0] += 1
            flags[g][1] += event
    def compact(d: dict[str, list[int]]):
        return {k:{'observations':v[0],'events':v[1],'event_rate': round(v[1]/v[0],8) if v[0] else None}
                for k,v in sorted(d.items())}
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    return {'source_sha256': digest, 'total_rows': full_rows,
            'unique_accounts': len(ids), 'snapshot_months': len(full_months),
            'duplicate_account_month_keys': bad_keys, 'rows_missing_required_fields': missing_required,
            'test_window': [start, end], 'test_rows': test_rows, 'test_events': test_events,
            'test_event_rate': round(test_events/test_rows,8) if test_rows else None,
            'monthly': compact(months), 'cohort': compact(cohort),
            'utilization_missed_payment_groups': compact(flags),
            'local_processing_seconds': round(time.perf_counter()-t0,4),
            'limitations': ['synthetic data','account-month observations repeated by account',
                            'event=30+ DPD next 60d, not default','no fitted-model predictions or causal outreach effect']}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', required=True, type=Path)
    p.add_argument('--start', default='2024-12')
    p.add_argument('--end', default='2025-03')
    p.add_argument('--out', type=Path)
    args = p.parse_args()
    result = summarize(args.data, args.start, args.end)
    encoded = json.dumps(result, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded + '\n', encoding='utf-8')
    print(encoded)

if __name__=='__main__':main()
