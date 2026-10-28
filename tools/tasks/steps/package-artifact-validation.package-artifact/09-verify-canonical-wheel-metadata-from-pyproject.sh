set -eu
cd /tmp/source
python - <<'PY'
import email
import pathlib
import tomllib
import zipfile

project = tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']
expected_name = project['name']
expected_version = project['version']
expected_python = project['requires-python']
expected_scripts = project.get('scripts', {})

wheels = list(pathlib.Path('dist').glob('*.whl'))
if len(wheels) != 1:
    raise SystemExit(f'EXPECTED_ONE_WHEEL:{wheels!r}')
wheel = wheels[0]
with zipfile.ZipFile(wheel) as zf:
    metadata_name = next(n for n in zf.namelist() if n.endswith('.dist-info/METADATA'))
    entry_name = next(n for n in zf.namelist() if n.endswith('.dist-info/entry_points.txt'))
    metadata = email.message_from_bytes(zf.read(metadata_name))
    entries = zf.read(entry_name).decode('utf-8')

assert metadata['Name'] == expected_name, (metadata['Name'], expected_name)
assert metadata['Version'] == expected_version, (metadata['Version'], expected_version)
assert metadata['Requires-Python'] == expected_python, (metadata['Requires-Python'], expected_python)
requires = metadata.get_all('Requires-Dist') or []
required_fragments = ()
# Removed 2026-10-13: pyyaml and python-dotenv were never imported; requests is
# replaced by the standard library. Dependencies are reduced, never added back.
removed_fragments = ('pyyaml', 'python-dotenv', 'requests')
compact = [r.replace(' ', '') for r in requires]
for expected in required_fragments:
    if not any(expected in r for r in compact):
        raise SystemExit(f'MISSING_REQUIRES_DIST:{expected}:{requires!r}')
for removed in removed_fragments:
    if any(r.lower().startswith(removed) for r in compact):
        raise SystemExit(f'REMOVED_DEPENDENCY_REINTRODUCED:{removed}:{requires!r}')
for script, target in expected_scripts.items():
    expected = f'{script} = {target}'
    if expected not in entries:
        raise SystemExit(f'MISSING_ENTRY_POINT:{expected}')
print('SDK_WHEEL_METADATA_MATCHES_PYPROJECT_PASS', expected_version)
PY
