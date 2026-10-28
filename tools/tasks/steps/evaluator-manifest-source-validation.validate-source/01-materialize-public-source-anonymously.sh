set -eu
test -z "${GITHUB_TOKEN:-}"
test -z "${GH_TOKEN:-}"
test -z "${PYPI_API_TOKEN:-}"
curl -fsSL "https://github.com/${SOURCE_REPO}/archive/${SOURCE_SHA}.tar.gz" -o /tmp/source.tgz
mkdir /tmp/source
tar -xzf /tmp/source.tgz -C /tmp/source --strip-components=1
