set -euo pipefail
# Repair (catalog repairs[]): the folded workflow used a second actions/checkout of the
# release receipt commit into release-ref/. A catalog step cannot run an action, so the same
# read-only checkout is a git fetch of that exact commit into a detached worktree. It runs only
# when the TV/TVC release receipt names a commit.
git fetch --no-tags --depth=1 origin "$RELEASE_COMMIT"
git worktree add --detach release-ref "$RELEASE_COMMIT"
echo "root=release-ref" >> "$GITHUB_OUTPUT"
