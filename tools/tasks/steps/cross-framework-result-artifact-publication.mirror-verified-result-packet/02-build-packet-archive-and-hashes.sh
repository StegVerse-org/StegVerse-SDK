set -eu
cd /tmp
tar -czf cross-framework-current-basis-v0.4-results.tar.gz cross-framework-current-basis-v0.4-packet
sha256sum cross-framework-current-basis-v0.4-results.tar.gz > cross-framework-current-basis-v0.4-results.tar.gz.sha256
cat cross-framework-current-basis-v0.4-results.tar.gz.sha256
