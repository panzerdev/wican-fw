#!/usr/bin/env bash
TARGET_HOST="192.168.2.252"
FW_PATH="build/wican-fw_obd_$(git rev-parse --short HEAD).bin"
LOCAL_GIT_SHORT="$(git rev-parse --short HEAD)"

# Basic reachability check
if ! ping -c 1 -W 1 "$TARGET_HOST" >/dev/null 2>&1; then
	echo "Host unreachable: $TARGET_HOST" >&2
	exit 1
fi

# Check HTTP responsiveness
if ! curl -s -o /dev/null -w "%{http_code}\n" "http://${TARGET_HOST}/" | grep -q "^[23]"; then
	echo "HTTP check failed on http://${TARGET_HOST}/" >&2
	exit 1
fi

# Compare remote git_version with local short hash using jq; skip if identical
REMOTE_GIT_VERSION=$(curl -s "http://${TARGET_HOST}/check_status" | jq -r '.git_version // empty')
if [ -n "$REMOTE_GIT_VERSION" ] && [ "$REMOTE_GIT_VERSION" = "$LOCAL_GIT_SHORT" ]; then
	echo "Remote git_version matches local ($LOCAL_GIT_SHORT); skipping upload." >&2
	exit 0
fi

docker run --rm -v "$PWD":/project -w /project -u "$UID" -e HOME=/tmp espressif/idf:v5.4.1 idf.py build || {
	echo "Docker build failed" >&2
	exit 1
}

if [ -f "$FW_PATH" ]; then
	curl -v -X POST -F "file=@${FW_PATH}" "http://${TARGET_HOST}/upload/ota.bin"
else
	echo "Firmware not found: $FW_PATH" >&2
	exit 1
fi
