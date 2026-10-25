set -euo pipefail
git init .
git remote add origin https://github.com/StegVerse-org/StegVerse-SDK.git
if [ "${GITHUB_EVENT_NAME}" = "pull_request" ]; then
  SOURCE_REF="refs/pull/${PR_NUMBER}/merge"
else
  SOURCE_REF="${GITHUB_SHA}"
fi
env -u GITHUB_TOKEN -u GH_TOKEN git fetch --depth=1 origin "${SOURCE_REF}"
git checkout --detach FETCH_HEAD
test -z "$(git config --local --get-regexp 'extraheader|credential' || true)"
