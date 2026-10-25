set -eu
curl -fsSL "https://github.com/GCAT-BCAT-Engine/Publisher/archive/${SOURCE_SHA}.tar.gz" -o /tmp/pub.tar.gz
mkdir -p /tmp/publisher
tar -xzf /tmp/pub.tar.gz -C /tmp/publisher --strip-components=1
