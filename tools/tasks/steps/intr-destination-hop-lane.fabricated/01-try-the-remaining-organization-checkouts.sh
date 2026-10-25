set +e
mkdir -p _orgs
for spec in \
  "SV-011|_orgs/SV-011" \
  "GCAT-BCAT-Engine|_orgs/GCAT-BCAT-Engine" \
  "StegVerse-002|_orgs/StegVerse-002" \
  "StegGhost|_orgs/StegGhost"
do
  org="${spec%%|*}"
  dest="${spec##*|}"
  git clone --quiet --depth 1 "https://github.com/${org}/.github.git" "$dest"
  if [ ! -f "$dest/org-runtime/interlock-intr.json" ]; then
    rm -rf "$dest"
  fi
done
