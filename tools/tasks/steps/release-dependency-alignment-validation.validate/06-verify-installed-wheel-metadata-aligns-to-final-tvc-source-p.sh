set -eu
/tmp/alignment-venv/bin/python - <<'PY'
from stegverse.release_dependency_alignment import verify_installed_governed_test_dependency_alignment

final_receipt = {
    'components': [
        {'repository': 'StegVerse-Labs/StegCore', 'commit_sha': '1'*40, 'source_parent_commit': 'ef38410505b0ef3e84148892b1d6e3cdef20f300'},
        {'repository': 'Data-Continuation/core-lite', 'commit_sha': '2'*40, 'source_parent_commit': '72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8'},
    ]
}
pre_tvc = {
    'components': [
        {'repository': 'StegVerse-Labs/StegCore', 'commit_sha': '4'*40, 'source_parent_commit': '124ea6b53ff79db8f514cacf1aab295f03cacf74'},
        {'repository': 'Data-Continuation/core-lite', 'commit_sha': '2'*40, 'source_parent_commit': '72bdb0f110031ccc2cd98b8ebb7c22b1ab7326f8'},
    ]
}
ok = verify_installed_governed_test_dependency_alignment(final_receipt)
assert ok['verified'] is True, ok
mismatch = verify_installed_governed_test_dependency_alignment(pre_tvc)
assert mismatch['verified'] is False, mismatch
assert 'stegcore:commit_mismatch' in mismatch['reasons'], mismatch
assert not [r for r in ok['reasons'] if r.startswith('unexpected_governed_test_git_pin')], ok
print('INSTALLED_FINAL_TVC_RELEASE_DEPENDENCY_ALIGNMENT_PASS')
PY
