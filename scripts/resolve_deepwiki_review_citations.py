#!/usr/bin/env python3
"""Create source-pinned DeepWiki citation candidates without publication.

Checks repository-relative paths and numeric bounds against a checked-out source
revision. Does not establish semantic correctness, indexing parity or reuse rights.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote

SIMPLE = re.compile(r'\[([^\]\n]{1,200})\]\(\)')
LOCATOR = re.compile(r'^`?([A-Za-z0-9_.\-/]+\.[A-Za-z0-9]+):(\d+)(?:-(\d+))?`?$')
PATH_ONLY = re.compile(r'^`?([A-Za-z0-9_.\-/]+\.[A-Za-z0-9]+)`?$')
SHA = re.compile(r'^[0-9a-f]{40}$')


def resolve_label(label: str, root: Path, revision: str) -> tuple[str | None, str, str | None]:
    """Return a candidate only when its file and declared numerical span exist."""
    locator = LOCATOR.fullmatch(label)
    bare = PATH_ONLY.fullmatch(label) if not locator else None
    if locator:
        raw_path, start_raw, end_raw = locator.groups()
    elif bare:
        raw_path = bare.group(1)
        start_raw = end_raw = None
    else:
        return None, 'AMBIGUOUS_LABEL_OR_NONNUMERIC_SYMBOL', None
    path = Path(raw_path)
    if path.is_absolute() or not raw_path or any(p in ('..', '') for p in raw_path.split('/')):
        return None, 'UNSAFE_OR_AMBIGUOUS_PATH', raw_path
    repo = root.resolve()
    target = (repo / path).resolve()
    if not target.is_relative_to(repo) or not target.is_file():
        return None, 'SOURCE_FILE_NOT_FOUND', raw_path
    try:
        lines = target.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeError):
        return None, 'SOURCE_NOT_READABLE_TEXT', raw_path
    url = 'https://github.com/StegVerse-org/StegVerse-SDK/blob/' + revision + '/' + quote(path.as_posix(), safe='/')
    if start_raw:
        a = int(start_raw)
        b = int(end_raw or start_raw)
        if a < 1 or b < a or b > len(lines):
            return None, 'SOURCE_LINE_OUT_OF_RANGE', raw_path
        url += f'#L{a}' + (f'-L{b}' if b != a else '')
        return url, 'VALID_SOURCE_LINE_CANDIDATE_SEMANTICS_UNREVIEWED', raw_path
    return url, 'VALID_SOURCE_FILE_CANDIDATE_SEMANTICS_UNREVIEWED', raw_path


def audit(markdown: str, root: Path, revision: str) -> tuple[str, dict]:
    if not SHA.fullmatch(revision):
        raise ValueError('Expected pinned 40-character lowercase source SHA')
    headers = [(m.start(), m.group(1)) for m in re.finditer(r'^# Page:\s*(.+?)\s*$', markdown, re.M)]
    offsets = [x[0] for x in headers]
    rows = []

    def replace(match: re.Match) -> str:
        label = match.group(1)
        url, disposition, candidate_path = resolve_label(label, root, revision)
        i = bisect.bisect_right(offsets, match.start()) - 1
        rows.append({
            'offset': match.start(), 'page': headers[i][1] if i >= 0 else None,
            'label': label, 'candidate_path': candidate_path,
            'disposition': disposition, 'candidate_url': url,
        })
        return f'[{label}]({url})' if url else match.group(0)

    candidate = SIMPLE.sub(replace, markdown)
    literal_count = markdown.count(']()')
    grouped = {}
    for row in rows:
        grouped[row['disposition']] = grouped.get(row['disposition'], 0) + 1
    return candidate, {
        'schema': 'stegverse.deepwiki-citation-review/v1',
        'source_revision': revision,
        'input_sha256': hashlib.sha256(markdown.encode('utf-8')).hexdigest(),
        'candidate_sha256': hashlib.sha256(candidate.encode('utf-8')).hexdigest(),
        'input_empty_targets': literal_count,
        'simple_labels': len(rows),
        'non_simple_occurrences': literal_count - len(rows),
        'candidate_source_links': sum(bool(x['candidate_url']) for x in rows),
        'remaining_empty_targets': candidate.count(']()'),
        'dispositions': grouped, 'entries': rows,
        'source_revision_parity_with_deepwiki': 'UNKNOWN',
        'semantic_source_verification': 'NOT_PERFORMED',
        'reuse_rights_verified': False, 'publication_allowed': False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--revision', required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    source = a.input.read_text(encoding='utf-8')
    candidate, report = audit(source, a.root, a.revision)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / 'citation-candidates-UNREVIEWED.md').write_text(candidate, encoding='utf-8')
    (a.out / 'citation-review-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in (
        'input_empty_targets', 'candidate_source_links',
        'remaining_empty_targets', 'dispositions', 'publication_allowed'
    )}, sort_keys=True))


if __name__ == '__main__':
    main()
