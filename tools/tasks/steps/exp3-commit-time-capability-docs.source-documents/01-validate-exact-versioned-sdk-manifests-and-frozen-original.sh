python -m unittest tests.test_mir_sv_exp3_capability_documents -v
python -m scripts.build_mir_sv_exp3_capability_documents --output-dir /tmp/mir-exp3-documents
python -m json.tool /tmp/mir-exp3-documents/primary.manifest.json >/dev/null
python -m json.tool /tmp/mir-exp3-documents/addendum.manifest.json >/dev/null
sha256sum /tmp/mir-exp3-documents/*
echo 'Source-only documents. No native authority, Publisher or MIR delivery claimed.'
