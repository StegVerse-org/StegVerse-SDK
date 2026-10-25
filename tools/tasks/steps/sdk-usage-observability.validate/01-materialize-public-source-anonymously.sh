set -eu
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
SHA="${PR_HEAD_SHA:-${DISPATCH_SHA}}"
curl -fsSL "https://github.com/${SOURCE_REPO}/archive/${SHA}.tar.gz" -o /tmp/source.tgz
mkdir /tmp/source
tar -xzf /tmp/source.tgz -C /tmp/source --strip-components=1
