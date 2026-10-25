set -eu
cd /tmp/source
python -m py_compile \
  stegverse/llm_connection.py \
  stegverse/llm_connect_cli.py \
  stegverse/sdk_surfaces.py \
  tests/test_llm_connection.py
