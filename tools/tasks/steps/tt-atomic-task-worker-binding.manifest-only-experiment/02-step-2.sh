python -m pip install -e '.[dev]'
python -m pip freeze | LC_ALL=C sort > /tmp/pip-freeze.txt
: > /tmp/experiment-stage-results.log
