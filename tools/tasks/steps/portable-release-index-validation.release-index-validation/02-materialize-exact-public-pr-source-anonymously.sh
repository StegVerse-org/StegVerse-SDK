set -euo pipefail
git config --global --unset-all http.https://github.com/.extraheader || true
git init .
git remote add origin https://github.com/StegVerse-org/StegVerse-SDK.git
env -u GITHUB_TOKEN -u GH_TOKEN git fetch --depth=1 origin "refs/pull/${PR_NUMBER}/merge"
git checkout --detach FETCH_HEAD
